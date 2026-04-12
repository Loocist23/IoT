#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int8MultiArray
import serial

class UARTReader(Node):
    def __init__(self):
        super().__init__('uart_reader')
        self.publisher = self.create_publisher(Int8MultiArray, '/robot/mode_and_direction', 10)
        self.serial_port = serial.Serial('/dev/ttyS0', baudrate=115200, timeout=1)

    def read_uart(self):
        while rclpy.ok():
            if self.serial_port.in_waiting > 0:
                data = self.serial_port.read(1)
                if data:
                    byte = data[0]
                    mode = (byte >> 4) & 0x01
                    direction = byte & 0x0F
                    msg = Int8MultiArray()
                    msg.data = [mode, direction]
                    self.publisher.publish(msg)
                    self.get_logger().info(f"Received: Mode={mode}, Direction={direction}")

def main(args=None):
    rclpy.init(args=args)
    node = UARTReader()
    try:
        node.read_uart()
    except KeyboardInterrupt:
        pass
    finally:
        node.serial_port.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
