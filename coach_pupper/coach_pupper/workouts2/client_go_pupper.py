#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from mini_pupper_interfaces.srv import DanceCommand
#from pupper_interfaces.srv import GoPupper


class MiniPupperDanceClientAsync(Node):

    def __init__(self):
        super().__init__('mini_pupper_dance_client_async')
        self.cli = self.create_client(DanceCommand, 'dance_command')

        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')

        self.req = DanceCommand.Request()

    def send_dance_request(self, dance_command):
        self.req = DanceCommand.Request()
        self.req.data = dance_command
        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()

def main():
    rclpy.init()
    minimal_client = MiniPupperDanceClientAsync()

    for index, command in enumerate(minimal_client.dance_commands):
        # Start music for the first command
        if index == 0:
            minimal_client.get_logger().info('Starting music...')
            minimal_client.send_play_music_request(dance_song_file_name,
                                                   dance_song_start_second)

        # Send movemoment comment for the robot to dance
        response = minimal_client.send_dance_request(command)
        if response.executed:
            minimal_client.get_logger().info('Command Executed!')

        # Stop music after the last command
        if index == len(minimal_client.dance_commands) - 1:
            minimal_client.get_logger().info('Stopping music...')
            minimal_client.send_stop_music_request()

    minimal_client.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
