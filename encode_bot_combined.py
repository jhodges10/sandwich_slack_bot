from slackclient import SlackClient
import threading, subprocess, time, Queue, sys, random
sys.path.append('/Users/sanvidpro/Desktop/sandwichvideo')
import sandwich
import csv

authy = sandwich.get_auth('/Volumes/Sandwich/assets/python/auth.csv')
token = authy['slack']['token']
sc = SlackClient(token)
#chan = 'C06PTC83B' #LIVE OUTPUT
chan = 'C12PL8TSS' #TEMP SLACK

message_queue = Queue.Queue()
lunch_options = ['Fritzi','Grow','Edibol','Cafe Gratitude','Pie Hole','Wurstkurch','Cerveteca','Americano','Umami','Groundwork',]

#with open('users.csv', 'rb') as user_file:
    

class User:
    def __init__(self, UUID, recent_message, display_name, clip_pref):
        self.UUID = UUID
        self.recent_message = recent_message
        self.clip_pref = clip_pref
        self.display_name = display_name
        
    def check_user_display_name():
        try:
            user_info = sc.api_call('users.info', user=UUID)
            fn = user_info['first_name']
            ln = user_info['last_name']
            full_name = fn + ' ' + ln
        except:
            full_name = 'encoder'
        return self.display_name = full_name
        
	def print_user_info(self):
		print 'Name: ', self.display_name, ', UUID: ', self.UUID

def send_to_slack(slackput):
    try:
        sc.rtm_send_message(chan,slackput)
    except:
        print 'Something happened while attempting to send your message to slack'

def slack_RTM_connection():
    evt = ''
    message = ''
    for attempt in range(100):
        try:
            if sc.rtm_connect():
                while True:
                    new_evts = sc.rtm_read()
                    for evt in new_evts:
                        if 'type' in evt:
                            if evt['type'] == 'message' and 'text' in evt:
                                message = evt['text']
                                person = evt['user']
                                output_command = [person,message]
                                message_queue.put(output_command)
                                time.sleep(.5)
            else:
                print 'Unable to connect to Slack right now'
        except:
            print 'You caused a much larger problem than you probably realize.'

def listener():
    listener = threading.Thread(target=slack_RTM_connection)
    listener.daemon = True
    listener.start()

def check_message_type(cur_message): # Method to find message type
    if '/Volumes/' in cur_message:
        return 1
    elif 'lunch' in cur_message:
        return 2
    elif 'hungry' in cur_message:
        return 2
    elif 'food' in cur_message:
        return 2    
    else:
        return 3

def lunch_answer():
    lunch_message = 'You should have ' +str(lunch_options[random.randint(0,9)]) + ' for lunch.'
    send_to_slack(lunch_message)

def video_handler_type(cur_message):
    if '.mov' in cur_message:
        if 'cuts' in cur_message and 'scenes' not in cur_message:
            print 'This is a cut'
            return 'cut'
        elif 'ae' in cur_message:
            return 'scene'
        elif 'scenes' in cur_message:
            return 'scene'
        else:
            send_to_slack("More than likely, you just added a local file that the server doesn't recognize.")
    else:
        send_to_slack("This isn't a video file.")
        return False

def conversation():
    cur_message = message_queue.get() # Check the cue for the message, only called if the queue has an item in it
    print 'This is the UUID for the person who sent that message: ' +cur_message[0]
    print 'This is what they said:' +cur_message[1]
    if 'U12NSJMD2' not in cur_message[0]: # This filters out messages from the slackbot itself
        if check_message_type(cur_message[1]) == 1: # If the message contains a path to the server, then check what kind it is
            if 'cut' in video_handler_type(cur_message):
                print 'This is definitely a cut.'
            elif 'scene' in video_handler_type(cur_message):
                print 'This is definitely a scene.'
      
        elif check_message_type(cur_message[1]) == 2: # Call the lunch method if the current message contains something related to lunch or food
            lunch_answer()
            
        elif check_message_type(cur_message[1]) == 3:
            send_to_slack("I can't handle this type of input yet")
    else:
        print 'Unknown message type or it handled the bug where the Slack RTM conneciton just started by loading the last message sent.'
        return

'''Calls the listen function which spawns the second thread. It continually checks to see if
    the message queue is empty and if not (meaning it contains something) it triggers the conversation method 
    which in turns checks what kind of message that is before then acting upon it.'''

def controller():
    listener()
    while True:
        if message_queue.empty() is False:
            conversation()
            print "Successfully called the conversation method"
            
controller()