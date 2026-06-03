########
# Name: pupperGame.py
#
# Purpose: Run the base game code, main code taht will direct pupper to workouts.
#
# Usage: After conpling and sourcing the ~/ros2_ws/install/setup.bash , launch the service like this:
#         ros2 run go_pupper_srv service
#
# Author: Madison Tran <mat034@ucsd.edu>
#
# Acknowledgements: Used some code from BIMM 182 and CSE 8A
# Date: 28 May 2026
#
########

import sys
import random
import os
import sounddevice as sd
import time
import pygame
pygame.mixer.init()
from pupper_interfaces.srv import GoPupper
import numpy as np 
from sensor_msgs.msg import Image as sensormsg
import cv2
from cv_bridge import CvBridge
from geometry_msgs.msg import Twist

# Packages to let us create nodes and spin them up
import rclpy
from rclpy.node import Node
from MangDang.mini_pupper.display import Display, BehaviorState
from resizeimage import resizeimage  # library for image resizing
from PIL import Image, ImageDraw, ImageFont # library for image manip.
import RPi.GPIO as GPIO
#import sounddevice as sd
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

class SampleControllerAsync(Node):
    def __init__(self):
        # initalize
        super().__init__('sample_controller')
        self.cli = self.create_client(GoPupper, 'pup_command')
        self.thinking = False
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

    ####
    # Name: image_open
    #
    # Purpose: Open images on Pupper's screen
    ####
    def image_open(self, workoutLoc):
        # Open the image (Your image file name goes here)
        MAX_WIDTH = 320
        disp = Display()
        imgFile = None
        print("This is image open ", workoutLoc)
        try:
            imgLoc = workoutLoc
            print("This is image open imageLoc", imgLoc)
            imgFile = Image.open(imgLoc)
        except:
            print("Error")
        print("Huzzah")
        # Convert to RGBA if needed
        if (imgFile.format == 'PNG'):
            if (imgFile.mode != 'RGBA'):
                imgOld = imgFile.convert("RGBA")
                imgFile = Image.new('RGBA', imgOld.size, (255, 255, 255))

        # Display it on Pupper's LCD display
        disp.show_image(imgLoc)

    ####
    # Name: send_pushup
    #
    # Purpose: Make Pupper do a pushup
    ####
    def send_pushup(self):
        self.send_move_request("tilt_down")
        self.send_move_request("move_down")
        self.send_move_request("move_up")
        self.send_move_request("tilt_up")
    
    ####
    # Name: send_squat
    #
    # Purpose: Make Pupper do a squat
    ####
    def send_squat(self):
        self.send_move_request("tilt_up")
        self.send_move_request("move_down")
        self.send_move_request("move_up")
        self.send_move_request("tilt_down")

    ####
    # Name: send_lunge
    #
    # Purpose: Make Pupper do a lunge
    ####
    def send_lunge(self):
        self.send_move_request("tilt_left")
        #self.send_move_request("move_left")
        self.send_move_request("tilt_right")
        self.send_move_request("tilt_right")
        #self.send_move_request("move_right")
        self.send_move_request("tilt_left")
    
    ####
    # Name: workout_loop
    #
    # Purpose: Make Pupper do a specific workout with music for 30 seconds
    ####
    def workout_loop(self, workout, peer):
        pygame.mixer.music.load("/home/ubuntu/ros2_ws/src/coach_pupper/coach_pupper/music/workoutduration.mp3")
        if workout == "pushup":
            workout_movement = self.send_pushup
        elif workout == "squat":
            workout_movement = self.send_squat
        elif workout == "lunge":
            workout_movement = self.send_lunge
        start_time = time.time()
        pygame.mixer.music.play()
        while time.time() - start_time < 30:
            if peer:
                workout_movement()
            else:
                pygame.mixer.music.stop()
                pass
        pygame.mixer.music.stop()
    
    ####
    # Name: send_workout
    #
    # Purpose: Display the proper workout gif on pupper's screen
    ####
    def send_workout(self, workout, peer):
        if workout == "pushup":
            fileLoc = "/home/ubuntu/ros2_ws/src/coach_pupper/coach_pupper/workouts/pushup.gif"
        elif workout == "squat":
            fileLoc = "/home/ubuntu/ros2_ws/src/coach_pupper/coach_pupper/workouts/squat.gif"
        elif workout == "lunge":
            fileLoc = "/home/ubuntu/ros2_ws/src/coach_pupper/coach_pupper/workouts/lunges.gif"
        self.image_open(fileLoc)
        self.workout_loop(workout, peer)
        # Change this to default image
        #self.image_open("/home/ubuntu/ros2_ws/src/finalproject/finalproject/Push-Up-ezgif.com-resize.gif")
    ####
    # Name: rockPaperScissors
    #
    # Purpose: Takes in the input from the user(input1) and random robot(input2) to detemine workout move. 
    ####
    def rockPaperScissors(self, input1, input2):
        if input1 == input2:
            #tie.play()
            return tWin
        elif input1 == r:
                self.image_open("/home/ubuntu/ros2_ws/src/coach_pupper/coach_pupper/gameImages/imageRock.jpg")
                if input2 == p:
                    #lose.play()
                    return pWin
                else:
                    #win.play()
                    return yWin 
        elif input1 == p:
                self.image_open("/home/ubuntu/ros2_ws/src/coach_pupper/coach_pupper/gameImages/imagePaper.jpg")
                if input2 == s:
                    #lose.play()
                    return pWin
                else:
                    #win.play()
                    return yWin 
        elif input1 == s:
                self.image_open("/home/ubuntu/ros2_ws/src/coach_pupper/coach_pupper/gameImages/imageScissors.jpg")
                if input2 == r:
                    #lose.play()
                    return pWin
                else:
                    #win.play()
                    return yWin
####
# Name: echo_camera
#
# Purpose: Allow pupper to recognize and sense colors red, green, and yellow.
####
class echo_camera(Node):
	def __init__(self):
		#Initializing a node with the name 'echo_camera'
		super().__init__('echo_camera')
		self.result = ""
		
		#Subscribing to the /oak/rgb/image_raw topic that carries data of Image type
		self.subscription = self.create_subscription(sensormsg, '/oak/rgb/image_raw', self.echo_topic, 10)
		self.subscription #this is just to remove unused variable warnings
		
		#CvBridge has functions that allow you to convert ROS Image type data into OpenCV images
		self.br = CvBridge()
		self.hsv_red_lower = [0, 85, 85]
		self.hsv_red_upper = [5, 255, 255] #prev lower
		
		self.hsv_green_lower = [40, 50, 45]
		self.hsv_green_upper = [70, 255, 255] #prev was hsv_lower1, upper1

		self.hsv_yellow_lower = [23, 50, 45]
		self.hsv_yellow_upper = [30, 255, 255] 
	
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
		#cv2.imshow(img_window_name, np.hstack([current_frame, masked_frame]))
		cv2.imshow(img_window_name, np.hstack([current_frame, masked_frame1]))
		#This shows each image frame for 1 millisecond, try playing around with different wait values to achieve the video framerate you want!
		#Detects green, changes class variable accordingly to move turtle and logs message
		
		if green:
		    self.result = "green"
		    self.get_logger().info('Receiving green')
            
		#go commands 
		elif red:
		    self.result = "red"
		    self.get_logger().info('Receiving red')
            
		elif yellow:
		    self.result = "yellow"
		    self.get_logger().info('Receiving Yellow')
		return result

#Change all vlc to sd
#os.add_dll_directory(r"C:\Program Files\VideoLAN\VLC") 
#import vlc
#from workout import send_workout
#input1 will be user, input2 will be computer
r = "Rock"
p = "Paper"
s = "Scissors"
pWin = "Pupper wins!"
yWin = "You win!"
tWin = "Tie!"

peer = True


####
# Name: moveGen
#
# Purpose: Randomly generate Pupper move.
####
def moveGen():
    move = random.randint(1, 3)
    if move == 1:
        return r
    elif move == 2:
        return p     
    else:
        return s


####
# Name: reader
#
# Purpose: Detect user move based on color sensors.
####           
def reader(controller):
    echo_obj = echo_camera()
    robotMove = moveGen()
    userMove = "Nothing :("
    result = echo_obj.result
    if result == "green": #REPLACE WITH COLOR DETECTION
        userMove = r
    elif result == "yellow": #REPLACE WITH COLOR DETECTION
        userMove = p
    elif result == "red": #REPLACE WITH COLOR DETECTION
        userMove = s
    outcome = controller.rockPaperScissors(userMove, robotMove)
    print("Your move was", userMove, "and Pupper's move was", robotMove)
    echo_obj.destroy_node()
    return outcome

####
# Name: main
#
# Purpose: Run the game and output correct workout sound and images based on outcome.
####     
def main():
    rclpy.init()
    sample_controller = SampleControllerAsync()
    holder3 = "/home/ubuntu/ros2_ws/src/coach_pupper/coach_pupper/coachPupper.jpg"
    #disp.show_image(holder3)  
    print("Welcome, type Ready to begin!")
    answer = input()
    while answer != "N": #REPLACE WITH DETECTION
    	holder3 = "/home/ubuntu/ros2_ws/src/coach_pupper/coach_pupper/coachPupper.jpg"
    	#disp.show_image(holder3)
    	print("Show your move!")
    	answer = reader(sample_controller)
    	outcome = answer
    	if outcome == tWin:
            pygame.mixer.music.load("/home/ubuntu/ros2_ws/src/coach_pupper/coach_pupper/music/replay.mp3")
            pygame.mixer.music.play()
            time.sleep(2)
            print(tWin)
            time.sleep(3)
            sample_controller.send_workout("lunge", peer)
    	if outcome == pWin:
            pygame.mixer.music.load("/home/ubuntu/ros2_ws/src/coach_pupper/coach_pupper/music/loss.mp3")
            pygame.mixer.music.play()
            time.sleep(2)
            print(pWin)
            time.sleep(3)
            sample_controller.send_workout("pushup", peer)
    	if outcome == yWin:
            pygame.mixer.music.load("/home/ubuntu/ros2_ws/src/coach_pupper/coach_pupper/music/win.mp3")
            pygame.mixer.music.play()
            time.sleep(2)
            print(yWin)
            time.sleep(3)
            sample_controller.send_workout("squat", peer)
    print("Thanks for playing with Pupper!")
    sample_controller.destroy_node()
    rclpy.shutdown()
        
