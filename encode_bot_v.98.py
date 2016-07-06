#version .98 - now re-connects up to 10 times
import sys,subprocess,time,os
from slackclient import SlackClient
import dropbox
from fuzzywuzzy import fuzz,process
import csv
import sandwich
import threading

#responses set-up
#reader = csv.reader(open('responses.csv', 'r'))
#qanda = {}
#for row in reader:
#   k, v = row
#   qanda[k] = v

CRF_VALUE = '19' # controls the quality of the encode
PROFILE = 'high422' # h.264 profile
PRESET = 'fast' # encoding speed:compression ratio
TUNE = 'film' # tune setting
FFMPEG_PATH = '/usr/local/bin/ffmpeg' # path to ffmpeg bin
THREADS = '8' # of threads to use
OUTPUTDIR = '/Users/sanvidpro/Dropbox/encoder_output/' # Output directory
SCALER_540 = "scale=-1:540, scale=trunc(iw/2)*2:540" # 540 Scale settings
SCALER_1080 = "scale=-1:1080, scale=trunc(iw/2)*2:1080" # 1080 Scale settings

# DECLARATIONS
global sc
global dropbox_path
global chan
global src
global output

dropbox_path = '/Users/sanvidpro/Dropbox/'
#chan = "C12PL8TSS" #TEMP SLACK
chan = "C06PTC83B" #LIVE OUTPUT
evt = ''
src = ''

#Define SLACKBOT token and Dropbox API
token = "xoxb-36774633444-7WG8kaLpG23HeRcLjrix7RA4"# found at https://api.slack.com/web#authentication
sc = SlackClient(token)
app_key = 'xxxxx'
app_secret = 'xxxxx'
access_token = 'xxxxx'
dropbox_client = dropbox.client.DropboxClient(access_token)


def file_finder(link):
    link_list = link.split('/')
    project = link_list[4]
    fn = link_list[-1]
    send_to_slack("Looks like this is for the "+str(project) +" project.")
    return project,fn

def fuzzy(project):
    direct_list = os.listdir(dropbox_path)
    dir_temp = process.extract(project,direct_list,limit=1)
    directory = dir_temp[0]
    directory = directory[0]
    print directory
    return directory

def trim(src):
    fn = str(src)
    fn.split('.')
    fn = fn[:-4]
    fn = fn.translate(None,"[\(\)\{\}<>&%!@#$^*]")
    print fn
    return fn
    
def encode_540(video,directory,fn):
    output = dropbox_path + directory + "/cuts/" + fn + "-540.mov"
    dropbox_output = directory + "/cuts/" + fn + "-540.mov"
    print output
    try:
        subprocess.call([FFMPEG_PATH, '-i', video, '-c:v', 'libx264', '-tune', TUNE, '-pix_fmt', 'yuv420p', '-preset', PRESET, '-profile:v', PROFILE, '-vf', SCALER_540, '-crf', CRF_VALUE, '-c:a', 'libfdk_aac', '-b:a', '192k', '-threads', THREADS, output])
        return dropbox_output
    except:
        print "failure"
        
def encode_1080(video,directory,fn):
    output = dropbox_path + str(directory) + "/cuts/" + fn + "-1080.mov"
    dropbox_output = directory + "/cuts/" + fn + "-1080.mov"
    print output
    try:
        subprocess.call([FFMPEG_PATH, '-i', video, '-c:v', 'libx264', '-tune', TUNE, '-pix_fmt', 'yuv420p', '-preset', PRESET, '-profile:v', PROFILE, '-vf', SCALER_1080, '-crf', CRF_VALUE, '-c:a', 'libfdk_aac', '-b:a', '192k', '-threads', THREADS, output])
        return dropbox_output
    except:
        print "failure"

def encode_simple(video,directory,fn):
    output = dropbox_path + str(directory) + "/cuts/_scenes/" + fn + "-1080.mov"
    dropbox_output = directory + "/cuts/_scenes/" + fn + "-1080.mov"
    db_path_plain = directory +"/cuts/_scenes"
    print db_path_plain
    try:
        os.makedirs(db_path_plain)
    except OSError:
        if not os.path.isdir(db_path_plain):
            raise
    print output
    try:
        subprocess.call([FFMPEG_PATH, '-i', video, '-c:v', 'libx264', '-tune', TUNE, '-pix_fmt', 'yuv420p', '-preset', PRESET, '-profile:v', PROFILE, '-vf', SCALER_1080, '-crf', CRF_VALUE, '-c:a', 'libfdk_aac', '-b:a', '192k', '-threads', THREADS, output])
        return dropbox_output
    except:
        print "failure"

def update_airtable(project,cut):
    record_dict = sandwich.get_record_endpoints("Sandwich Post Projects")
    dictlist = []
    dictlist = record_dict.keys()
    air_project = process.extract(project,dictlist,limit=2)
    air_project = air_project[0]
    air_project = air_project[0]
    try:
        sandwich.updateLatestcut(air_project,cut)
    except:
        send_to_slack("Was unable to update Airtable")

def encode_options(src,directory,fn):
    evt = ""
    while True:
        new_evts = sc.rtm_read()
        for evt in new_evts:
            if "type" in evt:
                if evt["type"] == "message" and "text" in evt:
                    message = evt["text"]
                    if "540" in message:
                        try:
                            print "540"
                            send_to_slack("Encoding that for you now, wait until complete to submit next file.")
                            dropbox_output = encode_540(src,directory,fn)
                            return dropbox_output
                        except:
                            send_to_slack("Something went wrong")
                    elif "1080" in message:
                        try:
                            print "1080"
                            send_to_slack("Encoding that for you now, wait until completed to submit next file.")
                            dropbox_output = encode_1080(src,directory,fn)
                            return dropbox_output
                        except:
                            send_to_slack("Something went wrong")
        time.sleep(1)
                            
def send_to_slack(slackput):
    try:
        sc.rtm_send_message(chan,slackput)
    except:
        print "Something happened while attempting to send to slack"

for i in range(100):
    for attempt in range(10):
        try:
            if sc.rtm_connect():
                while True:
                    new_evts = sc.rtm_read()
                    for evt in new_evts:
                        print(evt)
                    if "type" in evt:
                        if evt["type"] == "message" and "text" in evt:
                            message = evt["text"]
                            if "/Volumes/Sandwich" in message:
                                send_to_slack("Message received, processing...")
                                src = message
                                project,fn = file_finder(message)
                                directory = fuzzy(project)
                                if "cuts" in src and "scenes" not in src:
                                    send_to_slack("Would you like a 540 or a 1080?")
                                    try:
                                        final_link = dropbox_client.share(encode_options(src,directory,trim(fn)),short_url=True)
                                        print final_link
                                        time.sleep(1)
                                        send_to_slack("Encoding complete and available here \n" +final_link['url'])
                                        final_link = final_link['url']
                                        update_airtable(project,final_link)
                                    except:
                                        send_to_slack("All kinds of failure happened, give it another shot maybe")
                                else:
                                    send_to_slack("Encoding that clip for you!")
                                    try:
                                        final_link = dropbox_client.share(encode_simple(src,directory,trim(fn)),short_url=True)
                                        send_to_slack("Encoding complete and available here \n" +final_link['url'])
                                    except:
                                        send_to_slack("Something went very wrong")
                            #else:
                                #question = message
                                #if question in qanda:

                    time.sleep(1)
            else:
                print "Connection Failed, invalid token?"
        except:
            print "Lost connection to Slack"
            break
