# Baby Rover — Milestones

## Milestone 1 — Environment Setup ✅ COMPLETE
- [x] Flash Ubuntu 24.04 server onto Pi 5 SSD
- [x] Install ROS 2 Jazzy on ThinkPad
- [x] Install ROS 2 Jazzy on Pi 5
- [x] Confirm talker/listener demo working on both machines
- [x] Confirm cross-machine ROS 2 communication over WiFi
- [x] Create baby-rover repo and push to GitHub
- [x] Scaffold folder structure
- [x] Install Claude Code, Cursor extensions
- [x] Write hardware.md and session_log.md

---

## Milestone 2 — Sensors Publishing ← CURRENT
Get all sensors publishing real data to ROS 2 topics on the Pi 5.
Dirty data acceptable — clean plumbing is the goal.

- [ ] IMU (MPU-6050) publishing to /imu/data
  - Install mpu6050 ROS 2 driver on Pi 5
  - Confirm I2C connection: `i2cdetect -y 1`
  - Verify topic: `ros2 topic echo /imu/data`

- [ ] Motors responding to /cmd_vel via keyboard teleop
  - Write motor_controller node (TB6612 + Pi 5 GPIO)
  - Write teleop node (keyboard → /cmd_vel)
  - Test: keyboard input drives motors

- [ ] Encoders publishing to /odom
  - Add encoder reading to motor_controller node
  - Verify topic: `ros2 topic echo /odom`

- [ ] RealSense D415 publishing to /camera/depth
  - Build librealsense2 from source on Pi 5 (ARM64)
  - Install realsense-ros ROS 2 wrapper
  - Verify topic: `ros2 topic echo /camera/depth`

---

## Milestone 3 — State Machine
Design and implement the safety state machine node.

- [ ] Draw state diagram on paper (Teleop/Auto/Pause/Safe-stop/Fault)
- [ ] Define all transitions and trigger conditions
- [ ] Write skeleton state machine node in ROS 2
- [ ] Implement all state transitions
- [ ] Implement fault detection (sensor dropout, comms loss, e-stop)
- [ ] Test all transitions manually
- [ ] Test fault injection (unplug sensor, kill node)

---

## Milestone 4 — EKF Localisation
Fuse IMU + encoders into a clean localisation estimate.

- [ ] Install robot_localization package
- [ ] Configure EKF with IMU + odometry inputs
- [ ] Verify /odometry/filtered topic publishing
- [ ] Tune EKF parameters for baby rover scale

---

## Milestone 5 — Nav2 Integration
Get autonomous waypoint following working end to end.

- [ ] Install Nav2
- [ ] Configure Nav2 for baby rover (footprint, speeds, costmaps)
- [ ] Test waypoint following in simulation (Gazebo)
- [ ] Test waypoint following on real hardware
- [ ] Integrate with state machine (Auto mode)
