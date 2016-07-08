from slackclient import SlackClient
import threading, subprocess, time, Queue, sys, random
sys.path.append('/Users/sanvidpro/Desktop/sandwichvideo')
import sandwich

authy = sandwich.get_auth('/Volumes/Sandwich/assets/python/auth.csv')
token = authy['slack']['token']
sc = SlackClient(token)
#chan = 'C06PTC83B' #LIVE OUTPUT
chan = 'C12PL8TSS' #TEMP SLACK

message_queue = Queue.Queue()
lunch_options = ['Fritzi','Grow','Edibol','Cafe Gratitude','Pie Hole','Wurstkurch','Cerveteca','Americano','Umami','Groundwork',]


class User:
    def __init__(self, UUID, recent_message, display_name, clip_pref):
        self.UUID = UUID
        self.recent_message = recent_message
        self.clip_pref = clip_pref
        try:
            user_info = sc.api_call('users.info', user=UUID)
            fn = user_info['first_name']
            ln = user_info['last_name']
            full_name = fn + ' ' + ln
        except:
            full_name = 'encoder'
        self.display_name = full_name
        
	def print_user_info(self):
		print 'Name: ', self.display_name, ', UUID: ', self.UUID

def send_to_slack(slackput):
    try:
        sc.rtm_send_message(chan,slackput)
    except:
        print 'Something happened while attempting to send your message to slack'

def listen_to_slack():
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
                                time.sleep(1)
            else:
                print 'Unable to connect to Slack right now'
        except:
            print 'You caused a much larger problem than you probably realize.'

def listener():
    listener = threading.Thread(target=listen_to_slack)
    listener.daemon = True
    listener.start()


def check_message_type(cur_message):
    if 'cuts' in cur_message and 'scenes' not in cur_message:
        return 0
    elif '/Volumes/' in cur_message:
        return 1
    elif 'lunch' or 'food' in cur_message:
        return 2
    else:
        return 3

def lunch_answer():
    lunch_message = 'You should have ' +str(lunch_options[random.randint(0,9)]) + ' for lunch.'
    send_to_slack(lunch_message)

def conversation():
    listener()
    while True:
        cur_message = message_queue.get()
        time.sleep(1)
        print cur_message
        if check_message_type(cur_message[1]) <= 1:
            print 'This is either a cut or a scene.'
        elif check_message_type(cur_message[1]) == 2:
            lunch_answer()
            
conversation()
