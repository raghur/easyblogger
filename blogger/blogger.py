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

import os
import os.path
import urlparse
import re
import sys

import logging

import argparse
import pypandoc
import json
import httplib2

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

logger = logging.getLogger()
logging.basicConfig()


class EasyBlogger(object):

    @staticmethod
    def _parseLabels(labels):
        if not labels:
            return None

        if isinstance(labels, basestring):
            if labels.strip() == "":
                return None
            lbl = [i.strip() for i in labels.split(",") if i.strip()]
            return lbl if lbl else None
        else:
            lbl = [i.strip() for i in labels if i.strip()]
            return lbl if lbl else None

    def __init__(self, clientId, clientSecret, blogId=None, blogUrl=None):
        self.clientId = clientId
        self.clientSecret = clientSecret
        self.service = None
        self.blogId = blogId
        self.blogUrl = blogUrl
        self.converter = pypandoc

    def _OAuth_Authenticate(self):
        """@todo: Docstring for OAuth_Authenticate

        :client_id: Client ID - Get it from google API console
        :client_secret: Client secret - same as above
        :returns: service object

        """
        if self.service:
            return self.service
        # The scope URL for read/write access to a user's blogger data
        scope = 'https://www.googleapis.com/auth/blogger'

        # Create a flow object. This object holds the client_id, client_secret, and
        # scope. It assists with OAuth 2.0 steps to get user authorization and
        # credentials.
        flow = OAuth2WebServerFlow(self.clientId, self.clientSecret, scope)
        # Create a Storage object. This object holds the credentials that your
        # application needs to authorize access to the user's data. The name of the
        # credentials file is provided. If the file does not exist, it is
        # created. This object can only hold credentials for a single user, so
        # as-written, this script can only handle a single user.
        storage = Storage(os.path.expanduser('~/.easyblogger.credentials'))

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
        self.service = build('blogger', 'v3', http=http)
        return self.service

    def _setBlog(self):
        if self.blogId:
            return
        service = self._OAuth_Authenticate()
        request = service.blogs().getByUrl(url=self.blogUrl)
        blog = request.execute()
        self.blogId = blog['id']

    def getPosts(self, postId=None, query=None, labels="", maxResults=1):
        self._setBlog()
        try:
            service = self._OAuth_Authenticate()
            if postId:
                request = service.posts().get(
                    blogId=self.blogId, postId=postId)
                post = request.execute()
                return {"items": [post]}
            elif query:
                request = service.posts().search(blogId=self.blogId, q=query)
            else:
                request = service.posts().list(
                    blogId=self.blogId,
                    labels=labels,
                    maxResults=maxResults)
            return request.execute()
        except HttpError as he:
            if he.resp.status == 404:
                return {"items": []}
            raise

    # def slugify(s):
        #from text_unidecode import unidecode
        #import re
        #slug = unidecode(s)
        #slug = slug.encode('ascii', 'ignore').lower()
        #slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
        #slug = re.sub(r'[-]+', '-', slug)
        # return slug

    def _getMarkup(self, content, fmt):
        raw = content
        if hasattr(content, 'read'):
            raw = content.read()
        html = raw
        if fmt != "html":
            html = self.converter.convert(raw, 'html', format=fmt)
        return html

    def post(self, title, content, labels, isDraft=True, fmt="html"):
        self._setBlog()
        #url = slugify(title) + ".html"
        service = self._OAuth_Authenticate()
        markup = self._getMarkup(content, fmt)
        blogPost = {"content": markup, "title": title}
        blogPost['labels'] = EasyBlogger._parseLabels(labels)

        req = service.posts().insert(blogId=self.blogId, body=blogPost)
        return req.execute()

    def deletePost(self, postId):
        self._setBlog()
        service = self._OAuth_Authenticate()
        req = service.posts().delete(blogId=self.blogId, postId=postId)
        return req.execute()

    def updatePost(self, postId, title=None,
                   content=None, labels=None, isDraft=True, fmt="html"):
        # Permalink cannot be updated...
        #from datetime import date
        #today = date.today()
        #url = "/{}/{}/{}".format(today.year, today.month, slugify(title) + ".html")
        self._setBlog()
        service = self._OAuth_Authenticate()
        blogPost = {}
        if not (title or content or labels):
            raise ValueError(
                "At least one of title, content or labels is required")
        if title:
            blogPost['title'] = title
        if content:
            blogPost['content'] = self._getMarkup(content, fmt)
        blogPost['labels'] = EasyBlogger._parseLabels(labels)
        req = service.posts().patch(
            blogId=self.blogId,
            postId=postId,
            body=blogPost)
        return req.execute()


class ContentArgParser(object):
    rePostId = re.compile("^\s*postId\s*:\s*(\d+)\s*$", re.I | re.M)
    reLabels = re.compile("^\s*labels\s*:\s*([\w\d\- ,_]*)\s*$", re.I | re.M)
    reTitle = re.compile("^\s*title\s*:\s*(.+)\s*$", re.I | re.M)
    reFormat = re.compile("^\s*format\s*:\s*(.+)\s*$", re.I | re.M)
    rePostIdUpdate = re.compile("^(\s*postId\s*:)", re.I | re.M)

    def __init__(self, theFile, open=open):
        self.theFile = theFile
        self.open = open

    def _inferArgsFromContent(self):
        fileContent = self.theFile.read()

        self.postId = ContentArgParser.rePostId.search(fileContent)
        if self.postId:
            self.postId = self.postId.group(1).strip()

        self.labels = ContentArgParser.reLabels.search(fileContent)
        if self.labels:
            self.labels = self.labels.group(1).strip()

        self.title = ContentArgParser.reTitle.search(fileContent)
        if self.title:
            self.title = self.title.group(1).strip()

        self.format = ContentArgParser.reFormat.search(fileContent)
        if self.format:
            self.format = self.format.group(1).strip()
        else:
            self.format = "markdown"
        self.content = fileContent

    def updateArgs(self, args):
        self._inferArgsFromContent()
        args.labels = self.labels
        args.title = self.title
        args.content = self.content
        args.format = self.format
        if self.postId:
            args.postId = self.postId
            args.command = "update"
        else:
            args.command = "post"

    def updateFileWithPostId(self, postId):
        if self.theFile == sys.stdin:
            return
        if not hasattr(self, "content"):
            self.content = self.theFile.read()
        with self.open(self.theFile.name, "w") as f:
            # logger.debug(
                        #"updating file {} with postId {}",
                        # self.theFile.name,
                        # postId)
            content = ContentArgParser.rePostIdUpdate.sub(
                'PostId: ' + postId,
                self.content)
            f.write(content)
            f.flush()


def parse_args(sysargv):
    parser = argparse.ArgumentParser(
        prog='easyblogger',
        description="Easily manage posts on Blogger blogs",
        fromfile_prefix_chars='@')
    parser.add_argument(
        "-i",
        "--clientid",
        help="Your API Client id",
        default="132424086208.apps.googleusercontent.com")
    parser.add_argument(
        "-s",
        "--secret",
        help="Your API Client secret",
        default="DKEk2rvDKGDAigx9q9jpkyqI")
    parser.add_argument(
        "-v",
        "--verbose",
        help="verbosity(log level) -vvvv = DEBUG, -v = CRITICAL",
        action="count",
        default=0)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--blogid", help="Your blog id")
    group.add_argument("--url", help="Your blog url")

    subparsers = parser.add_subparsers(help="sub-command help", dest="command")

    get_parser = subparsers.add_parser("get", help="list posts")
    group = get_parser.add_mutually_exclusive_group()
    group.add_argument("-p", "--postId", help="the post id")
    group.add_argument("-l", "--labels", help="comma separated list of labels")
    group.add_argument("-q", "--query", help="search term")
    output_format = get_parser.add_mutually_exclusive_group()
    output_format.add_argument(
        "-f",
        "--fields",
        help="fields to output",
        default="id,title,url")
    output_format.add_argument("-d", "--doc",
                               help="Output as document - use one of the output formats supported by pandoc")
    get_parser.add_argument("-w", "--write-files",
                            dest='tofiles',
                            help="write output files (only used with --doc). True if more than one post is retrieved",
                            action="store_true")
    get_parser.add_argument(
        "-c",
        "--count",
        type=int,
        help="count",
        default=10)

    post_parser = subparsers.add_parser("post", help="create a new post")
    post_parser.add_argument("-t", "--title", help="Post title")
    post_parser.add_argument(
        "-l",
        "--labels",
        help="comma separated list of labels")
    post_input = post_parser.add_mutually_exclusive_group(required=True)
    post_input.add_argument("-c", "--content", help="Post content")
    post_input.add_argument(
        "-f",
        "--file",
        type=argparse.FileType('r'),
        help="Post content - input file")
    pandocInputFormats = ["native",
                          "json",
                          "markdown",
                          "markdown_strict",
                          "markdown_phpextra",
                          "markdown_mmd",
                          "rst",
                          "mediawiki",
                          "docbook",
                          "textile",
                          "html",
                          "latex"]
    post_parser.add_argument(
        "--format",
        help="Content format",
        choices=pandocInputFormats,
        default="html")
    delete_parser = subparsers.add_parser("delete", help="delete a post")
    delete_parser.add_argument("postIds", nargs="+", help="the post to delete")

    update_parser = subparsers.add_parser("update", help="update a post")
    update_parser.add_argument("postId", help="the post to update")
    update_parser.add_argument("-t", "--title", help="Post title")

    update_input = update_parser.add_mutually_exclusive_group()
    update_input.add_argument("-c", "--content", help="Post content")
    update_input.add_argument(
        "-f",
        "--file",
        type=argparse.FileType('r'),
        help="Post content - input file")

    update_parser.add_argument(
        "--format",
        help="Content format",
        choices=pandocInputFormats,
        default="html")

    update_parser.add_argument(
        "-l",
        "--labels",
        help="comma separated list of labels")

    file_parser = subparsers.add_parser(
        "file",
        help="Figure out what to do from the input file")
    file_parser.add_argument(
        "file",
        type=argparse.FileType('r'),
        nargs="?",
        default=sys.stdin,
        help="Post content - input file")

    config = os.path.expanduser("~/.easyblogger")
    if (os.path.exists(config)):
        sysargv = ["@" + config] + sysargv
    logger.debug("Final args:")
    logger.debug(sysargv)

    args = parser.parse_args(sysargv)
    verbosity = 50 - args.verbose * 10
    if args.verbose > 0:
        print("Setting log level to %s" % logging.getLevelName(verbosity))
    logger.setLevel(verbosity)
    return args


def main(sysargv=sys.argv):
    args = parse_args(sysargv[1:])
    blogger = EasyBlogger(args.clientid, args.secret, args.blogid, args.url)
    return runner(args, blogger)


def runner(args, blogger):
    try:
        contentArgs = None
        if args.command == "file":
            contentArgs = ContentArgParser(args.file)
            contentArgs.updateArgs(args)

        if args.command == "post":
            newPost = blogger.post(args.title,
                                   args.content or args.file,
                                   args.labels, fmt=args.format)
            postId = newPost['id']
            if contentArgs:
                contentArgs.updateFileWithPostId(postId)
            else:
                print postId

        if args.command == 'delete':
            for postId in args.postIds:
                blogger.deletePost(postId)

        if args.command == 'update':
            blogger.updatePost(
                args.postId,
                args.title,
                args.content or args.file,
                args.labels,
                fmt=args.format)

        if args.command == "get":
            if args.postId:
                posts = blogger.getPosts(postId=args.postId)
            elif args.query:
                posts = blogger.getPosts(
                    query=args.query,
                    maxResults=args.count)
            else:
                posts = blogger.getPosts(
                    labels=args.labels,
                    maxResults=args.count)
            printJson(posts)
            printPosts(posts, args.fields, args.doc, args.tofiles)
    except AccessTokenRefreshError:
        # The AccessTokenRefreshError exception is raised if the credentials
        # have been revoked by the user or they have expired.
        print ('The credentials have been revoked or expired, please re-run'
               'the application to re-authorize')
        return -1
    return 0


def getFilenameFromPostUrl(url, format):
    urlp = urlparse.urlparse(url)
    filename = os.path.basename(urlp.path)
    return os.path.splitext(filename)[0] + "." + format


def printPosts(posts, fields, docFormat=None, writeToFiles=False):
    template = """<!--
Title       : {0}
PostId      : {1}
Labels      : {2}
Format      : {3}
-->

{4}
"""
    if not "items" in posts:
        return
    if docFormat:
        if len(posts["items"]) > 1:
            writeToFiles = True
        for item in posts["items"]:
            converted = pypandoc.convert(
                item["content"].encode('utf-8',
                                       'ignore'),
                docFormat,
                format="html")
            content = template.format(
                item["title"],
                item['id'],
                ",".join(item["labels"]),
                docFormat,
                converted)
            if writeToFiles:
                filename = getFilenameFromPostUrl(item['url'], docFormat)
                logger.info(filename)
                with open(filename, "wb") as outputFile:
                    outputFile.write(content)
            else:
                print content
        return
    if isinstance(fields, basestring):
        fields = fields.split(",")
    for item in posts['items']:
        line = [str(item[k]) for k in fields if k in item]
        print ",".join(line)


def printJson(data):
    """@todo: Docstring for printJson

    :data: @todo
    :returns: @todo
    """
    logger.debug(
        json.dumps(data,
                   sort_keys=True,
                   indent=4,
                   separators=(',',
                               ': ')))

if __name__ == '__main__':
    # print sys.argv
    main()
