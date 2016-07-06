#listen to slack
from slackclient import SlackClient
import sys
sys.path.append('/Users/sanvidpro/Desktop/sandwichvideo')
import sandwich


authy = sandwich.get_auth('/Volumes/Sandwich/assets/python/auth.csv')
token = authy['slack']['token']


##### DECLARATIONS #####

global sc
global chan


sc = SlackClient(token)

chan = "C06PTC83B" #LIVE OUTPUT

def send_to_slack(slackput):
    try:
        sc.rtm_send_message(chan,slackput)
    except:
        print "Something happened while attempting to send your message to slack"

def listen():
    evt = ''
    message = ''
    for attempt in range(100):
        try:
            if sc.rtm_connect():
                while True:
                    new_evts = sc.rtm_read()
                    for evt in new_evts:
                        #print evt   
                        if "type" in evt:
                            if evt["type"] == "message" and "text" in evt:
                                message = evt["text"]
                                person = evt["user"]
                                output_command = [person,message]
                                print output_command

            else:
                print "Unable to connect to Slack"
        except:
            print "The whole thing failed."

listen()
