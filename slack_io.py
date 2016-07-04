#listen to slack
from slackclient import SlackClient

##### DECLARATIONS #####

global sc
global chan

token = "xoxb-36774633444-7WG8kaLpG23HeRcLjrix7RA4"# found at https://api.slack.com/web#authentication
sc = SlackClient(token)

chan = "C06PTC83B" #LIVE OUTPUT
pp_key = 'lry3zo9bnw0539y'
app_secret = '5292p7am7dnpdfq'
access_token = 'rnDrBIxEFbAAAAAAAAAH'


def send_to_slack(slackput):
    try:
        sc.rtm_send_message(chan,slackput)
    except:
        print "Something happened while attempting to send to slack"

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