#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
import math

class SlipTester(Node):
    def __init__(self):
        super().__init__('slip_test_rig')
        
        # We publish to the topics your monitor is listening to
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.gz_pub = self.create_publisher(Odometry, '/gz_odom', 10)
        
        # Publish at 10Hz (100ms)
        self.timer = self.create_timer(1.0, self.publish_simulated_slip)
        self.time_elapsed = 0.0

    def publish_simulated_slip(self):
        self.time_elapsed += 1.0
        
        # 1. Gazebo Ground Truth (Moves steadily forward along X)
        gz_msg = Odometry()
        gz_msg.header.stamp = self.get_clock().now().to_msg()
        gz_msg.header.frame_id = 'odom'
        gz_msg.pose.pose.position.x = 0.0
        gz_msg.pose.pose.position.y = 0.0
        
        # 2. Wheel Odometry (Simulating slip using a sine wave error)
        odom_msg = Odometry()
        odom_msg.header.stamp = self.get_clock().now().to_msg()
        odom_msg.header.frame_id = 'odom'
        
        # The error will oscillate up to 0.6 meters and back down
        simulated_error = 0.6 * math.sin(self.time_elapsed) 
        odom_msg.pose.pose.position.x = simulated_error
        odom_msg.pose.pose.position.y = 0.0
        
        self.gz_pub.publish(gz_msg)
        self.odom_pub.publish(odom_msg)

def main(args=None):
    rclpy.init(args=args)
    node = SlipTester()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()