from setuptools import find_packages, setup

package_name = 'odom_monitor_v3'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='deepak-r',
    maintainer_email='wssedd18@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            "odom_drift_updater_v3 = odom_monitor_v3.monitor_node:main",
            "slip_tester = odom_monitor_v3.slip_tester:main",
        ],
    },
)
