#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int8MultiArray, Int8
import time

STATE_SEARCHING = 0
STATE_MANUAL = 1
STATE_AUTO = 2
STATE_EMERGENCY = 3

class Brain(Node):
    def __init__(self):
        super().__init__('brain')
        self.mode_dir_sub = self.create_subscription(
            Int8MultiArray,
            '/robot/mode_and_direction',
            self.mode_dir_callback,
            10)
        self.lidar_sub = self.create_subscription(
            Int8,
            '/scan',
            self.lidar_callback,
            10)
        self.motor_pub = self.create_publisher(
            Int8MultiArray,
            '/robot/motor_cmd',
            10)
        self.current_state = STATE_SEARCHING
        self.last_mode = 0
        self.last_direction = 0
        self.last_activity_time = time.time()
        self.battery_ok = True
        self.lidar_ok = True

    def mode_dir_callback(self, msg):
        self.last_mode = msg.data[0]
        self.last_direction = msg.data[1]
        self.last_activity_time = time.time()

        if self.current_state == STATE_SEARCHING:
            if self.last_mode == 0:
                self.current_state = STATE_MANUAL
                self.get_logger().info("Switched to MANUAL mode")
            else:
                self.current_state = STATE_AUTO
                self.get_logger().info("Switched to AUTO mode")

        elif self.current_state == STATE_MANUAL:
            if self.last_mode == 1:
                self.current_state = STATE_AUTO
                self.get_logger().info("Switched to AUTO mode (button press)")

        motor_msg = Int8MultiArray()
        motor_msg.data = [self.last_direction]
        self.motor_pub.publish(motor_msg)

    def lidar_callback(self, msg):
        if not self.lidar_ok:
            self.current_state = STATE_EMERGENCY
            self.get_logger().warn("LiDAR DECONNECTED! EMERGENCY STOP!")

    def check_timeout(self):
        if self.current_state == STATE_MANUAL and (time.time() - self.last_activity_time) > 30:
            self.current_state = STATE_AUTO
            self.get_logger().info("Timeout: switched to AUTO mode")
            motor_msg = Int8MultiArray()
            motor_msg.data = [0b0000]
            self.motor_pub.publish(motor_msg)

    def run(self):
        while rclpy.ok():
            self.check_timeout()
            time.sleep(0.1)

def main(args=None):
    rclpy.init(args=args)
    node = Brain()
    node.run()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
