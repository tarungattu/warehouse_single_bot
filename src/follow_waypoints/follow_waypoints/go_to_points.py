#! /usr/bin/env python3
# Copyright 2021 Samsung Research America
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
from copy import deepcopy

from geometry_msgs.msg import PoseStamped
from rclpy.duration import Duration
import rclpy
#
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
#
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

json_file_path = '/home/tarun_56/lmas_ws/src/JobShopGA/amr_data.json'


class Go_to_points:
    def __init__(self):
        self.amr1_sequence = []
        self.amr1_ptimes = []

    def parse_json(self, json_file):
        with open(json_file, 'r') as file:
            data = json.load(file)
            
        machine_sequences = []
        ptime_sequences = []
        
        new_machine_sequences = []
        new_ptime_sequences = []
        
            
        for amr in data['amr_list']:
            machine_sequences.append(amr['machine_sequence'])
            ptime_sequences.append(amr['ptime_sequence'])
            
        for machines, ptimes in zip(machine_sequences, ptime_sequences):
            new_machines = []
            new_ptimes = []
            for machine, ptime in zip(machines, ptimes):
                if ptime != 0:
                    new_machines.append(machine)
                    new_ptimes.append(ptime)
            new_machine_sequences.append(new_machines)
            new_ptime_sequences.append(new_ptimes)
        
        print(machine_sequences, ptime_sequences)
        print(new_machine_sequences, new_ptime_sequences)
        amr1_sequence = new_machine_sequences[0]
        amr1_ptimes = new_ptime_sequences[0]
        self.amr1_sequence = amr1_sequence
        self.amr1_ptimes = amr1_ptimes
        return amr1_sequence, amr1_ptimes
    
    def start_execution(self):
        rclpy.init()

        navigator = BasicNavigator()

        m1 = [-3.32, 6.65]
        m2 = [-3.38, 1.46]
        m3 = [1.627, 6.459]
        m4 = [1.681, 1.407]
        loading_dock = [-6.69, 4.028]
        unloading_dock = [3.52, 3.96]

        poses = {
            '0': m1,
            '1': m2,
            '2': m3,
            '3': m4,
            '-1': loading_dock,
            '-2': unloading_dock
        }

        inspection_route = []
        # json_file_path = '/home/tarun_56/pc_ws/src/JobShopGA/amr_data.json'
        # sequence, ptimes = self.parse_json(json_file_path)
        sequence, ptimes = self.amr1_sequence, self.amr1_ptimes

        for m in sequence:
            inspection_route.append(poses[str(m)])

        # Set our demo's initial pose
        # initial_pose = PoseStamped()
        # initial_pose.header.frame_id = 'map'
        # initial_pose.header.stamp = navigator.get_clock().now().to_msg()
        # initial_pose.pose.position.x = -0.004
        # initial_pose.pose.position.y = -0.041
        # initial_pose.pose.orientation.z = 1.0
        # initial_pose.pose.orientation.w = 0.0
        # navigator.setInitialPose(initial_pose)

        # Wait for navigation to fully activate
        # navigator.waitUntilNav2Active()

        # while rclpy.ok():

        # Send our route
        for i,m in zip(range(len(sequence)),sequence):
            goal_pose = PoseStamped()
            goal_pose.header.frame_id = 'map'
            goal_pose.header.stamp = navigator.get_clock().now().to_msg()
            goal_pose.pose.position.x = poses[str(m)][0]
            goal_pose.pose.position.y = poses[str(m)][1]
            goal_pose.pose.orientation.w = 1.0

            navigator.goToPose(goal_pose)
            if m >= 0:
                print(f'Going to machine {m}')
            elif m == -1:
                print('Going to Loading dock for next job')
            elif m == -2:
                print('Going to unloading dock to drop completed job')
            while not navigator.isTaskComplete():
                time.sleep(1)
            
            print(f'job being process for time {ptimes[i]} seconds')
            time.sleep(ptimes[i])



        # Do something during our route (e.x. AI to analyze stock information or upload to the cloud)
        # Simply print the current waypoint ID for the demonstration
        # i = 0
        # while not navigator.isTaskComplete():
        #     i += 1
        #     feedback = navigator.getFeedback()
        #     if feedback and i % 5 == 0:
        #         print('Executing current waypoint: ' +
        #               str(feedback.current_waypoint + 1) + '/' + str(len(sequence)))

        result = navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            print('Inspection of shelves complete! Returning to start...')
        elif result == TaskResult.CANCELED:
            print('Inspection of shelving was canceled. Returning to start...')
            exit(1)
        elif result == TaskResult.FAILED:
            print('Inspection of shelving failed! Returning to start...')

        # Uncomment to go back to start
        # initial_pose.header.stamp = navigator.get_clock().now().to_msg()
        # navigator.goToPose(initial_pose)
        # while not navigator.isTaskComplete():
        #     pass


class JSONFileHandler(FileSystemEventHandler):
    def __init__(self, file_path, callback):
        self.file_path = file_path
        self.callback = callback
        self.callback_called = False

    def on_modified(self, event):
        if event.src_path == self.file_path and not self.callback_called:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
            self.callback(data)
            self.callback_called = True

def wait_for_json_update(file_path, callback):
    event_handler = JSONFileHandler(file_path, callback)
    observer = Observer()
    observer.schedule(event_handler, path=file_path, recursive=False)
    observer.start()

    try:
        while not event_handler.callback_called:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.stop()
    observer.join()

def on_json_update(data):
    print("JSON file updated with new values:")
    print(data)
    # You can put the main execution code here or continue in another function
    go_to_points = Go_to_points()
    go_to_points.parse_json(json_file_path)
    go_to_points.start_execution()  # Call the main execution function

def main():
    
    
    print('go to points is being executed')
    
    wait_for_json_update(json_file_path, on_json_update)
#
if __name__ == '__main__':
    main()
