import sys
import logging
import argparse
import os
import json
import pypandoc
import toml

from oauth2client.client import AccessTokenRefreshError
from .blogger import ContentArgParser, EasyBlogger, logger
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
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


def getFilenameFromPostUrl(url, format):
    urlp = urlparse(url)
    filename = os.path.basename(urlp.path)
    return os.path.splitext(filename)[0] + "." + format


def printPosts(posts, fields, docFormat=None, writeToFiles=False):
    template = """+++
{0}
+++

{1}
"""
    if "items" not in posts:
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
            frontmatter = dict()
            frontmatter["title"] = item["title"]
            frontmatter["id"] = item["id"]
            if "labels" in item:
                frontmatter["tags"] = item["labels"]
            frontmatter["aliases"] = [item["url"]]
            frontmatter["publishdate"] = item["published"]
            frontmatter["date"] = item["published"]
            frontmatter["lastmod"] = item["updated"]
            content = template.format(toml.dumps(frontmatter), converted)
            if writeToFiles:
                filename = getFilenameFromPostUrl(item['url'], docFormat)
                logger.info(filename)
                with open(filename, "wb") as outputFile:
                    try:
                        encodedBytes = bytes(content, "utf8")
                    except TypeError:
                        encodedBytes = bytes(content).encode("utf8")
                    outputFile.write(encodedBytes)
            else:
                print(content)
        return
    if isinstance(fields, basestring):
        fields = fields.split(",")
    for item in posts['items']:
        line = [str(item[k]) for k in fields if k in item]
        print(",".join(line))


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
    group.add_argument("-u", help="the full post url", metavar="URL")
    output_format = get_parser.add_mutually_exclusive_group()
    output_format.add_argument(
        "-f",
        "--fields",
        help="fields to output",
        default="id,title,url")
    output_format.add_argument(
        "-d", "--doc",
        help="Output as document - use one of the output formats supported by pandoc")
    get_parser.add_argument(
        "-w", "--write-files", dest='tofiles',
        help="write output files (only used with --doc). True if more than one post is retrieved",
        action="store_true")
    get_parser.add_argument(
        "-c",
        "--count",
        type=int,
        help="count")

    post_parser = subparsers.add_parser("post", help="create a new post")
    post_parser.add_argument("-t", "--title", help="Post title")
    post_parser.add_argument(
        "-l",
        "--labels",
        help="comma separated list of labels")
    post_parser.add_argument(
        "--publish", action="store_true",
        help="Publish to the blog [default: false]")
    post_input = post_parser.add_mutually_exclusive_group(required=True)
    post_input.add_argument("-c", "--content", help="Post content")
    post_input.add_argument(
        "-f",
        "--file",
        type=argparse.FileType('r'),
        help="Post content - input file")
    pandocInputFormats = ["commonmark",
                          "docbook",
                          "docx",
                          "epub",
                          "haddock",
                          "html",
                          "json",
                          "latex",
                          "markdown",
                          "markdown_github",
                          "markdown_mmd",
                          "markdown_phpextra",
                          "markdown_strict",
                          "mediawiki",
                          "native",
                          "odt",
                          "opml",
                          "org",
                          "rst",
                          "t2t",
                          "textile",
                          "twiki"]
    post_parser.add_argument(
        "--filters",
        nargs="+",
        default=[],
        help="pandoc filters")
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

    update_parser.add_argument(
        "--publish", action="store_true",
        help="Publish to the blog [default: false]")

    update_parser.add_argument(
        "--filters",
        nargs="+",
        default=[],
        help="pandoc filters")

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
                                   args.labels,
                                   args.filters,
                                   isDraft=not args.publish,
                                   fmt=args.format)
            postId = newPost['id']
            if contentArgs:
                contentArgs.updateFileWithPostId(postId)
            print(newPost['url'])

        if args.command == 'delete':
            for postId in args.postIds:
                blogger.deletePost(postId)

        if args.command == 'update':
            updated = blogger.updatePost(
                args.postId,
                args.title,
                args.content or args.file,
                args.labels,
                args.filters,
                isDraft=not args.publish,
                fmt=args.format)
            print(updated['url'])

        if args.command == "get":
            if args.postId:
                posts = blogger.getPosts(postId=args.postId)
            elif args.query:
                posts = blogger.getPosts(
                    query=args.query,
                    maxResults=args.count)
            elif args.u:
                posts = blogger.getPosts(
                    url=args.u)
            else:
                posts = blogger.getPosts(
                    labels=args.labels,
                    maxResults=args.count)
            printJson(posts)
            printPosts(posts, args.fields, args.doc, args.tofiles)
    except AccessTokenRefreshError:
        # The AccessTokenRefreshError exception is raised if the credentials
        # have been revoked by the user or they have expired.
        print('The credentials have been revoked or expired, please re-run'
              'the application to re-authorize')
        return -1
    return 0


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
