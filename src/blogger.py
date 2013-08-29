#!/usr/bin/python
#
# Copyright 2012 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import httplib2
import sys

import logging
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run, run_flow
import argparse
from oauth2client import tools
import json

# The scope URL for read/write access to a user's blogger data
scope = 'https://www.googleapis.com/auth/blogger'

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def OAuth_Authenticate(client_id, client_secret):
    """@todo: Docstring for OAuth_Authenticate

    :client_id: Client ID - Get it from google API console
    :client_secret: Client secret - same as above
    :returns: service object

    """
    # Create a flow object. This object holds the client_id, client_secret, and
    # scope. It assists with OAuth 2.0 steps to get user authorization and
    # credentials.
    flow = OAuth2WebServerFlow(client_id, client_secret, scope)
    # Create a Storage object. This object holds the credentials that your
    # application needs to authorize access to the user's data. The name of the
    # credentials file is provided. If the file does not exist, it is
    # created. This object can only hold credentials for a single user, so
    # as-written, this script can only handle a single user.
    storage = Storage('credentials.dat')
  
    # The get() function returns the credentials for the Storage object. If no
    # credentials were found, None is returned.
    credentials = storage.get()
  
    # If no credentials are found or the credentials are invalid due to
    # expiration, new credentials need to be obtained from the authorization
    # server. The oauth2client.tools.run() function attempts to open an
    # authorization server page in your default web browser. The server
    # asks the user to grant your application access to the user's data.
    # If the user grants access, the run() function returns new credentials.
    # The new credentials are also stored in the supplied Storage object,
    # which updates the credentials.dat file.
  
    if credentials is None or credentials.invalid:
        credentials = run(flow, storage)
  
    # Create an httplib2.Http object to handle our HTTP requests, and authorize it
    # using the credentials.authorize() function.
    http = httplib2.Http()
    http.disable_ssl_certificate_validation = True
    http = credentials.authorize(http)
  
    # The apiclient.discovery.build() function returns an instance of an API service
    # object can be used to make API calls. The object is constructed with
    # methods specific to the blogger API. The arguments provided are:
    #   name of the API ('blogger')
    #   version of the API you are using ('v3')
    #   authorized httplib2.Http() object that can be used for API calls
    service = build('blogger', 'v3', http=http)
    return service

def getBlog(service, blogId = None, blogUrl = None, posts = 0):
    if blogUrl:
        request = service.blogs().getByUrl(url = blogUrl)
    else:
        request = service.blogs().get(blogId=blogId, maxPosts=posts)
    return request.execute()

def getPosts(service, blogId, postId = None, query=None,  labels = "", maxResults = 1 ):
    if postId:
        request = service.posts().get(blogId, postId)
    elif query:
        request = service.posts().search(blogId = blogId, q = query )
    else:
        request = service.posts().list(blogId = blogId, labels = labels, maxResults = maxResults)
    return request.execute()

#def slugify(s):
    #from text_unidecode import unidecode
    #import re
    #slug = unidecode(s)
    #slug = slug.encode('ascii', 'ignore').lower()
    #slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    #slug = re.sub(r'[-]+', '-', slug)
    #return slug

def post(service, blogId, title, content, labels, isDraft = True ):
    #url = slugify(title) + ".html"
    blogPost = { "labels": labels.split(","), "content": content, "title":title }
    req = service.posts().insert(blogId = blogId, body= blogPost)
    return req.execute()

def deletePost(service, blogId, postId):
    req = service.posts().delete(blogId = blogId, postId = postId)
    return req.execute()

def updatePost(service, blogId, postId, title = None, content = None, labels = None, isDraft = True ):
    # Permalink cannot be updated...
    #from datetime import date
    #today = date.today()
    #url = "/{}/{}/{}".format(today.year, today.month, slugify(title) + ".html")
    blogPost = {}
    if title:
        blogPost['title'] = title
    if content: 
        blogPost['content'] = content
    if labels:
        blogPost['labels'] = labels.split(",")
    req = service.posts().patch(blogId = blogId, postId = postId, body= blogPost)
    return req.execute()

def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--clientid", help = "Your API Client id", default="132424086208.apps.googleusercontent.com")
    parser.add_argument("-s","--secret", help = "Your API Client secret", default="DKEk2rvDKGDAigx9q9jpkyqI")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--blogid", help = "Your blog id", default="7642453")
    group.add_argument("--url", help = "Your blog url")

    subparsers = parser.add_subparsers(help = "sub-command help", dest="command")

    get_parser = subparsers.add_parser("get", help= "list posts")
    group = get_parser.add_mutually_exclusive_group()
    group.add_argument("-p","--postId", help = "the post id")
    group.add_argument("-l","--labels", help = "comma separated list of labels")
    group.add_argument("-q","--query", help = "search term")
    get_parser.add_argument("-c","--count", type=int, help = "count", default=10)

    post_parser = subparsers.add_parser("post", help= "create a new post")
    post_parser.add_argument("-t", "--title", help = "Post title")
    post_parser.add_argument("-c","--content", help = "Post content")
    post_parser.add_argument("-l","--labels", help = "comma separated list of labels")

    delete_parser = subparsers.add_parser("delete", help= "delete a post")
    delete_parser.add_argument("postId", help = "the post to delete")

    update_parser = subparsers.add_parser("update", help= "update a post")
    update_parser.add_argument("postId", help = "the post to update")
    update_parser.add_argument("-t", "--title", help = "Post title")
    update_parser.add_argument("-c","--content", help = "Post content")
    update_parser.add_argument("-l","--labels", help = "comma separated list of labels")

    args = parser.parse_args()


    
    client_id = args.clientid
    client_secret = args.secret
    blog_id = args.blogid
    try:
       service = OAuth_Authenticate(client_id, client_secret)
       #blog = getBlog(service, blog_id)
       #print printJson(blog)

       if args.url:
           blog = getBlog(service, blogUrl = args.url)
           printJson(blog)
           blog_id =  blog['id']
       posts = {}

       if args.command == "post":
           newPost = post(service, blog_id, args.title, args.content, args.labels)
           print newPost['id']

       if args.command == 'delete':
            deletePost(service, blog_id, args.postId)

       if args.command == 'update':
            updatePost(service, blog_id, args.postId, args.title, args.content, args.labels)

       if args.command == "get":
           if args.postId:
               posts = getPosts(service, blog_id, postId = args.postId)
           elif args.query:
               posts = getPosts(service, blog_id, query = args.query, maxResults = args.count)
           else:
               posts = getPosts(service, blog_id, labels =args.labels, maxResults = args.count)
           print printJson(posts)

    except AccessTokenRefreshError:
        # The AccessTokenRefreshError exception is raised if the credentials
        # have been revoked by the user or they have expired.
        print ('The credentials have been revoked or expired, please re-run'
            'the application to re-authorize')

def printJson(data):
    """@todo: Docstring for printJson

    :data: @todo
    :returns: @todo
    """
    logger.debug(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))

if __name__ == '__main__':
    main()
