'''
Filename: color_detection.py
Students: Audrey Liang, Oscar Tran, Madison Tran
Final Project: Rock Paper Scissors Color detection

This is the main file that detects color during the Rock Paper Scissors game and will make Coach Pupper move according to what color it sees. We have Red(Scissors), Green (Rock), and Yellow(Paper), and Coach Pupper will do a work out based on who wins, and what workout it does.

How to use:
Usage

	First run the colcon build command below
	colcon build --packages-select camera_basics

	After building the packages, run these 2 ros2 commands in order 
	Run these 2 ros2 commands
	ros2 launch depthai_ros_driver camera.launch.py
	ros2 run camera_basics color_detection
'''

import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge
from geometry_msgs.msg import Twist

# Creating a class for the echo camera node. Note that this class inherits from the Node class.
class echo_camera(Node):
	def __init__(self):
		#Initializing a node with the name 'echo_camera'
		super().__init__('echo_camera')
		
		#Subscribing to the /oak/rgb/image_raw topic that carries data of Image type
		self.subscription = self.create_subscription(Image, '/oak/rgb/image_raw', self.echo_topic, 10)
		self.subscription #this is just to remove unused variable warnings
		
		#CvBridge has functions that allow you to convert ROS Image type data into OpenCV images
		self.br = CvBridge()
		self.hsv_red_lower = [0, 85, 85]
		self.hsv_red_upper = [5, 255, 255] #prev lower
		
		self.hsv_green_lower = [40, 50, 45]
		self.hsv_green_upper = [70, 255, 255] #prev was hsv_lower1, upper1

		self.hsv_yellow_lower = [23, 50, 45]
		self.hsv_yellow_upper = [30, 255, 255] 
		# self.move = False
		# self.publisher_ = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
	
	# Callback function to echo the video frame being received	
	def echo_topic(self, data):
		#Logging a message - helps with debugging later on
		self.get_logger().info('Receiving video frame')
		
		#Using the CvBridge function imgmsg_to_cv to convert ROS Image to OpenCV image. Now you can use this image to do other OpenCV things
		current_frame = self.br.imgmsg_to_cv2(data)
		
		hsv = cv2.cvtColor(current_frame, cv2.COLOR_BGR2HSV)
		
		#mask to detect red 
		
		lower_red = np.array(self.hsv_red_lower)
		upper_red = np.array(self.hsv_red_upper)
		
		mask_red = cv2.inRange(hsv, lower_red, upper_red)
		
		#mask to detect green
		lower1_green = np.array(self.hsv_green_lower)
		upper1_green = np.array(self.hsv_green_upper)
		mask_green = cv2.inRange(hsv, lower1_green, upper1_green)
		
		#mask to detect yellow
		
		lower_yellow = np.array(self.hsv_yellow_lower)
		upper_yellow = np.array(self.hsv_yellow_upper)
		
		mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
		
		red = np.any(mask_red > 0)
		green = np.any(mask_green > 0)
		yellow = np.any(mask_yellow > 0)
	
	#combining the masks so that you can detect either one in your frame
		combMask  = cv2.bitwise_or(mask_red, mask_green, mask_yellow)
		
		masked_frame1 = cv2.bitwise_and(current_frame, current_frame, mask=combMask)
		
		#Using the imshow function to echo display the image frame currrently being published by the OAK-D
		#cv2.imshow("camera", current_frame)
		
		img_window_name = "color_detected"
		cv2.namedWindow(img_window_name, cv2.WINDOW_NORMAL)
		cv2.resizeWindow(img_window_name, 800, 400)
		cv2.imshow(img_window_name, np.hstack([current_frame, masked_frame1]))
		#This shows each image frame for 1 millisecond, try playing around with different wait values to achieve the video framerate you want!
		#Detects green, changes class variable accordingly to move turtle and logs message
		if green:
			# self.move = True
			self.get_logger().info('Receiving green')
		#go commands 
		
		#Detects red, changes class variable accordingly to move turtle and logs message
		elif red:
		#stop command
			# self.move = False
			self.get_logger().info('Receiving red')
		elif yellow:
		#stop command
			# self.move = False
			self.get_logger().info('Receiving Yellow')

# Main function 		
def main(args=None):
	# Initializing rclpy (ROS Client Library for Python)
	rclpy.init(args=args)
	
	#Create an object of the echo_camera class
	echo_obj = echo_camera()
	
	#Keep going till termination
	rclpy.spin(echo_obj)
	
	#Destroy node when done 
	echo_obj.destroy_node()
	
	#Shutdown rclpy
	rclpy.shutdown()
	
if __name__ == '__main__':
	main()
