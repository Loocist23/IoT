#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from rplidar import RPLidar

class LidarNode(Node):
    def __init__(self):
        super().__init__('lidar_node')
        self.publisher = self.create_publisher(LaserScan, '/scan', 10)
        self.lidar = RPLidar('/dev/ttyUSB0')
        self.timer = self.create_timer(0.1, self.publish_scan)

    def publish_scan(self):
        scan = self.lidar.get_scan()
        msg = LaserScan()
        msg.ranges = scan[0]
        msg.angles = scan[1]
        self.publisher.publish(msg)

    def destroy_node(self):
        self.lidar.stop()
        self.lidar.disconnect()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = LidarNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
