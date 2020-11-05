#!/usr/bin/python3

# import the necessary packages
import rospy
import rospkg

import csv

# import the necessary msgs. Example with msg type String_Int_Arrays:
from std_msgs.msg import String
from std_msgs.msg import UInt16MultiArray
from std_msgs.msg import UInt8


class detector():
    """ Class class_name.

    Info about the class
    """

    def __init__(self):
        """Class constructor

        It is the constructor of the class. It does:
        - Subscribe to asr topic
        - Define publisher for asr detected word
        - Create msg type to send
        - take path to every database
        """

        #Subscribe to ROS topics
        self.detector_sub = rospy.Subscriber("asr_full_text", String, self.callback)
        self.mode_sub = rospy.Subscriber("mode", UInt8, self.mode_cb)

        #Define the ROS publishers
        self.fragance_pub = rospy.Publisher("fragances", UInt16MultiArray, queue_size=0)
        self.function_pub = rospy.Publisher("function", UInt8, queue_size=0)

        #Define object as msg type
        self.fragance_msg = UInt16MultiArray()
        self.fragance_msg.data = []

        self.function_msg = UInt8()

        self.mode = 2

        self.databases()

        print("[INFO] Node started")

    def databases(self):
        rospack = rospkg.RosPack()
        pkg_name = "voice_recognition"			# Name of the ROS package. Is used to take the path of the package
        path_fragances = rospack.get_path(pkg_name) + "/data/long_fragances.csv"
        path_options = rospack.get_path(pkg_name) + "/data/long_options.csv"

        self.word = []
        self.frag1 = []
        self.frag2 = []
        self.options = []
        self.modes = []

        with open(path_fragances) as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=";")	            # Read the csv file
            for row in csv_reader:								        # Go through every row in the csv file
                self.word.append(row[0])					            # Save the path of every SVG file into the array
                self.frag1.append(row[1])
                self.frag2.append(row[2])

        with open(path_fragances) as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=";")	            # Read the csv file
            for row in csv_reader:								        # Go through every row in the csv file
                self.options.append(row[0])					            # Save the path of every SVG file into the array
                self.modes.append(row[1])

    def detect_word(self, phrase):

        if self.mode == 0:
            detected = False
            for j in range(len(self.options)):
                if phrase.find(self.options[j]) >= 0:
                    detected = True
                    self.function_msg.data = int(self.modes[j])
            if detected == False:
                self.function_msg.data = 2                          # If modes not found, lets ask Alexa
            self.function_pub.publish(self.function_msg)

        elif self.mode == 1:
            self.fragance_msg.data = []
            for j in range(len(self.word)):
                if phrase.find(self.word[j]) >= 0:
                    if int(self.frag1[j]) in self.fragance_msg.data:
                        pass
                    else:
                        self.fragance_msg.data.append(int(self.frag1[j]))
                    if int(self.frag2[j]) != 0:
                        if int(self.frag2[j]) in self.fragance_msg.data:
                            pass
                        else:
                            self.fragance_msg.data.append(int(self.frag2[j]))
                    print (self.word[j])
            self.fragance_pub.publish(self.fragance_msg)
            
        elif self.mode == 2:
            continue


    def run_loop(self):
        """ Infinite loop.

        When ROS is closed, it exits.
        """
        while not rospy.is_shutdown():
            #functions to repeat until the node is closed
            rospy.spin()

    def stopping_node(self):
        """ROS closing node

        Is the function called when ROS node is closed."""
        print("\n\nBye bye! :)\n\n")

    def callback(self, data):
        """ROS callback

        This void is executed when a message is received"""
        self.detect_word(data.data)

    def mode_cb(self, data):
        """ROS callback

        This void is executed when a message is received"""
        self.mode = data.data


if __name__=='__main__':
    """ Main void.

    Is the main void executed when started. It does:
    - Start the node
    - Create an object of the class
    - Run the node

    """
    try:
        rospy.init_node('detector_node')       # Init ROS node

        word_detector = detector()
        rospy.on_shutdown(word_detector.stopping_node)   #When ROS is closed, this void is executed

        word_detector.run_loop()

    except rospy.ROSInterruptException:
        pass