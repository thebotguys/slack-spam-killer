"""
    Antispam script
    Free forever from specified spam with this customizable script.

    AUTHOR: Alessandro Sanino <saninoale@gmail.com>
"""

import time
import os

from slackclient import SlackClient

REPO_URL = 'https://github.com/AlessandroSanino1994/slack-spam-killer'
TOKEN = os.environ['BOT_TOKEN']
ADMIN_TOKEN = os.environ['ADMIN_LEGACY_TOKEN']
BAN_SIGNALS_CHANNEL = os.environ['BAN_SIGNALS_CHANNEL_ID']
BLOCKED_KEYWORDS = os.environ['BLOCKED_KEYWORDS'].split(';')

LOVE_EMOJIS = ['heart', '+1', 'beers', 'clap']
APPROVED_EMOJI = 'white_check_mark'

#used to access admin feature, must be a legacy token.
#allows chat.delete
ADMIN_CLIENT = SlackClient(ADMIN_TOKEN)

#bot user, sends messages.
SLACK_CLIENT = SlackClient(TOKEN)

def handle_request(rtm_event):
    """ Handles a single event get from RTM api and responds """

    if ('channel' in rtm_event and
            'text' in rtm_event and
            rtm_event.get('type') == 'message'):
        text, user = rtm_event['text'], rtm_event['user']
        msg = text.lower()
        print 'Getting user info...'
        infos = SLACK_CLIENT.api_call(
            'users.info', user=user)['user']
        print 'user info got'
        user, username = infos['id'], infos['name']
        is_adm, channel = infos['is_admin'], rtm_event['channel']
        timestamp = rtm_event['ts']
        # print str(event)
        blocked = False
        for item in BLOCKED_KEYWORDS:
            if item in msg:
                # print SLACK_CLIENT.api_call('channels.info', channel=rtm_event['channel'])
                if is_adm is False:
                    blocked = True
                    print "found spam: <@" + str(username) + "> " + str(text) + " on " + \
                    str(channel) + '. Removing...'
                    print ADMIN_CLIENT.api_call(
                        'chat.delete', channel=channel, ts=timestamp)
                    print 'message removed, posting message to ' + BAN_SIGNALS_CHANNEL + \
                        'channel...'
                    print SLACK_CLIENT.api_call('chat.postMessage', channel=BAN_SIGNALS_CHANNEL,
                                                text='<@' + str(user) + '>' + \
                                                ' is spamming, terminate him',
                                                as_user='true')
                    print 'message sent'
        if not blocked:
            if REPO_URL in text:
                for emoji in LOVE_EMOJIS:
                    print "my url detected, sending reaction..."
                    print SLACK_CLIENT.api_call('reactions.add', channel=channel,
                                                name=emoji, timestamp=timestamp)
                print "sent reaction: " + LOVE_EMOJIS
            elif 'http' in text or 't.me' in text or 'telegram.me' in text:
                print "msg ok, sending reaction..."
                print SLACK_CLIENT.api_call('reactions.add', channel=channel,
                                            name=APPROVED_EMOJI, timestamp=timestamp)
                print "sent reaction: " + APPROVED_EMOJI

if __name__ == "__main__":
    print 'Connecting...'
    if SLACK_CLIENT.rtm_connect():
        print 'Connected to Slack API'
        while True:
            EVENTS = SLACK_CLIENT.rtm_read()
            for event in EVENTS:
                handle_request(event)
            time.sleep(1)
    else:
        print 'Connection failed, invalid token?'
