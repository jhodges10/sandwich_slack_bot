from slackclient import SlackClient
from fuzzywuzzy import fuzz,process
import threading, subprocess, time, Queue, sys, random, csv, dropbox, os
sys.path.append('/Users/sanvidpro/Desktop/sandwichvideo')
import sandwich
from watchdog.observers import Observer # Install with pip, if it fails the you must run 'xcode-select --install' from terminal to install xcode command line tools
from watchdog.events import PatternMatchingEventHandler # Documentation here https://pythonhosted.org/watchdog/api.html

authy = sandwich.get_auth('/Volumes/Sandwich/assets/python/auth.csv')
token = authy['slack_testing']['token']
sc = SlackClient(token)
#chan = 'C06PTC83B' #LIVE OUTPUT
chan = 'C12PL8TSS' #TEMP SLACK

message_queue = Queue.Queue()
lunch_options = ['Fritzi','Grow','Edibol','Cafe Gratitude','Pie Hole','Wurstkurch','Cerveteca','Americano','Umami','Groundwork',]
server_directory = '/Volumes/Sandwich/projects/'
dropbox_path = '/Users/sanvidpro/Dropbox/'

CRF_VALUE = '19' # controls the quality of the encode
PROFILE = 'high422' # h.264 profile
PRESET = 'fast' # encoding speed:compression ratio
TUNE = 'film' # tune setting
FFMPEG_PATH = '/usr/local/bin/ffmpeg' # path to ffmpeg bin
THREADS = '8' # of threads to use
SCALER_540 = "scale=-1:540, scale=trunc(iw/2)*2:540" # 540 Scale settings
SCALER_1080 = "scale=-1:1080, scale=trunc(iw/2)*2:1080" # 1080 Scale settings

app_key = authy['dropbox']['app_key']
app_secret = authy['dropbox']['app_secret']
access_token = authy['dropbox']['access_token']
dropbox_client = dropbox.client.DropboxClient(access_token)

#with open('users.csv', 'rb') as user_file:

'''
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
'''

class directory_watch_handler(PatternMatchingEventHandler):
    patterns = ["*.mov"]

    def process(self, event):
        """
        event.event_type 
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        # the file will be processed there
        print event.src_path, event.event_type  # print now only for degug

    def on_created(self, event):
        self.process(event)
        send_to_slack(event.src_path)

def directory_watchdog(directory):
    path = directory + '/editorial/_to editorial/shots/'
    observer = Observer()
    observer.schedule(directory_watch_handler(), path, recursive = True)
    observer.start()

def file_finder(link):
    link_list = link.split('/')
    project = link_list[4]
    fn = link_list[-1]
    send_to_slack("Looks like this is for the "+str(project) +" project.")
    return project,fn

def fuzzy_dropbox(project):
    directory_listing = os.listdir(dropbox_path)
    dir_temp = process.extract(project,directory_listing,limit=1)
    dropbox_output_directory = dir_temp[0]
    dropbox_output_directory = dropbox_output_directory[0]
    return dropbox_output_directory

def trim(src):
    fn = str(src)
    fn.split('.')
    fn = fn[:-4]
    fn = fn.translate(None,"[\(\)\{\}<>&%!@#$^*]")
    return fn
    
def encode_1080(video,fn,db_dir):
    output = dropbox_path + str(db_dir) +'/cuts/' + fn + "-1080.mov"
    print output
    try:
        subprocess.call([FFMPEG_PATH, '-i', video, '-c:v', 'libx264', '-tune', TUNE, '-pix_fmt', 'yuv420p', '-preset', PRESET, '-profile:v', PROFILE, '-vf', SCALER_1080, '-crf', CRF_VALUE, '-c:a', 'libfdk_aac', '-b:a', '192k', '-threads', THREADS, output])
        return output
    except:
        print "That directory didn't exist or something else happened"
        
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
                                time.sleep(1)
            else:
                print 'Unable to connect to Slack right now'
        except:
            print 'You caused a much larger problem than you probably realize.'

def listener():
    listener = threading.Thread(target=slack_RTM_connection)
    listener.daemon = True
    listener.start()

def check_message_type(cur_message): # Method to find message type
    cur_message = str(cur_message.encode('ascii','ignore'))
    if '/Volumes/' in cur_message:
        return 1
    elif 'lunch' in cur_message.lower():
        return 2
    elif 'hungry' in cur_message.lower():
        return 2
    elif 'food' in cur_message.lower():
        return 2
    elif 'watch' in cur_message.lower():
        return 3
    else:
        return 4

def lunch_answer():
    lunch_message = 'You should have ' +str(lunch_options[random.randint(0,9)]) + ' for lunch.'
    send_to_slack(lunch_message)

def video_handler_type(cur_message):
    if '.mov' in cur_message[1]:
        if 'cuts' in cur_message[1] and 'scenes' not in cur_message[1]:
            return 1
        elif 'ae' in cur_message[1]:
            return 2
        elif 'scenes' in cur_message[1]:
            return 2
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
            if video_handler_type(cur_message) == 1:
                print 'This is definitely a cut.'
                project,fn = file_finder(cur_message[1])
                try:
                    send_to_slack('Encoding that cut for ' +project)
                    print "This is the source file: " +cur_message[1]
                    print "This is the trimmed filename: " +trim(fn)
                    print "This is the project name: " +project
                    print "This is the dropbox folder it will go into: " +fuzzy_dropbox(project)
                    encode = threading.Thread(target=encode_1080(cur_message[1],trim(fn),fuzzy_dropbox(project)))
                    encode.daemon = True
                    encode.start()
                    
                except:
                    print 'Ran into some issues encoding your file.'
                    
            elif video_handler_type(cur_message) == 2:
                print 'This is definitely a scene.'
      
        elif check_message_type(cur_message[1]) == 2: # Call the lunch method if the current message contains something related to lunch or food
            lunch_answer()
            
        elif check_message_type(cur_message[1]) == 3: # Call the directory watchdog to keep an eye on any outcoming shots
            project = 'Density'
            directory_watchdog(server_directory+project)
        elif check_message_type(cur_message[1]) == 4:
            #send_to_slack("I can't handle this type of input yet")
            pass
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
        time.sleep(1)
            
controller()
