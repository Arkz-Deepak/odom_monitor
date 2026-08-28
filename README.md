# odom_monitor

A ROS 2 package suite for mobile robot odometry monitoring, diagnostic status reporting, wheel slip detection, Gazebo simulation integration, and multi-topic safety locks.

---

## 🚀 Version History & Releases

This repository tracks iterative updates through Git tags:

| Tag | Version | Description | Key Features |
| --- | --- | --- | --- |
| `v1.0.0` | **v1** | Initial Odom Monitor | Basic `/odom` topic subscription & distance tracking |
| `v2.0.0` | **v2** | Diagnostic Status | Added `/diagnostics` publisher with `DiagnosticStatus` messages |
| `v3.0.0` | **v3** | Slip Detection | Added wheel slip detection algorithms & `slip_tester` node |
| `v4.0.0` | **v4** | Gazebo Simulation | Added Gazebo SIM launch (`sim_launch.py`), `gz_bridge` config & robot URDF |
| `v5.0.0` | **v5** | Safety & Twist Mux | Added `twist_mux_locks.yaml` and multi-topic safety locks |

---

## 🌿 Repository Structure

- **`main` Branch**: Unified ROS 2 package [`src/odom_monitor`](file:///home/deepak-r/mini_project/src/odom_monitor) updated through version milestones.
- **`all-versions` Branch**: Contains all original separate development folders (`odom_monitor_v1` through `odom_monitor_v5`) preserved intact.

---

## 🛠 Build & Installation

Ensure ROS 2 environment is sourced, then build the workspace:

```bash
cd ~/mini_project
colcon build --symlink-install
source install/setup.bash
```

### Running Nodes

- **Monitor Node**:
  ```bash
  ros2 run odom_monitor monitor_node
  ```
- **Slip Tester**:
  ```bash
  ros2 run odom_monitor slip_tester
  ```
- **Gazebo Simulation**:
  ```bash
  ros2 launch odom_monitor sim_launch.py
  ```
