# Interface contracts: ROS 2 topic names, message types, QoS policies, and service definitions.

What the nav team (P004044) needs from the sensor team (P004043).

## Topics

| Topic | Message Type | Min Rate | Source | Failure Response |
|-------|-------------|----------|--------|-----------------|
| `/odom` | nav_msgs/Odometry | 50 Hz | motor_controller node | dropout >1s → Fault |
| `/imu/data` | sensor_msgs/Imu | 100 Hz | imu_driver node | dropout >1s → Fault |
| `/camera/camera/depth/image_rect_raw` | sensor_msgs/Image | 30 Hz | realsense2_camera | dropout >2s → Pause |
| `/camera/camera/color/image_raw` | sensor_msgs/Image | 30 Hz | realsense2_camera | — |

## Running the Sensor Stack

### Motor controller + odometry
```bash
python3 ~/baby-rover/nodes/motor_controller.py
```

### IMU
```bash
python3 ~/baby-rover/nodes/imu_driver.py
```

### RealSense
```bash
ros2 launch realsense2_camera rs_launch.py
```

## Known Issues
- RealSense topic names use double prefix `/camera/camera/` — wrapper default, not a bug
- RealSense firmware 5.12.10 installed, recommended 5.17.0.10 — not critical for operation
- librealsense2 must be built from source on Pi 5 ARM64 — no official binary available