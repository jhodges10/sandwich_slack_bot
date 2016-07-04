#Slack bot with other functions

import sys,subprocess,time,os, csv
from slackclient import SlackClient
from multiprocessing import Process
from fuzzywuzzy import fuzz,process
import threading

##### DECLARATIONS #####
chan = "C06PTC83B" #LIVE OUTPUT
token = "xoxb-36774633444-7WG8kaLpG23HeRcLjrix7RA4"# found at https://api.slack.com/web#authentication
sc = SlackClient(token)

global message

message = ''

'''
def send_to_slack(slackput):
    try:
        sc.rtm_send_message(chan,slackput)
    except:
        print "Something happened while attempting to send to slack"
'''

def listen_to_slack():
    try:
        if sc.rtm_connect():
            while True:
                new_evts = sc.rtm_read()
                for evt in new_evts:
                    print(evt)
                if "type" in evt:
                    if evt["type"] == "message" and "text" in evt:
                        message = evt["text"]
                        return message

        else:
            print "failure"
    except:
        print "uber fail"


threading.Thread(target=listen_to_slack).start()

while True:
    print message
