#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int8MultiArray
import RPi.GPIO as GPIO
import time

MOTOR_PINS = {
    'IN1': 17,
    'IN2': 18,
    'IN3': 22,
    'IN4': 23
}

DIRECTION_MAP = {
    0b0000: (0, 0, 0, 0),
    0b0001: (1, 0, 1, 0),
    0b0010: (0, 1, 0, 1),
    0b0100: (0, 1, 1, 0),
    0b0110: (1, 0, 0, 1)
}

class MotorController(Node):
    def __init__(self):
        super().__init__('motor_controller')
        self.subscription = self.create_subscription(
            Int8MultiArray,
            '/robot/motor_cmd',
            self.motor_callback,
            10)
        GPIO.setmode(GPIO.BCM)
        for pin in MOTOR_PINS.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)

    def motor_callback(self, msg):
        direction = msg.data[0]
        signals = DIRECTION_MAP.get(direction, (0, 0, 0, 0))
        self.get_logger().info(f"Setting motors to direction: {direction} (signals: {signals})")
        GPIO.output(MOTOR_PINS['IN1'], signals[0])
        GPIO.output(MOTOR_PINS['IN2'], signals[1])
        GPIO.output(MOTOR_PINS['IN3'], signals[2])
        GPIO.output(MOTOR_PINS['IN4'], signals[3])

    def destroy_node(self):
        GPIO.cleanup()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = MotorController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
