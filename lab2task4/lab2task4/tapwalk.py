########
# Filename: tapwalk.py
# Students: Audrey Liang<ayliang@ucsd.edu>, Madison Tran<mat034@ucsd.edu>, Oscar Tran <ostran@ucsd.edu>
# Lab2 "Hello Robot" Task 4: Tapwalk
#
# Description: A sample Pupper controller. Will move the robot around a bit based on the input detected by the touch sensors, moving for roughly half a second in the corresponding direction.
#
# How to use:
# Usage:
#   (Build the corresponding packages using colcon)
#   Open a separate terminal
#   source ~/ros2_ws/install/setup.bash
#   ros2 launch mini_pupper_bringup bringup.launch.py
#
#   Open up a second terminal
#   source ~/ros2_ws/install/setup.bash
#   ros2 run lab2task4 service
#
#   Open up a third terminal
#   source ~/ros2_ws/install/setup.bash
#   ros2 run lab2task4 tapwalk
#   (Touch a sensor and the robodog will move in the corresponding direction for roughly half a second)
#
# Date: 11 May 2026
#
#
#####################

# Our custom interface, GoPupper. This specifies the message type (commands).
from pupper_interfaces.srv import GoPupper

# Packages to let us create nodes and spin them up
import rclpy
from rclpy.node import Node

import RPi.GPIO as GPIO
import time

# There are 4 areas for touch actions
# Each GPIO to each touch area
touchPin_Front = 6
touchPin_Left  = 3
touchPin_Right = 16
touchPin_Back  = 2

# Use GPIO number but not PIN number
GPIO.setmode(GPIO.BCM)

GPIO.setup(touchPin_Front, GPIO.IN)
GPIO.setup(touchPin_Left,  GPIO.IN)
GPIO.setup(touchPin_Right, GPIO.IN)
GPIO.setup(touchPin_Back,  GPIO.IN)

###
# Method: Sample Controller Async
# Purpose: Constructor for the controler
#
######
class SampleControllerAsync(Node):

    def __init__(self):
        # initalize
        super().__init__('sample_controller')
        self.cli = self.create_client(GoPupper, 'pup_command')

        # Check once per second if service matching the name is available 
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')

        # Create a new request object.
        self.req = GoPupper.Request()


    ###
    # Name: send_move_request
    # Purpose: send_move_request method, send request and spin until receive response or fail
    # Arguments:  self (reference the current class), move_command (the command we plan to send to the server)
    #####
    def send_move_request(self, move_command):
        self.req = GoPupper.Request()
        self.req.command = move_command
        # Debug - uncomment if needed
        #print("In send_move_request, command is: %s" % self.req.command)
        self.future = self.cli.call_async(self.req)  # send the command to the server
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()

    ###
    # Name: pupper_tapwalk
    # Purpose: Try to make the robot do Tapwalk, ie walking in the direction of the input sensor receiving input
    # Arguments:  self (reference the current class) -- /not sure if needed, but won't hurt/
    #####

    def pupper_tapwalk(self):
    	while True:
    	    touchValue_Front = GPIO.input(touchPin_Front)
    	    touchValue_Back  = GPIO.input(touchPin_Back)
    	    touchValue_Left  = GPIO.input(touchPin_Left)
    	    touchValue_Right = GPIO.input(touchPin_Right)
    	    if not touchValue_Front:
    	    	self.send_move_request("move_forward")
    	    if not touchValue_Back:
    	    	self.send_move_request("move_backward")
    	    if not touchValue_Left:
    	    	self.send_move_request("move_left")
    	    if not touchValue_Right:
    	    	self.send_move_request("move_right")
    	    time.sleep(0.1)
    		
###
# Name: Main
# Purpose: Main function. Going to try to have the robot dance salsa. 
#####
def main():
    rclpy.init()
    sample_controller = SampleControllerAsync()

    # send commands to do the conga dance
    sample_controller.pupper_tapwalk()

    # This spins up a client node, checks if it's done, throws an exception of there's an issue
    # (Probably a bit redundant with other code and can be simplified. But right now it works, so ¯\_(ツ)_/¯)
    while rclpy.ok():
        rclpy.spin_once(sample_controller)
        if sample_controller.future.done():
            try:
                response = sample_controller.future.result()
            except Exception as e:
                sample_controller.get_logger().info(
                    'Service call failed %r' % (e,))
            else:
                sample_controller.get_logger().info(
                   'Result of command: %s ' %
                   (response))
            break

    # Destroy node and shut down
    sample_controller.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()


