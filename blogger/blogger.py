#!/usr/bin/python
#
# Copyright 2012 Raghu Rajagopalan. All Rights Reserved.
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

import logging
import os
import os.path
import re
import sys
import toml
from subprocess import check_output
from tempfile import NamedTemporaryFile
import httplib2
import pypandoc
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client import tools
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = (str, bytes)
else:
    # 'unicode' exists, must be Python 2
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring
logger = logging.getLogger(__name__)


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
        self.check_output = check_output
        self.namedTemporaryFile = NamedTemporaryFile
        self.open = open

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

        # Create a flow object. This object holds the client_id, client_secret,
        # and scope. It assists with OAuth 2.0 steps to get user authorization
        # and credentials.
        flow = OAuth2WebServerFlow(self.clientId, self.clientSecret, scope)
        # Create a Storage object. This object holds the credentials that your
        # application needs to authorize access to the user's data. The name of
        # the credentials file is provided. If the file does not exist, it is
        # created. This object can only hold credentials for a single user, so
        # as-written, this script can only handle a single user.
        storage = Storage(os.path.expanduser('~/.easyblogger.credentials'))

        # The get() function returns the credentials for the Storage object.
        # If no credentials were found, None is returned.
        credentials = storage.get()

        # If no credentials are found or the credentials are invalid due to
        # expiration, new credentials need to be obtained from the
        # authorization server. The oauth2client.tools.run() function attempts
        # to open an authorization server page in your default web browser. The
        # server asks the user to grant your application access to the user's
        # data.  If the user grants access, the run() function returns new
        # credentials.  The new credentials are also stored in the supplied
        # Storage object, which updates the credentials.dat file.
        if credentials is None or credentials.invalid:
            flags = tools.argparser.parse_args(args=[])
            credentials = tools.run_flow(flow, storage, flags)

        # Create an httplib2.Http object to handle our HTTP requests, and
        # authorize it using the credentials.authorize() function.
        http = httplib2.Http()
        http.disable_ssl_certificate_validation = True
        http = credentials.authorize(http)

        # The apiclient.discovery.build() function returns an instance of an
        # API service object can be used to make API calls. The object is
        # constructed with methods specific to the blogger API. The arguments
        # provided are:
        #   name of the API ('blogger')
        #   version of the API you are using ('v3')
        #   authorized httplib2.Http() object that can be used for API calls
        self.service = build('blogger', 'v3', http=http, cache_discovery=False)
        return self.service

    def _setBlog(self):
        if self.blogId:
            return
        service = self._OAuth_Authenticate()
        request = service.blogs().getByUrl(url=self.blogUrl)
        blog = request.execute()
        self.blogId = blog['id']

    def getPosts(self, postId=None, query=None, labels="", url=None,
                 maxResults=None):
        self._setBlog()
        try:
            service = self._OAuth_Authenticate()
            if postId:
                request = service.posts().get(
                    blogId=self.blogId, postId=postId, view="AUTHOR")
                post = request.execute()
                yield post
                return
            elif query:
                request = service.posts().search(blogId=self.blogId, q=query)
            elif url:
                regex = re.compile(r"^https?://.*?/")
                if url.find("http") == 0:
                    url = "/" + regex.sub("", url)
                logger.debug('getting post by url %s', url)
                request = service.posts().getByPath(blogId=self.blogId,
                                                    path=url)
                post = request.execute()
                yield post
                return
            else:
                request = service.posts().list(
                    blogId=self.blogId,
                    labels=labels,
                    maxResults=maxResults)
            count = 0
            while request:
                response = request.execute()
                if not "items" in response:
                    break
                logger.debug("Got %s items", len(response["items"]))
                count += len(response["items"])
                for it in response["items"]:
                    yield it
                if maxResults and count == maxResults:
                    break
                request = service.posts().list_next(request, response)
        except HttpError as he:
            if he.resp.status == 404:
                return
            raise

    def _getMarkup(self, content, fmt, filters):
        raw = content
        if hasattr(content, 'read'):
            raw = content.read()
        html = raw
        if fmt != "html":
            if fmt == "asciidoc":
                logger.debug("using asciidoc")
                with self.namedTemporaryFile(delete=False,
                                             suffix=".adoc") as fp:
                    # print(type(raw))
                    if bytes == str:
                        # py2 - decode unicode to byte array
                        encodedBytes = raw.encode('utf8')
                    else:
                        encodedBytes = bytes(raw, 'utf8')
                    fp.write(encodedBytes)
                    fp.seek(0)
                    print(fp.name)
                    logger.debug("temp file: %s", fp.name)
                    htmlfile, ext = os.path.splitext(fp.name)
                    htmlfile = htmlfile + ".html"
                    logger.debug("Html file will be: %s", htmlfile)
                try:
                    cmd = ["asciidoctor",
                           "-v",
                           "-r",
                           "asciidoctor-diagram",
                           "-a", "stylesheet!",
                           "-a", "allow-uri-read",
                           "-a", "sectanchors",
                           "-a", "sectnums",
                           "-a", "last-update-label!",
                           "-a", "experimental",
                           "-a", "data-uri",
                           "-a", "icons=font",
                           fp.name]
                    logger.debug("Running command: %s", " ".join(cmd))
                    if (os.name == "nt"):
                        self.check_output(cmd, shell=True)
                    else:
                        self.check_output(cmd)
                    html = self.open(htmlfile).read()
                except Exception as e:
                    print(e)
                    raise e
            else:
                html = self.converter.convert(
                    raw, 'html', format=fmt, filters=filters)
        # logger.debug("Converted text: %s", html)
        return html

    def post(self, title, content, labels, filters=[], isDraft=True,
             fmt="html"):
        self._setBlog()
        # url = slugify(title) + ".html"
        service = self._OAuth_Authenticate()
        markup = self._getMarkup(content, fmt, filters)
        blogPost = {"content": markup, "title": title}
        blogPost['labels'] = EasyBlogger._parseLabels(labels)

        req = service.posts().insert(blogId=self.blogId,
                                     body=blogPost,
                                     isDraft=isDraft)
        return req.execute()

    def deletePost(self, postId):
        self._setBlog()
        service = self._OAuth_Authenticate()
        req = service.posts().delete(blogId=self.blogId, postId=postId)
        return req.execute()

    def updatePost(self, postId, title=None, content=None, labels=None,
                   filters=[],
                   isDraft=True,
                   fmt="html"):
        self._setBlog()
        service = self._OAuth_Authenticate()
        blogPost = {}
        if not (title or content or labels):
            raise ValueError(
                "At least one of title, content or labels is required")
        if title:
            blogPost['title'] = title
        if content:
            blogPost['content'] = self._getMarkup(content, fmt, filters)
        blogPost['labels'] = EasyBlogger._parseLabels(labels)

        logger.debug("blogpost %s", labels)
        postStatus = service.posts().get(
            blogId=self.blogId,
            postId=postId,
            view="AUTHOR",
            fields="status"
        ).execute()['status']
        mustPublish = postStatus == 'DRAFT' and not isDraft
        logger.debug(
            "must publish (postStatus(%s) == 'DRAFT' and not isDraft(%s)): %s"
            % (postStatus, isDraft, mustPublish))

        # publish the post since we cannot update a draft directly
        if postStatus == "DRAFT":
            service.posts().publish(blogId=self.blogId,
                                    postId=postId).execute()
        resp = service.posts().patch(
            blogId=self.blogId,
            postId=postId,
            body=blogPost,
            revert=isDraft,
            publish=mustPublish).execute()
        return resp


class ContentArgParser(object):
    reToml = re.compile(r"^\+\+\+\s*$(.*?)^\+\+\+\s*$(.*)",
                        re.MULTILINE | re.DOTALL)
    rePostId = re.compile("^\s*postId\s*:\s*(\d+)\s*$", re.I | re.M)
    reLabels = re.compile("^\s*labels\s*:(.*)$", re.I | re.M)
    reTitle = re.compile("^\s*title\s*:\s*(.+)\s*$", re.I | re.M)
    reFormat = re.compile("^\s*format\s*:\s*(.+)\s*$", re.I | re.M)
    rePublishStatus = re.compile(
        "^\s*published\s*:\s*(true|false)\s*$", re.I | re.M)
    reFilters = re.compile("^\s*filters\s*:(.*)$", re.I | re.M)
    rePostIdUpdate = re.compile("^(\s*postId\s*:)", re.I | re.M)

    def __init__(self, theFile, open=open):
        self.theFile = theFile
        self.open = open

    def _inferArgsFromContent(self):
        fileContent = self.theFile.read()

        matches = ContentArgParser.reToml.findall(fileContent)
        if matches:
            frontmatter = toml.loads(matches[0][0])
            print(frontmatter)
            logger.debug("Found toml frontmatter %s", frontmatter)
            self.postId = None
            if 'id' in frontmatter:
                self.postId = frontmatter["id"]

            self.labels = ["untagged"]
            if 'tags' in frontmatter:
                self.labels = frontmatter["tags"]

            if 'title' in frontmatter:
                self.title = frontmatter["title"]
            if 'format' in frontmatter:
                self.format = frontmatter["format"]
            else:
                self.format = 'asciidoc'
            if 'draft' in frontmatter:
                self.publishStatus = not frontmatter['draft']
            else:
                self.publishStatus = False
            self.filters = []
            if 'filters' in frontmatter:
                self.filters = frontmatter['filters']
            self.content = matches[0][1]
        else:
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

            self.publishStatus = ContentArgParser.rePublishStatus.search(
                fileContent)
            if self.publishStatus:
                self.publishStatus = self \
                    .publishStatus \
                    .group(1) \
                    .strip().lower() == "true"
            else:
                self.publishStatus = False

            self.filters = ContentArgParser.reFilters.search(fileContent)
            if self.filters:
                self.filters = self.filters.group(1).strip().split(",")
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
        args.publish = self.publishStatus
        args.filters = self.filters
        logger.debug("Updated args %s", args)

    def updateFileWithPostId(self, postId):
        if self.theFile == sys.stdin:
            return
        if not hasattr(self, "content"):
            self.content = self.theFile.read()
        with self.open(self.theFile.name, "w") as f:
            content = ContentArgParser.rePostIdUpdate.sub(
                'PostId: ' + postId,
                self.content)
            # print(type(content))
            if bytes == str and type(content) == unicode:
                content = content.encode('utf8')
            f.write(content)
            f.flush()
