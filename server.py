# -*- coding: utf-8 -*-
import urllib.request
import json
import datetime
import time
import sys
import os
import re
import tweepy

consumer_key = ''
consumer_secret = ''
access_token = ''
access_secret = ''

image_path = './image'

my_id = None
my_name = None
my_screen_name = None

command_regex = re.compile(r'\(([^\)]*)\)')

class listener(tweepy.StreamListener):
    def __init__(self, api):
        self.api = api

    def on_data(self, data):
        status = json.loads(data)

        if status.get('friends'):
            return True
        if status.get('direct_message'):
            return True
        if status.get('limit'):
            return True
        if status.get('disconnect'):
            return True
        if status.get('warning'):
            return True
        if status.get('delete'):
            return True

        #print(json.dumps(status))

        # If favorited/unfavorited my tweet, exit the function
        if status.get('target_object'):
            if status.get('target_object').get('user'):
                if status.get('target_object').get('user').get('screen_name') == my_id:
                    print('3')
                    return True

        # Only process favorite data
        if not status.get('event') == 'favorite':
            return True

        print('Favorited - ' + str(status.get('target_object').get('id')))

        media_list = []
        file_list = []
        today_date = datetime.datetime.now().strftime("%Y%m%d")

        if len(status.get('target_object').get('extended_entities').get('media')) > 0:
            media_list = status.get('target_object').get('extended_entities').get('media')

        if len(media_list) > 0:
            for media in media_list:
                # Only download the photo
                if not media.get('type') == 'photo':
                    continue

                file_name = today_date + '_' + str(media.get('id')) + '_wait'
                urllib.request.urlretrieve(media.get('media_url'), os.path.join(image_path, file_name))
                file_list.append(file_name)

        print('File saved. wait - ' + str(status.get('target_object').get('id')))

        # Wait the confirm the favorite. Prevent to saving media of unfavorited tweets.
        time.sleep(5)

        print('5 second outed - ' + str(status.get('target_object').get('id')))

        for file in file_list:
            try:
                os.rename(os.path.join(image_path, file), os.path.join(image_path, file.replace('_wait', '')))
            except:
                raise
                print('Unfavorited tweet. Will not process - ' + str(status.get('target_object').get('id')))
                return True

        print('File renamed. unfavorite - ' + str(status.get('target_object').get('id')))

        # Unfavorite the tweet
        try:
            self.api.destroy_favorite(status.get('target_object').get('id'))
            print('Unfavorited - ' + str(status.get('target_object').get('id')))
        except:
            print('Error. The tweet is unfavorited - ' + str(status.get('target_object').get('id')))

            for file in file_list:
                try:
                    os.remove(os.path.join(image_path, file.replace('_wait', '')))
                except:
                    pass

            return True


    def on_error(self, status):
        if status == 420:
            print('Exceed Limited attempt')
            return False

        print(status)

if __name__ == '__main__':
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)

    account_data = api.me()

    my_id = account_data.id
    my_name = account_data.name
    my_screen_name = account_data.screen_name

    print("System Start!")

    stream = tweepy.Stream(auth=auth, listener=listener(api))

    while True:
        try:
            stream.userstream(_with='user')
        except KeyboardInterrupt:
            break
            sys.exit(0)
        except AttributeError as e:
            print("AttributeError Occurred", e.message)
        except ValueError as e:
            print("ValueError Occurred", e.message)
        except IOError as e:
            print("IOError Occurred", e.message)

    stream.disconnect()
