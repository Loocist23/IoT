from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='uart_reader',
            executable='uart_reader',
            name='uart_reader'
        ),
        Node(
            package='motor_controller',
            executable='motor_controller',
            name='motor_controller'
        ),
        Node(
            package='brain',
            executable='brain',
            name='brain'
        ),
        Node(
            package='rplidar_ros',
            executable='rplidar_node',
            name='rplidar_node',
            parameters=[{'serial_port': '/dev/ttyUSB0'}]
        )
    ])
