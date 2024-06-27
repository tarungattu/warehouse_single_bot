import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():

    # Include the robot_state_publisher launch file, provided by our own package. Force sim time to be enabled
    package_name='autobot'  #<--- CHANGE ME

    slam_params_file = os.path.join(get_package_share_directory(package_name), 'config', 'mapper_params_online_async.yaml')
    world = os.path.join(get_package_share_directory(package_name),'worlds','new_warehouse.world')
    rviz_config_file = os.path.join(get_package_share_directory(package_name), 'config', 'warehouse.rviz')


    gazebo_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(package_name), 'launch', 'test_launch.py'
        )]), launch_arguments={'world': world}.items()
    )


    # slam_toolbox = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource([os.path.join(
    #         get_package_share_directory(package_name), 'launch', 'online_async_launch.py'
    #     )])
    # )

    slam_toolbox = Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[slam_params_file]
        )
    
    
    rviz_node= Node(
            package='rviz2',
            executable='rviz2',        
            name='rviz2_robot1',
            arguments=['-d', rviz_config_file],        
            output='screen'
        )



    return LaunchDescription([
        gazebo_robot,
        slam_toolbox,
        rviz_node

        
    ])

