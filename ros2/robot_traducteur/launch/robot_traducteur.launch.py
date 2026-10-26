from launch import LaunchDescription
from launch_ros.actions import Node

# Lance les nœuds ROS 2 « traducteur » et « voix ».
def generate_launch_description():
    return LaunchDescription([
        Node(package="robot_traducteur", executable="traducteur", output="screen"),
        Node(package="robot_traducteur", executable="voix", output="screen"),
    ])
