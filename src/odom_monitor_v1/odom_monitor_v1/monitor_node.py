#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
import diagnostic_updater
from diagnostic_msgs.msg import DiagnosticStatus 

class OdomMonitor(Node):
    def __init__(self):
        super().__init__('odom_status_updater')

        self.odom_ = self.create_subscription( Odometry, "/odom", self.odom_callback, 10)
        self.gz_odom = self.create_subscription( Odometry, '/gz_odom', self.gz_odom_callback, 10)

        self.latest_odom = None
        self.latest_gz = None
        self.drift = 0.0

        self.timer_ = self.create_timer(1.0, self.cal_drift)

        self.updater_ = diagnostic_updater.Updater(self)
        self.updater_.setHardwareID("odom_monitor")
        self.updater_.add("Odometry Drift", self.check_diagnostics)

    def odom_callback(self, msg: Odometry):
        self.latest_odom = msg

    def gz_odom_callback(self,msg: Odometry):
        self.latest_gz = msg

    def cal_drift(self):
        self.get_logger().info("Timer woke up...") 
        
        if self.latest_gz is None or self.latest_odom is None:
            self.get_logger().warn("Still waiting for one or both topics...") 
            return 
            
        self.get_logger().info("Messages received! Calculating math...")
        x_odom, y_odom = self.latest_odom.pose.pose.position.x, self.latest_odom.pose.pose.position.y
        x_gz, y_gz = self.latest_gz.pose.pose.position.x, self.latest_gz.pose.pose.position.y

        self.drift = math.sqrt((x_gz - x_odom)**2 + (y_gz - y_odom)**2)

        # self.get_logger().info(f"The currwent drift is : {self.drift}")

        self.updater_.force_update()

    def check_diagnostics(self, stat):
        if self.drift > 0.2:
            stat.summary(DiagnosticStatus.ERROR, "High Odometry Drift Detected!")
        else:
            stat.summary(DiagnosticStatus.OK, "Odometry Normal")

        stat.add("Drift Distance(m) ", str(self.drift))

        return stat

def main(args =None):
    rclpy.init(args = args)
    OM = OdomMonitor()
    rclpy.spin(OM)
    rclpy.shutdown()

if __name__ == "__main__":
    main()