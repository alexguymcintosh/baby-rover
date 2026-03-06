#!/usr/bin/env python3
"""
Motor controller node — open loop.
Subscribes to /cmd_vel, drives TB6612 via GPIO.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import lgpio
from nav_msgs.msg import Odometry
from std_msgs.msg import Header
import math
import gpiod
import threading
import datetime


# --- Pin definitions (BCM numbering) ---
AIN1 = 27  # Motor A (Right) direction
AIN2 = 17  # Motor A (Right) direction
PWMA = 13  # Motor A (Right) speed

BIN1 = 26  # Motor B (Left) direction
BIN2 = 19  # Motor B (Left) direction
PWMB = 12  # Motor B (Left) speed

STBY = None  # Pulled HIGH via resistor — no GPIO control needed

# --- Robot physical parameters ---
WHEEL_BASE = 0.34       # metres — distance between wheels, measure and update
MAX_SPEED = 100         # PWM duty cycle max (0-100)

MOTOR_PINS = [AIN1, AIN2, PWMA, BIN1, BIN2, PWMB]

#PID controller tunable parameters
pid_kp = 0.01
pid_ki = 0.005
pid_kd = 0
windup_limit = 50




class MotorController(Node):

    def __init__(self):
    
        super().__init__('motor_controller')
        self.get_logger().info('Motor controller starting...')

        # Init GPIO
        self.chip = lgpio.gpiochip_open(4)
        for pin in MOTOR_PINS:
            lgpio.gpio_claim_output(self.chip, pin, 0)

        # PWM setup — 1000 Hz
        lgpio.tx_pwm(self.chip, PWMA, 1000, 0)
        lgpio.tx_pwm(self.chip, PWMB, 1000, 0)

        # Encoder setup via gpiod kernel interrupts
        self.enc_a_count = 0
        self.enc_b_count = 0
        self._enc_lock = threading.Lock()

        self.gpio_chip = gpiod.Chip('/dev/gpiochip4')

        self.enc_a_request = self.gpio_chip.request_lines(
            consumer='enc_a',
            config={21: gpiod.LineSettings(edge_detection=gpiod.line.Edge.RISING, debounce_period=datetime.timedelta(microseconds=0.5))}
        )
        self.enc_b_request = self.gpio_chip.request_lines(
            consumer='enc_b',
            config={24: gpiod.LineSettings(edge_detection=gpiod.line.Edge.RISING, debounce_period=datetime.timedelta(microseconds=0.5))}
        )

        self.enc_a_thread = threading.Thread(target=self._watch_enc_a, daemon=True)
        self.enc_b_thread = threading.Thread(target=self._watch_enc_b, daemon=True)
        self.enc_a_thread.start()
        self.enc_b_thread.start()

        # ROS subscriber
        self.sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )
        

        self.get_logger().info('Motor controller ready.')

        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.last_enc_a = 0
        self.last_enc_b = 0
        self.create_timer(0.02, self.publish_odom)  # 50Hz

        # PID controller
        self.pid_integral = 0.0
        self.pid_prev_error = 0.0
        self.correction = 0.0
        self.linear = 0.0
        self.angular = 0.0
        self.debug_counter = 0

        self.active = False

    def cmd_vel_callback(self, msg):
        self.get_logger().info(f'cmd_vel: linear={msg.linear.x:.2f} angular={msg.angular.z:.2f}')
        self.get_logger().info(f'enc_a={self.enc_a_count} enc_b={self.enc_b_count}')
        self.linear = msg.linear.x
        self.angular = msg.angular.z
        self.active = True

    def drive_motor_a(self, speed):
        duty = min(abs(speed) * MAX_SPEED, MAX_SPEED)
        if speed > 0:
            lgpio.gpio_write(self.chip, AIN1, 1) # was 0
            lgpio.gpio_write(self.chip, AIN2, 0) # was 1
        elif speed < 0:
            lgpio.gpio_write(self.chip, AIN1, 0) # was 1
            lgpio.gpio_write(self.chip, AIN2, 1) # was 0
        else:
            lgpio.gpio_write(self.chip, AIN1, 0)
            lgpio.gpio_write(self.chip, AIN2, 0)
        lgpio.tx_pwm(self.chip, PWMA, 1000, duty)

    def drive_motor_b(self, speed):
        duty = min(abs(speed) * MAX_SPEED, MAX_SPEED)
        if speed > 0:
            lgpio.gpio_write(self.chip, BIN1, 0)
            lgpio.gpio_write(self.chip, BIN2, 1)
        elif speed < 0:
            lgpio.gpio_write(self.chip, BIN1, 1)
            lgpio.gpio_write(self.chip, BIN2, 0)
        else:
            lgpio.gpio_write(self.chip, BIN1, 0)
            lgpio.gpio_write(self.chip, BIN2, 0)
        lgpio.tx_pwm(self.chip, PWMB, 1000, duty)

    def stop_motors(self):
        lgpio.gpio_write(self.chip, AIN1, 0)
        lgpio.gpio_write(self.chip, AIN2, 0)
        lgpio.gpio_write(self.chip, BIN1, 0)
        lgpio.gpio_write(self.chip, BIN2, 0)
        lgpio.tx_pwm(self.chip, PWMA, 1000, 0)
        lgpio.tx_pwm(self.chip, PWMB, 1000, 0)

    def destroy_node(self):
        self.stop_motors()
        lgpio.gpiochip_close(self.chip)
        self.enc_a_request.release()
        self.enc_b_request.release()
        self.gpio_chip.close()
        super().destroy_node()


    def publish_odom(self):
        PULSES_PER_REV = 1050
        WHEEL_CIRCUMFERENCE = 0.1382

        delta_a = self.enc_a_count - self.last_enc_a
        delta_b = self.enc_b_count - self.last_enc_b
        self.last_enc_a = self.enc_a_count
        self.last_enc_b = self.enc_b_count

        dist_a = (delta_a / PULSES_PER_REV) * WHEEL_CIRCUMFERENCE
        dist_b = (delta_b / PULSES_PER_REV) * WHEEL_CIRCUMFERENCE

        error = delta_a - delta_b
        self.pid_integral += error * 0.02
        self.pid_integral = max(-windup_limit, min(windup_limit, self.pid_integral))
        derivative = (error - self.pid_prev_error) / 0.02
        self.correction = pid_kp * error + pid_ki * self.pid_integral + pid_kd * derivative
        self.debug_counter += 1
        if self.debug_counter % 25 == 0:
            self.get_logger().info(f'correction={self.correction:.4f} integral={self.pid_integral:.4f} error={error}')
        self.pid_prev_error = error

        right = self.linear - (self.angular * WHEEL_BASE / 2.0) - self.correction
        left = self.linear + (self.angular * WHEEL_BASE / 2.0) + self.correction

        if self.active and self.linear != 0.0:
            self.drive_motor_a(right)
            self.drive_motor_b(left)
        else:
            self.stop_motors()

        dist = (dist_a + dist_b) / 2.0
        dtheta = (dist_a - dist_b) / WHEEL_BASE
        self.x += dist * math.cos(self.theta)
        self.y += dist * math.sin(self.theta)
        self.theta += dtheta

        msg = Odometry()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'odom'
        msg.child_frame_id = 'base_link'
        msg.pose.pose.position.x = self.x
        msg.pose.pose.position.y = self.y
        msg.twist.twist.linear.x = dist / 0.02
        msg.twist.twist.angular.z = dtheta / 0.02
        self.odom_pub.publish(msg)
    
    def _watch_enc_a(self):
        while rclpy.ok():
            if self.enc_a_request.wait_edge_events(datetime.timedelta(seconds=1)):
                self.enc_a_request.read_edge_events()
                with self._enc_lock:
                    self.enc_a_count += 1

    def _watch_enc_b(self):
        while rclpy.ok():
            if self.enc_b_request.wait_edge_events(datetime.timedelta(seconds=1)):
                self.enc_b_request.read_edge_events()
                with self._enc_lock:
                    self.enc_b_count += 1


def main(args=None):
    rclpy.init(args=args)
    node = MotorController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()