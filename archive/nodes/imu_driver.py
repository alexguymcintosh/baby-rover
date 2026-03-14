#!/usr/bin/env python3
"""
IMU driver node — reads MPU-6050, publishes to /imu/data
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from mpu6050 import mpu6050
import math

IMU_ADDRESS = 0x68
PUBLISH_RATE = 100  # Hz


class ImuDriver(Node):

    def __init__(self):
        super().__init__('imu_driver')
        self.get_logger().info('IMU driver starting...')

        self.sensor = mpu6050(IMU_ADDRESS)
        self.pub = self.create_publisher(Imu, '/imu/data', 10)
        self.create_timer(1.0 / PUBLISH_RATE, self.publish_imu)

        self.get_logger().info('IMU driver ready.')

    def publish_imu(self):
        accel = self.sensor.get_accel_data()
        gyro = self.sensor.get_gyro_data()

        msg = Imu()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'imu_link'

        msg.linear_acceleration.x = accel['x']
        msg.linear_acceleration.y = accel['y']
        msg.linear_acceleration.z = accel['z']

        msg.angular_velocity.x = math.radians(gyro['x'])
        msg.angular_velocity.y = math.radians(gyro['y'])
        msg.angular_velocity.z = math.radians(gyro['z'])

        self.pub.publish(msg)

    def destroy_node(self):
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = ImuDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
