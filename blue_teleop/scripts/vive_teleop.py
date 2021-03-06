#!/usr/bin/env python
import rospy
import sys
import actionlib
from std_msgs.msg import Int32
from std_msgs.msg import Float32
from geometry_msgs.msg import PoseStamped

from control_msgs.msg import (
    GripperCommandAction,
    GripperCommandGoal,
)
global cmd_label
global command_publisher
cmd_label = 0

class GripperClient(object):
    def __init__(self):
        self._client = actionlib.SimpleActionClient(
            "blue_controllers/gripper_controller/gripper_cmd",
            GripperCommandAction,
        )
        # Wait 10 Seconds for the gripper action server to start or exit
        if not self._client.wait_for_server(rospy.Duration(10.0)):
            rospy.logerr("Exiting - Gripper Action Server Not Found")
            rospy.signal_shutdown("Action Server not found")
            sys.exit(1)

        self._goal = GripperCommandGoal()
        self.clear()
        rospy.Subscriber("trigger", Float32, self.goal_callback, queue_size=1)

    def command(self, position, effort):
        self._goal.command.position = position
        self._goal.command.max_effort = effort
        self._client.send_goal(self._goal)

    def stop(self):
        self._client.cancel_goal()

    def wait(self, timeout=0.1):
        self._client.wait_for_result(timeout=rospy.Duration(timeout))
        return self._client.get_result()

    def goal_callback(self, msg):
        self._goal.command.position = -1.5 * msg.data
        self._client.send_goal(self._goal)
        # rospy.logerr("msg.data: {}".format(msg.data))
        self.wait()

    def set_effort(self, eff):
        self._goal.command.max_effort = eff

    def clear(self):
        self._goal = GripperCommandGoal()

def command_callback(msg):
    global command_publisher
    global cmd_label
    if cmd_label == 1:
        command_publisher.publish(msg)

def label_callback(msg):
    global cmd_label
    cmd_label = msg.data

def main():
    global command_publisher
    rospy.init_node("vive_teleop")
    command_publisher = rospy.Publisher("pose_target/command", PoseStamped, queue_size=1)
    rospy.Subscriber("controller_pose", PoseStamped, command_callback, queue_size=1)
    rospy.Subscriber("command_label", Int32, label_callback, queue_size=1)

    gc = GripperClient()
    gc.clear()
    gc.set_effort(2.5)

    rospy.spin()

if __name__ == "__main__":
    main()
