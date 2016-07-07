from slackclient import SlackClient
from multiprocessing import process, Pipe
import threading, subprocess, time
import slack_io

class User:
	def __init__(self, UUID, message, display_name, clip_pref):
		self.clip_pref = clip_pref
		self.UUID = UUID
		self.display_name = sc.api_call('users.info', user=UUID)

	def print_user_info(self):
		print "Name: ", self.name, ", UUID:", self.UUID


command = ["python", "slack_io.py"]
proc = subprocess.Popen(command, stdin=PIPE, stdout=PIPE)

while True:
    next_line = proc.communicate()[0]
    #print next_line

'''
while True:
	line = proc.rtm_output.readline()
	if line != '':
		cur_user = line.rstrip()
	else:
		break
'''