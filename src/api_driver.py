from keyword import kwlist

from atproto import AtUri, models
from atproto_client import Client
import asyncio

from atproto_client.models.string_formats import DateTime

from profile import ProfileData
from datetime import datetime
import json
import os
import re

from atproto_client.request import Response

from src.endpoints import delete_skeet


#from post_data import PostData

class Driver:
    """
        class to wrap methods for generating output files after parsing
        """

    @staticmethod
    def perform_get_skeets(client: Client):
        latest = []
        id = 0
        replies = 0
        # try:
        posts = client.app.bsky.feed.post.list(client.me.did, limit=50)
        for uri, post in posts.records.items():
            #likes=0
            replies=0
            print("retrieving post - uri : " + uri)
            likes = Driver().find_skeet_likes(client, uri)
            # print("replies : " + str(post.reply))

            latest.append({'id': id, 'txt': post.text, 'time': post.created_at, 'uri': uri, 'likes': likes, 'replies': replies}) #post.likes_count})
            id = id + 1
        # except Exception as e: print(e)
        return latest

    @staticmethod
    def perform_get_skeets_from(client: Client, from_date: str, until_date: str):
        latest = []
        id = 0
        if (until_date == 'Unknown' or from_date == 'Unknown'):
            return latest
        until_date += "T00:00:00.000Z"
        from_date += "T00:00:00.000Z"
        print("from date  : " + str(from_date))
        print("until date  : " + str(until_date))
        searched_posts = client.app.bsky.feed.search_posts({'q':'a','author': client.me.did,'since': str(from_date), 'until': str(until_date), 'limit': 50})
        try:
            for postView in searched_posts.posts:
                replies = 0
                # if str(postView.reply) == 'None':
                #     replies = 0
                # else:
                #     replies = 1
                latest.append(
                     {'id': id, 'txt': postView.record.text, 'time': postView.record.created_at, 'uri': postView.uri, 'likes': postView.like_count, 'reply': replies})  # post.likes_count})
                id = id + 1
        except Exception as e: print(e)
        print(str(latest))
        return latest

    @staticmethod
    def perform_get_inactive_skeets(client: Client, limit_length: int):
        latest = []
        id = 0
        replies = 0
        # try:
        posts = client.app.bsky.feed.post.list(client.me.did, limit=limit_length)
        for uri, post in posts.records.items():
            l_s = Driver().find_skeet_likes(client, uri)
            try:
                likes = int(l_s)
            except ValueError:
                likes = -1
            if likes == 0:
                # if str(post.reply) == 'None':
                #     replies = 0
                # else:
                #     replies = 1
                latest.append(
                    {'id': id, 'txt': post.text, 'time': post.created_at, 'uri': uri, 'likes': likes, 'reply': replies})  # post.likes_count})
                id = id + 1
        # except Exception as e: print(e)
        return latest

    @staticmethod
    def perform_delete_inactive_skeets(client: Client, limit_length: int):
        latest = []
        id = 0
        # try:
        print("deleting inactive skeets")
        posts = client.app.bsky.feed.post.list(client.me.did, limit=limit_length)
        for uri, post, likes, replies in posts.records.items():
            print("retrieving post - uri : " + uri)
            #l_s = Driver().find_skeet_likes(client, uri)
            latest.append(
                {'id': id, 'txt': post.text, 'time': post.created_at, 'uri': uri,
                 'likes': likes, 'replies': replies})  # post.likes_count})
            # try:
            #     likes = int(l_s)
            # except ValueError:
            #     likes = -1
            #     print('Please enter an integer')
            # if likes == 0:
            #     print(" permanently deleting uri : " + str(uri))
            #     latest.append(
            #         {'id': id, 'txt': post.text, 'time': post.created_at, 'uri': uri,
            #          'likes': likes})  # post.likes_count})
            #     id = id + 1
            #     delete_skeet(str(uri))
        # except Exception as e: print(e)
        return latest

    @staticmethod
    def find_single_skeet(client: Client, uri):
        return client.app.bsky.feed.post.get(client.me.did, AtUri.from_str(uri).rkey)

    @staticmethod
    def check_notifications(client: Client):
        print('Checking notifications...')
        notifications = []
        # save the time in UTC when we fetch notifications
        last_seen_at = client.get_current_time_iso()

        response = client.app.bsky.notification.list_notifications()
        for notification in response.notifications:
            if not notification.is_read:
                print(f'Got new notification! Type: {notification.reason}; from: {notification.author.did}')
                notifications.append({'author': notification.author.display_name, 'description': notification.reason})
        # mark notifications as processed (isRead=True) uncomment if we decide to update this later
        # client.app.bsky.notification.update_seen({'seen_at': last_seen_at})
        print('Successfully process notification. Last seen at:', last_seen_at)
        return notifications

    @staticmethod
    def create_skeet(client: Client, skeet_text):
        post_record = models.AppBskyFeedPost.Record(text=skeet_text,
                                                    created_at=client.get_current_time_iso())
        new_post = client.app.bsky.feed.post.create(client.me.did, post_record)
        print("Created new skeet with the text : " + post_record.text + " : the new uri :" + new_post.uri)
        uri = new_post.uri
        return uri

    @staticmethod
    def delete_skeet(client: Client, uri: str):
        print("Deleting the post at the uri : " + uri)
        deleted_post = client.app.bsky.feed.post.delete(client.me.did, AtUri.from_str(uri).rkey)
        print(deleted_post)

    @staticmethod
    def find_skeet_likes(client: Client, uri: str):
        count = 0
        print("Calling feed.post.get")
        likes = client.app.bsky.feed.get_likes(params={'uri': uri, 'limit': 100})
        like_list = likes['likes']
        for like in like_list:
            count = count + 1
        return count

    @staticmethod
    def get_replied_skeetss(client: Client, author: str):
        cursor = None
        replies = []
        return replies

    @staticmethod
    def get_follows(client: Client, author: str):
        cursor = None
        following = []
        while True:
            fetched = client.app.bsky.graph.get_follows(params={'actor': author, 'cursor': cursor})
            following = following + fetched.follows
            if not fetched.cursor:
                break
            cursor = fetched.cursor
        following_list = []
        for actor in following:
            following_list.append({'name': actor.display_name, 'handle': actor.handle, 'description': actor.description, 'avatar' :actor.avatar})
        return following_list

    @staticmethod
    def get_followed(client: Client, author: str):
        cursor = None
        following = []
        while True:
            fetched = client.app.bsky.graph.get_follows(params={'actor': author, 'cursor': cursor})
            following = following + fetched.follows
            if not fetched.cursor:
                break
            cursor = fetched.cursor
        following_list = []
        for actor in following:
            following_list.append({'name': actor.display_name, 'handle': actor.handle, 'description': actor.description,
                                   'avatar': actor.avatar})
        return following_list

    @staticmethod
    async def create_following_json(client: Client, author: str, filename):
        following = Driver().get_following(client, author)
        try:
            print("attempting to remove file : " + filename)
            os.remove(filename)
        except OSError:
            pass
        print("writing following list to jason file len: " + str(len(following)))
        with open(filename, 'w') as f:
            json.dump(following, f, indent=4)
        print("file : " + filename + " : finished")

    @staticmethod
    def get_followers(client: Client, author: str):
        cursor = None
        followers = []
        while True:
            fetched = client.app.bsky.graph.get_followers(params={'actor': author, 'cursor': cursor})
            followers = followers + fetched.followers
            if not fetched.cursor:
                break
            cursor = fetched.cursor
        followers_list = []
        for actor in followers:
            followers_list.append({'name': actor.display_name, 'handle': actor.handle, 'description': actor.description,
                                   'avatar': actor.avatar})
        return followers_list

    @staticmethod
    async def create_follower_json(client: Client, author: str, filename):
        followers = Driver().get_followers(client, author)
        try:
            print("attempting to remove file : " + filename)
            os.remove(filename)
        except OSError:
            pass
        print("writing follows list to jason file len: " + str(len(followers)))
        with open(filename, 'w') as f:
            json.dump(followers, f, indent=4)
        print("file : " + filename + " : finished")

    @staticmethod
    def find_skeet_thread(client: Client, uri: str):
        count = 0
        threads = client.app.bsky.feed.get_post_thread(params={'uri': uri})
        replies = threads.thread.replies
        print("thread" + str(replies))
        for reply in replies:
            count = count + 1
        return count

    @staticmethod
    def get_feed_list(client: Client, author: str):
        feed_list = []
        #feeds = client.app.bsky.feed.get_author_feed(params={'author': author})
        feeds = client.app.bsky.feed.get_actor_feeds(params={'actor': author})
        print("called get feeds list " + str(feeds))
        for feed in feeds:
            feed_list.append(feed)
        return feed_list

    @staticmethod
    def get_timeline(client: Client, author: str):
        timeline = []
        id = 0
        # feeds = client.app.bsky.feed.get_author_feed(params={'author': author})
        feed_list = client.app.bsky.feed.get_timeline(params={'actor': author})
        print("called get timeline")
        for feed_view in feed_list.feed:
            action = 'New Post'
            if feed_view.reason:
                action_by = feed_view.reason.by.handle
                action = f'Reposted by @{action_by}'

            post = feed_view.post.record
            author = feed_view.post.author
            likes = feed_view.post.like_count
            uri = feed_view.post.uri
            replies = feed_view.post.reply_count

            #print(f'[{action}] {author.display_name}: {post.text}')
            #timeline.append(post)
            timeline.append({'id': id, 'author': author.avatar, 'txt': str(post.text), 'likes': likes, 'replies': replies, 'time': str(post.created_at)})
            id = id + 1

        print("returning timeline object")
        return timeline

    @staticmethod
    def get_profile_data(client: Client, profile_uri: str):
        print("retrieving date for profile :" + profile_uri)
        p = client.get_profile(actor=profile_uri)
        profile_obj = ProfileData(p.display_name, p.description, p.avatar, p.banner, int(p.followers_count),
                                  int(p.follows_count), p.posts_count, p.created_at)
        return profile_obj

    def get_deleted(self, client: Client):
        pass
        # print("calling get deleted posts")
        # driver_object.get_deleted(account, token)

    @staticmethod
    def post_with_image(client: Client, post_text: str, image_path: str):
        #print("image path inside post_with_image is : " + image_path)
        status = True
        # Post with an image
        try:
            with open(image_path, 'rb') as f:
                img_data = f.read()
                client.send_image(text=post_text, image=img_data, image_alt="Teat image description")
        except:
            print("Failure posting with image")
            status = False
        return status
