// motor_controller.cpp
// TB6612 differential drive — ROS2 Jazzy — Raspberry Pi

#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <lgpio.h>
#include <gpiod.h>
#include <thread>
#include <mutex>
#include <atomic>
#include <cmath>
#include <algorithm>
#include <chrono>

// ─── PIN DEFINITIONS (BCM) ────────────────────────────────────────────────────
constexpr int AIN1 = 27;
constexpr int AIN2 = 17;
constexpr int PWMA = 13;

constexpr int BIN1 = 26;
constexpr int BIN2 = 19;
constexpr int PWMB = 12;

// ─── ROBOT PARAMETERS ─────────────────────────────────────────────────────────
constexpr double WHEEL_BASE          = 0.34;
constexpr double MAX_SPEED           = 100.0;
constexpr int    PULSES_PER_REV      = 1050;
constexpr double WHEEL_CIRCUMFERENCE = 0.1382;
constexpr double DT                  = 0.02;   // 50 Hz timer period (seconds)

// ─── PID TUNING ───────────────────────────────────────────────────────────────
// TODO: set these once you have written and tested the PID
constexpr double PID_KP       = 0.001;
constexpr double PID_KI       = 0.0;
constexpr double PID_KD       = 0.0;
constexpr double WINDUP_LIMIT = 50.0;
constexpr double MOTOR_B_TRIM = 0.971;


// ─── PID STATE ────────────────────────────────────────────────────────────────
// These three variables are all the memory the PID needs between timer ticks.
// You own these — do not touch them anywhere except inside computePID().
struct PidState 
{
    double integral   = 0.0;
    double prev_error = 0.0;
};

PidState pid_state_a_;
PidState pid_state_b_;

double computePID(double error, PidState& state)
{

double p = PID_KP * error;
state.integral += PID_KI * error * DT;
state.integral = std::clamp(state.integral, -WINDUP_LIMIT, WINDUP_LIMIT);
double d = PID_KD * (error - state.prev_error) / DT;
state.prev_error = error;
return p + state.integral + d;

}



// ─── MOTOR CONTROLLER NODE ────────────────────────────────────────────────────
class MotorController : public rclcpp::Node
{
public:
    MotorController() : Node("motor_controller")
    {
        RCLCPP_INFO(get_logger(), "Motor controller starting...");

        initGPIO();
        initEncoders();

        cmd_vel_sub_ = create_subscription<geometry_msgs::msg::Twist>(
            "/cmd_vel", 10,
            [this](const geometry_msgs::msg::Twist::SharedPtr msg) {
                cmdVelCallback(msg);
            });

        odom_pub_ = create_publisher<nav_msgs::msg::Odometry>("/odom", 10);

        timer_ = create_wall_timer(
            std::chrono::milliseconds(20),
            [this]() { timerCallback(); });

        RCLCPP_INFO(get_logger(), "Motor controller ready.");
    }

    ~MotorController()
    {
        stopMotors();
        lgGpiochipClose(chip_);
        gpiod_line_release(enc_a_line_);
        gpiod_line_release(enc_b_line_);
        gpiod_chip_close(gpiod_chip_);
    }

private:

    // ── GPIO / HARDWARE ───────────────────────────────────────────────────────
    int chip_;

    void initGPIO()
    {
        chip_ = lgGpiochipOpen(4);
        for (int pin : {AIN1, AIN2, PWMA, BIN1, BIN2, PWMB})
            lgGpioClaimOutput(chip_, 0, pin, 0);
        lgTxPwm(chip_, PWMA, 1000, 0, 0, 0);
        lgTxPwm(chip_, PWMB, 1000, 0, 0, 0);
    }

    void driveMotorA(double speed)
    {
        double duty = std::min(std::abs(speed) * MAX_SPEED, MAX_SPEED);
        lgGpioWrite(chip_, AIN1, speed > 0 ? 1 : 0);
        lgGpioWrite(chip_, AIN2, speed > 0 ? 0 : 1);
        if (speed == 0.0) { lgGpioWrite(chip_, AIN1, 0); lgGpioWrite(chip_, AIN2, 0); }
        lgTxPwm(chip_, PWMA, 1000, duty, 0, 0);       
    }

    void driveMotorB(double speed)
    {
        double duty = std::min(std::abs(speed) * MAX_SPEED, MAX_SPEED);
        lgGpioWrite(chip_, BIN1, speed > 0 ? 0 : 1);
        lgGpioWrite(chip_, BIN2, speed > 0 ? 1 : 0);
        if (speed == 0.0) { lgGpioWrite(chip_, BIN1, 0); lgGpioWrite(chip_, BIN2, 0); }
        lgTxPwm(chip_, PWMB, 1000, duty, 0, 0);
    }

    void stopMotors()
    {
        lgGpioWrite(chip_, AIN1, 0); lgGpioWrite(chip_, AIN2, 0);
        lgGpioWrite(chip_, BIN1, 0); lgGpioWrite(chip_, BIN2, 0);
        lgTxPwm(chip_, PWMA, 1000, 0, 0, 0);
        lgTxPwm(chip_, PWMB, 1000, 0, 0, 0);
    }

    // ── ENCODERS ──────────────────────────────────────────────────────────────
    std::atomic<int> enc_a_count_{0};
    std::atomic<int> enc_b_count_{0};
    std::mutex       enc_lock_;

    struct gpiod_chip* gpiod_chip_;
    struct gpiod_line* enc_a_line_;
    struct gpiod_line* enc_b_line_;
    std::thread enc_a_thread_;
    std::thread enc_b_thread_;

    void initEncoders()
    {
        gpiod_chip_ = gpiod_chip_open("/dev/gpiochip4");
        enc_a_line_ = gpiod_chip_get_line(gpiod_chip_, 21);
        enc_b_line_ = gpiod_chip_get_line(gpiod_chip_, 24);
        gpiod_line_request_rising_edge_events(enc_a_line_, "enc_a");
        gpiod_line_request_rising_edge_events(enc_b_line_, "enc_b");
        enc_a_thread_ = std::thread([this]() { watchEncoder(enc_a_line_, enc_a_count_); });
        enc_b_thread_ = std::thread([this]() { watchEncoder(enc_b_line_, enc_b_count_); });
        enc_a_thread_.detach();
        enc_b_thread_.detach();
    }

    void watchEncoder(struct gpiod_line* line, std::atomic<int>& count)
    {
        struct gpiod_line_event event;
        struct timespec timeout = {1, 0};
        while (rclcpp::ok()) {
            int ret = gpiod_line_event_wait(line, &timeout);
            if (ret == 1) {
                gpiod_line_event_read(line, &event);
                count++;
                

            }
        }
    }

    // ── CMD_VEL ───────────────────────────────────────────────────────────────
    double linear_  = 0.0;
    double angular_ = 0.0;
    bool   active_  = false;

    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_sub_;

    void cmdVelCallback(const geometry_msgs::msg::Twist::SharedPtr msg)
    {
        linear_  = msg->linear.x;
        //angular_ = msg->angular.z;
        angular_ = 0.0;
        active_  = true;
    }

    // ── ODOMETRY ──────────────────────────────────────────────────────────────
    double x_     = 0.0;
    double y_     = 0.0;
    double theta_ = 0.0;
    int    last_enc_a_ = 0;
    int    last_enc_b_ = 0;
    int    debug_counter_ = 0;

    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;

    // ── PID STATE INSTANCE ────────────────────────────────────────────────────
    PidState pid_state_;

    // ── MAIN TIMER CALLBACK ───────────────────────────────────────────────────
    rclcpp::TimerBase::SharedPtr timer_;

    void timerCallback()
    {
        int current_a = enc_a_count_.load();
        int current_b = enc_b_count_.load();
        int delta_a = current_a - last_enc_a_;
        int delta_b = current_b - last_enc_b_;
        last_enc_a_ = current_a;
        last_enc_b_ = current_b;

        // ── PID ───────────────────────────────────────────────────────────────
        double target_a = linear_ - (angular_ * WHEEL_BASE / 2.0);
        double target_b = (linear_ + (angular_ * WHEEL_BASE / 2.0)) * MOTOR_B_TRIM;
        double target_counts_a = target_a * (PULSES_PER_REV * DT / WHEEL_CIRCUMFERENCE);
        double target_counts_b = target_b * (PULSES_PER_REV * DT / WHEEL_CIRCUMFERENCE);
        double error_a = target_counts_a - delta_a;
        double error_b = target_counts_b - delta_b;
        double pwm_a = target_a + computePID(error_a, pid_state_a_);
        double pwm_b = target_b + computePID(error_b, pid_state_b_);

        // ── MOTOR DRIVE ───────────────────────────────────────────────────────
        if (active_ && linear_ != 0.0) {
            driveMotorA(pwm_a);
            driveMotorB(pwm_b);
        } else {
            stopMotors();
        }

        // ── ODOMETRY ──────────────────────────────────────────────────────────
        double dist_a = (static_cast<double>(delta_a) / PULSES_PER_REV) * WHEEL_CIRCUMFERENCE;
        double dist_b = (static_cast<double>(delta_b) / PULSES_PER_REV) * WHEEL_CIRCUMFERENCE;
        double dist   = (dist_a + dist_b) / 2.0;
        double dtheta = (dist_a - dist_b) / WHEEL_BASE;

        x_     += dist * std::cos(theta_);
        y_     += dist * std::sin(theta_);
        theta_ += dtheta;

        auto odom        = nav_msgs::msg::Odometry();
        odom.header.stamp    = get_clock()->now();
        odom.header.frame_id = "odom";
        odom.child_frame_id  = "base_link";
        odom.pose.pose.position.x  = x_;
        odom.pose.pose.position.y  = y_;
        odom.twist.twist.linear.x  = dist   / DT;
        odom.twist.twist.angular.z = dtheta / DT;
        odom_pub_->publish(odom);

        if (++debug_counter_ % 25 == 0)
            RCLCPP_INFO(get_logger(), "err_a=%.4f err_b=%.4f pwm_a=%.4f pwm_b=%.4f",
                        error_a, error_b, pwm_a, pwm_b);
        
    }
};


// ─── MAIN ─────────────────────────────────────────────────────────────────────
int main(int argc, char** argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<MotorController>());
    rclcpp::shutdown();
    return 0;
}