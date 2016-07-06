#listen to slack
from slackclient import SlackClient

with open('../token.txt', 'r') as token_file:
    read_data = token_file.read()
token_file.closed

##### DECLARATIONS #####

global sc
global chan

token = read_data
sc = SlackClient(token)

chan = "C06PTC83B" #LIVE OUTPUT
app_key = 'lry3zo9bnw0539y'
app_secret = '5292p7am7dnpdfq'
access_token = 'rnDrBIxEFbAAAAAAAAAH'


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
