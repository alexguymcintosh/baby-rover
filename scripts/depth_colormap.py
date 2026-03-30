#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np


class DepthColormap(Node):
    MAX_DEPTH_MM = 3000

    def __init__(self):
        super().__init__('depth_colormap')
        self.bridge = CvBridge()
        self.pub = self.create_publisher(Image, '/camera/depth/colormap', 10)
        self.sub = self.create_subscription(
            Image,
            '/camera/camera/depth/image_rect_raw',
            self.callback,
            10,
        )

    def callback(self, msg: Image):
        depth = self.bridge.imgmsg_to_cv2(msg, desired_encoding='16UC1')
        clipped = np.clip(depth, 0, self.MAX_DEPTH_MM)
        normalised = (clipped / self.MAX_DEPTH_MM * 255).astype(np.uint8)
        colormap = cv2.applyColorMap(normalised, cv2.COLORMAP_JET)
        out = self.bridge.cv2_to_imgmsg(colormap, encoding='bgr8')
        out.header = msg.header
        self.pub.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = DepthColormap()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
