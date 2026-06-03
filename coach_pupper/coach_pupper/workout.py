# Our custom interface, GoPupper. This specifies the message type (commands).
from pupper_interfaces.srv import GoPupper

# Packages to let us create nodes and spin them up
import rclpy
from rclpy.node import Node
from MangDang.mini_pupper.display import Display, BehaviorState
from resizeimage import resizeimage  # library for image resizing
from PIL import Image, ImageDraw, ImageFont # library for image manip.
import RPi.GPIO as GPIO
import sounddevice as sd
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
    
    def image_open(self, workoutLoc):
        # Open the image (Your image file name goes here)
        MAX_WIDTH = 320
        disp = Display()
        print("This is image open ", workoutLoc)
        try:
            imgLoc = workoutLoc
            print("This is image open imageLoc", imgLoc)
            imgFile = Image.open(imgLoc)
        except:
            print("Error")
        # Convert to RGBA if needed
        if (imgFile.format == 'PNG'):
            if (imgFile.mode != 'RGBA'):
                imgOld = imgFile.convert("RGBA")
                imgFile = Image.new('RGBA', imgOld.size, (255, 255, 255))

        # Display it on Pupper's LCD display
        disp.show_image(imgLoc)

    def send_pushup(self):
        self.send_move_request("tilt_down")
        self.send_move_request("move_down")
        self.send_move_request("move_up")
        self.send_move_request("tilt_up")
    
    def send_squat(self):
        self.send_move_request("tilt_up")
        self.send_move_request("move_down")
        self.send_move_request("move_up")
        self.send_move_request("tilt_down")

    def send_lunge(self):
        self.send_move_request("tilt_left")
        self.send_move_request("move_left")
        self.send_move_request("tilt_right")
        self.send_move_request("tilt_right")
        self.send_move_request("move_right")
        self.send_move_request("tilt_left")

    def workout_loop(self, workout, peer):
        workout = sd.play("workoutduration.mp3")
        if workout == "pushup":
            workout_movement = self.send_pushup
        elif workout == "squat":
            workout_movement = self.send_squat
        elif workout == "lunge":
            workout_movement = self.send_lunge
        start_time = time.time()
        workout.play()
        while time.time() - start_time < 30:
            if peer:
                self.workout_movement()
            else:
                workout.stop()
                pass
            
    def send_workout(self, workout, peer):
        if workout == "pushup":
            fileLoc = "/home/ubuntu/ros2_ws/src/coach_pupper/coach_pupper/workouts/pushup.gif"
        elif workout == "squat":
            fileLoc == "/home/ubuntu/ros2_ws/src/coach_pupper/coach_pupper/workouts/squat.gif"
        elif workout == "lunge":
            fileLoc == "/home/ubuntu/ros2_ws/src/coach_pupper/coach_pupper/workouts/lunges.gif"
        self.image_open(fileLoc)
        self.workout_loop(workout, peer)
        # Change this to default image
        #self.image_open("/home/ubuntu/ros2_ws/src/finalproject/finalproject/Push-Up-ezgif.com-resize.gif")
        
