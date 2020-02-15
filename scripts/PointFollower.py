#!/usr/bin/env python
import rospy
import math
from geometry_msgs.msg import PointStamped
from ackermann_msgs.msg import AckermannDrive
from std_msgs.msg import String
from state_controller.msg import TwistLabeled
from tf import TransformListener

class PointFollower():
    """
    Directs the tractor at a point in 2D space, changing speed with distance from point.

    Sub: /point2follow - PointStamped
    Pub: /state_controller/cmd_behavior_twist - TwistLabeled
    """
    def __init__(self):
        rospy.init_node('PointFollower', anonymous=True)
        self.subPoint = rospy.Subscriber('/point2follow', PointStamped, self.callback)
        self.pubDrive = rospy.Publisher('/state_controller/cmd_behavior_twist',TwistLabeled, queue_size=10)
        self.goalPoint = None
        self.rate = rospy.Rate(1)
        self.tf = TransformListener()
        self.prevAngle = 0

    def callback(self,data):
        #self.goalPoint = self.tf.transformPoint('/hood',data).point
        self.goalPoint = data.point

    def follow(self):
        """
        Follows the point given, moving faster if farther, and stopping if closer than 1 meter.
        """
        drive_msg = TwistLabeled()
        drive_msg.label = String()
        drive_msg.label.data = "2D PointFollower"
        distance = math.sqrt(self.goalPoint.x**2+self.goalPoint.y**2)
        # distance is in meters
        if (distance > 1): #If obstacle is more than 1 meter away, go, faster if farther
            speed = 0.25 * (distance - 1) 
        else: # if obstacle is really close, stop moving
            speed = 0
        if(speed > 1):
            speed = 1
        drive_msg.twist.linear.x = speed
        angle = math.atan2(self.goalPoint.y,self.goalPoint.x) # Finds the angle at which the tractor should turn
        angle = math.degrees(angle) # set the angle to the ackermann message
        if(angle > 45):
            angle = 45
        elif(angle < -45):
            angle = -45
        elif(distance < 1): 
            angle = self.prevAngle
        self.prevAngle = angle
        drive_msg.twist.angular.z = angle / 45
        self.pubDrive.publish(drive_msg) # publish

    def main(self):
        while not rospy.is_shutdown():
            if(self.goalPoint != None):
                self.follow()
            self.rate.sleep()

if __name__ == '__main__':
    follower = PointFollower()
    follower.main()