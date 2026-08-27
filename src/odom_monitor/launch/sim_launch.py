import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    pkg_name = 'odom_monitor_v5' # Make sure this matches your package name!
    pkg_path = get_package_share_directory(pkg_name)

    # 1. Process the URDF file
    urdf_file = os.path.join(pkg_path, 'urdf', 'my_robot.urdf') # Make sure you put your URDF in a 'urdf' folder
    doc = xacro.process_file(urdf_file)
    robot_desc = doc.toxml()

    # 2. Start Gazebo Sim (Empty World)
    gazebo_pkg = get_package_share_directory('ros_gz_sim')
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gazebo_pkg, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': '-r empty.sdf'}.items()
    )

    # 3. Start Robot State Publisher
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )

    # 4. Spawn the robot in Gazebo
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-string', robot_desc, '-name', 'my_robot', '-z', '0.5'] # Drops the robot slightly from the air
    )

    # 5. Start the Bridge using your YAML file
    bridge_config = os.path.join(pkg_path, 'config', 'gz_bridge.yaml')
    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': bridge_config,
            'expand_gz_topic_names': True
        }],
        output='screen'
    )

    # 6. Start the dashboard to monitor the drift
    rqt_dashboard = Node(
        package="rqt_runtime_monitor",
        executable="rqt_runtime_monitor",
        name="rqt_dashboard",
    )  

    # 7. Start the Twist Multiplexer
    mux_config = os.path.join(pkg_path, 'config', 'twist_mux_locks.yaml')
    twist_mux_node = Node(
        package='twist_mux',
        executable='twist_mux',
        parameters=[mux_config],
        remappings=[('/cmd_vel_out', '/cmd_vel')],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        node_robot_state_publisher,
        spawn_entity,
        gz_bridge,
        rqt_dashboard,
        twist_mux_node
    ])
