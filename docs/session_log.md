# Session Log

## 2026-02-23-20-00 - Alex

### What I worked on
- Installed ROS 2 Jazzy on ThinkPad (Ubuntu 24.04)
- Flashed Ubuntu 24.04 server onto Crucial BX500 SSD for Pi 5
- SSH confirmed working ThinkPad → Pi 5
- Installed ROS 2 Jazzy on Pi 5
- Confirmed talker/listener demo working on both machines
- Confirmed cross-machine ROS 2 communication working over WiFi via DDS
- Created baby-rover repo structure and pushed to GitHub
- Installed Claude Code, ROS, GitLens, Python extensions in Cursor

### What broke
- librealsense2-dkms failed on kernel 6.17 on ThinkPad — removed for now, not needed yet
- Network dropped mid apt upgrade — fixed with --fix-missing flag
- SSH host key conflict after reflash — fixed with ssh-keygen -R

### What's next
- Get IMU publishing to /imu/data on Pi 5
- Get motors responding to /cmd_vel via keyboard teleop
- Get encoders publishing to /odom

## 2026-02-24-09-35 - Alex 

### What was done
- Confirmed wiring from memory and documented in hardware.md
- Identified 10kΩ pulldowns on motor control pins as suspected curve cause
- Deferred motor curve troubleshooting to dedicated session

### Decisions made
- Motor A = Right, Motor B = Left
- Pulldowns to be removed before PID tuning begins

### Blockers / open issues
- hardware.md wiring not yet committed to group repo

### Next session
- Write motor_controller node

## 2026-02-24-10-20 - Alex 

### Updated README

## 2026-02-24-15-14 - Alex

### What was done
- Confirmed Cursor SSH workflow — editing files directly on Pi
- Installed lgpio on Pi 5
- Discovered Pi 5 uses gpiochip4 not gpiochip0
- Wrote motor_controller node — open loop, subscribes to /cmd_vel
- Confirmed ROS 2 pub/sub pipeline working
- Motors responding to /cmd_vel — both wheels spinning correct direction
- Measured wheel diameter = 44mm
- Encoder resolution: 7PPR × 150 gear ratio = 1050 PPR, 1 pulse = 0.1316mm
- Encoder callbacks broken in lgpio 0.2.0.0 on Pi 5 — switched to 100Hz polling via ROS 2 timer
- /odom publishing and incrementing correctly with wheel movement


### Decisions made
- Running nodes directly with Python for now — no colcon package yet
- nodes/ directory on Pi for scripts
- No sudo required — babyrover already in gpio, i2c, spi groups
- Encoder polling at 100Hz instead of interrupt-driven callbacks — lgpio bug, revisit on university rover

### Deferred
- 10kΩ pulldown troubleshooting — suspected curve cause, dedicated session
- colcon workspace setup — after all nodes working
- /odom accuracy tuning — y drift and angular.z oscillation confirm wheel mismatch, do not tune until pulldowns resolved

### Next session
- IMU node — MPU-6050 publishing to /imu/data

## 2026-02-24-17-00 - Alex

### What was done 
- Wired MPU-6050 via I2C — GPIO 2 (SDA), GPIO 3 (SCL)
- Confirmed i2cdetect shows 0x68
- Wrote imu_driver node — publishes to /imu/data at 100Hz
- Installed i2c-tools, mpu6050-raspberrypi, python3-smbus on Pi
- Created updated dependencies.md
- Updated hardware.md with motor/encoder specs for measuring movement
- Updated hardare.md with IMU wiring 

## 2026-02-24-17-43 - Alex 
- Updated disisions.md - ADR-001-(encoder reading polling vs interrupt-driven callbacks)
- README.md is compete and up to date

## 2026-02-24-19-25 - Alex

### What was done
- Built librealsense2 2.57.6 from source on Pi 5 ARM64
- Installed ros-jazzy-realsense2-camera ROS 2 wrapper
- RealSense D415 confirmed publishing on Pi 5 via USB 3.2
- Confirmed all 4 topics publishing simultaneously:
  - /odom ✅
  - /imu/data ✅
  - /camera/camera/depth/image_rect_raw ✅
  - /camera/camera/color/image_raw ✅
- Confirmed depth stream publishing at 29Hz via `ros2 topic hz`
- Milestone 2 complete
- Updated README
- Added milestones.md

### Decisions made
- RealSense uses realsense2_camera wrapper directly — no custom node needed
- Topic names have /camera/camera/ double prefix — wrapper default, documented in interface contract

### Deferred
- RealSense firmware update to 5.17.0.10 — not critical
- State machine — Milestone 3

### Milestone 2 status
- /cmd_vel → motors ✅
- /odom publishing ✅
- /imu/data publishing ✅
- /camera/depth publishing ✅

## 2026-03-03-21-50 - Alex

### what was done 
- drove the motro with teleop-twist-keyboard
- calculated 5% drift to the right
- measured wheel to wheel weidth 340mm from centre of track mark (tape measure)
- updated wheel base motor_contorller.py
- tested 100hz poll rate was too slow, increased to 1000hz could count slow hand turning but failed at practical speed
- installed gpiod-2.4.0 with  pip3 install gpiod --break-system-packages
- installed pulseview on ThinkPad -> for DIGISHUO 24Hz - 8 channel logic analyzer -> run with pulseview
- sudo apt install sigrok-firmware-fx2lafw for logic analyzer 
- Abandened polling - not sufficent for high frequencey encoder pulses
- implemented kernal interupts method - enc_b is accuracte, enc_a is 2.5 times larger consitently
- encoder_dianostic.md was created refer to for test procedure and truth 
- problem solved wires were carrying EMF spike from motor A, problem fixed with wire separation 


### observations
- wheel contact dirt mark curve around the wheel -> wheel needs alignment

### known problem 
- motor A produces EMF spikes - solution capacitor accorss motor power - and + and add a low pass filter. 
- motor B did not produce EMF 

### short term solution seperated the wires (worked)

## 2026-03-05-22-50 Alex

### what was done:
- implented added PID
- open loop 5% variance 
- closed loop -> P = 0.01 | I = 0.005 | Variance = 0.5% after 10 seconds - (linear x = 0.3)

## 2026-03-06-20-20 Alex

### Problem
Stalling noise when linear x = 0.0 on node startup.

### Explanation
`publish_odom` runs at 50Hz from the moment the node starts. Before any `cmd_vel` arrives `self.linear = 0.0` so it commands zero speed 50 times per second. The TB6612 in active brake mode holds both direction pins LOW with PWM at 0%, shorting the motor terminals together through the driver. The 1000Hz PWM carrier is still running at 0% duty cycle — motor coils are energised and de-energised at 1000Hz with zero net torque. That's the stalling noise.

### Solution
- Added `self.active = False` to `__init__`
- Added `self.active = True` to `cmd_vel_callback`
- Wrapped motor drive calls in `publish_odom` with:
```python
  if self.active and self.linear != 0.0:
      self.drive_motor_a(right)
      self.drive_motor_b(left)
  else:
      self.stop_motors()
```
Motors are now silent until the first `cmd_vel` arrives.