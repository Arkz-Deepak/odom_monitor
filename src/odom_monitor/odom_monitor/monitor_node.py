#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
import diagnostic_updater
from diagnostic_msgs.msg import DiagnosticStatus
from visualization_msgs.msg import Marker, MarkerArray 
from geometry_msgs.msg import Point
import csv
from geometry_msgs.msg import Twist

class OdomMonitor(Node):
    def __init__(self):
        super().__init__('odom_status_updater')

        self.declare_parameter("odom_topic", '/odom')
        self.declare_parameter("gz_topic", '/gz_odom')
        self.declare_parameter("drift_threshold", 0.2)

        self.odom_topic = self.get_parameter("odom_topic").value
        self.gz_topic = self.get_parameter("gz_topic").value
        self.drift_threshold = self.get_parameter("drift_threshold").value

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.odom_ = self.create_subscription( Odometry, self.odom_topic, self.odom_callback, 10)
        self.gz_odom = self.create_subscription( Odometry, self.gz_topic, self.gz_odom_callback, 10)
        self.vis_pub_ = self.create_publisher(MarkerArray, "/drift_visuals", 10)

        self.latest_odom = None
        self.latest_gz = None
        self.drift = 0.0
        self.max_drift = 0.0

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

        if self.drift > self.drift_threshold:
            self.get_logger().error("SAFETY INTERLOCK TRIGGERED! BRAKES APPLIED!")
            
            # Create a zero-velocity message and publish it
            stop_msg = Twist()
            self.cmd_pub.publish(stop_msg)
            self.drift = 0.0

        self.publish_marker(x_odom, y_odom, x_gz, y_gz)

        if self.drift > self.max_drift: 
            self.max_drift = self.drift

        self.get_logger().info(f"The current drift is : {self.drift}")

        # Log data to the CSV
        with open('drift_benchmark.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            # Write: ROS Time, Odom X, Gz X, Current Drift, Max Drift
            writer.writerow([self.get_clock().now().nanoseconds, x_odom, x_gz, self.drift, self.max_drift])

        self.updater_.force_update()

    def check_diagnostics(self, stat):
        if self.drift > self.drift_threshold:
            stat.summary(DiagnosticStatus.ERROR, "High Odometry Drift Detected!")
        else:
            stat.summary(DiagnosticStatus.OK, "Odometry Normal")

        stat.add("Drift Distance(m) ", str(self.drift))

        stat.add("Max Drift(m): ", str(self.max_drift))

        return stat

    def publish_marker(self, x_odom, y_odom, x_gz, y_gz):
        marker = Marker()
        marker.header.frame_id = 'odom'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "drift_line"
        marker.id = 0
        marker.type = Marker.SPHERE_LIST  # Bypasses the line shader bug
        marker.action = Marker.ADD
        
        # ... (keep your pose orientation exactly as it is) ...
        
        # Give the spheres a 10cm diameter in all 3 dimensions
        marker.scale.x = 0.1 
        marker.scale.y = 0.1
        marker.scale.z = 0.1
        
        # ... (keep your colors and points exactly the same) ...
        
        # 1. Fully define the base pose (RViz demands this)
        marker.pose.position.x = 0.0
        marker.pose.position.y = 0.0
        marker.pose.position.z = 0.0
        marker.pose.orientation.x = 0.0
        marker.pose.orientation.y = 0.0
        marker.pose.orientation.z = 0.0
        marker.pose.orientation.w = 1.0 
        
        # 2. Make it thick and explicitly set float colors
        marker.scale.x = 0.1 
        marker.color.r = 1.0
        marker.color.g = 0.0
        marker.color.b = 0.0
        marker.color.a = 1.0 

        # 3. Force the coordinates into floats and lift it 5cm
        point_odom = Point(x=float(x_odom), y=float(y_odom), z=0.05)
        point_gz = Point(x=float(x_gz), y=float(y_gz), z=0.05)

        marker.points = [point_odom, point_gz]

        marker_array = MarkerArray()
        marker_array.markers.append(marker)

        self.vis_pub_.publish(marker_array)


def main(args =None):
    rclpy.init(args = args)
    OM = OdomMonitor()
    rclpy.spin(OM)
    rclpy.shutdown()

if __name__ == "__main__":
    main()