import sys
import logging
import coloredlogs
import argparse
import os
import json
import pypandoc
import toml
import gevent
import copy
import glob
import chardet

from gevent import monkey
from oauth2client.client import AccessTokenRefreshError
from .blogger import ContentArgParser, EasyBlogger
from io import open
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
try:
    unicode = unicode
except NameError:
    py2 = False
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = (str, bytes)
else:
    # 'unicode' exists, must be Python 2
    py2 = True
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring

monkey.patch_all()
logging.basicConfig()
logger = logging.getLogger(__name__)


def toUnicode(s):
    if py2:
        enc = chardet.detect(s)['encoding']
        return s.decode(enc).encode('utf8')
    else:
        return s


def getFilenameFromPostUrl(url, format):
    urlp = urlparse(url)
    filename = os.path.basename(urlp.path)
    return os.path.splitext(filename)[0] + "." + format


def getFrontMatter(item, format="toml"):
    frontmatter = dict()
    frontmatter["title"] = item["title"]
    frontmatter["id"] = item["id"]
    if "labels" in item:
        frontmatter["tags"] = item["labels"]
    frontmatter["aliases"] = [item["url"]]
    frontmatter["publishdate"] = item["published"]
    frontmatter["draft"] = False
    frontmatter["date"] = item["published"]
    frontmatter["lastmod"] = item["updated"]
    if format == "toml":
        return toml.dumps(frontmatter)


def printPosts(item, fields, docFormat=None, writeToFiles=False):
    template = u"""+++
{0}
+++

{1}
"""
    logger.debug(json.dumps(item,
                            sort_keys=True,
                            indent=2,
                            separators=(',', ': ')))
    if docFormat:
        logger.debug("Starting to print %s", item['id'])
        filename = None
        content = item["content"].encode('utf-8', "ignore")
        if writeToFiles:
            filename = getFilenameFromPostUrl(item['url'], docFormat)
            with open(filename, "wb") as outputFile:
                outputFile.write(content)
            converted = pypandoc.convert_file(
                filename,
                docFormat,
                format="html")
            content = template.format(getFrontMatter(item),
                                      converted).encode('utf-8',
                                                        errors='replace')
            with open(filename, "wb") as outputfile:
                outputfile.write(content)
        else:
            print(content)
        logger.info("Finished print %s: %s", item['id'], filename)
    elif isinstance(fields, basestring):
        fields = fields.split(",")
        line = [str(item[k]) for k in fields if k in item]
        print(",".join(line))


def parse_args(sysargv):
    pandocInputFormats, pandocOutputFormats = pypandoc.get_pandoc_formats()
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
        help="verbosity(log level) - default CRITICAL",
        choices=["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"],
        type=str.upper,
        default="CRITICAL")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--blogid", help="Your blog id")
    group.add_argument("--url", help="Your blog url")

    subparsers = parser.add_subparsers(help="sub-command help", dest="command")

    get_parser = subparsers.add_parser("get", help="list posts")
    group = get_parser.add_mutually_exclusive_group()
    group.add_argument("-p", "--postId", help="the post id")
    group.add_argument("-l", "--labels", help="comma separated list of labels",
                       type=toUnicode)
    group.add_argument("-q", "--query", help="search term", type=toUnicode)
    group.add_argument("-u", help="the full post url", metavar="URL",
                       type=toUnicode)
    output_format = get_parser.add_mutually_exclusive_group()
    output_format.add_argument(
        "-f",
        "--fields",
        help="fields to output",
        default="id,title,url")
    output_format.add_argument(
        "-d", "--doc",
        help="""Output as document - use one of the output
        formats supported by pandoc: """ + ", ".join(pandocOutputFormats))
    get_parser.add_argument(
        "-w", "--write-files", dest='tofiles',
        help="write output files (only used with --doc). " +
        "True if more than one post is retrieved",
        action="store_true")
    get_parser.add_argument(
        "-c",
        "--count",
        type=int,
        help="count")

    post_parser = subparsers.add_parser("post", help="create a new post")
    post_parser.add_argument("-t", "--title", help="Post title",
                             type=toUnicode)
    post_parser.add_argument(
        "-l",
        "--labels",
        help="comma separated list of labels", type=toUnicode)
    post_parser.add_argument(
        "--publish", action="store_true",
        help="Publish to the blog [default: false]")
    post_input = post_parser.add_mutually_exclusive_group(required=True)
    post_input.add_argument("-c", "--content", help="Post content",
                            type=toUnicode)
    post_input.add_argument(
        "-f",
        "--file",
        type=argparse.FileType('r'),
        help="Post content - input file")
    post_parser.add_argument(
        "--filters",
        nargs="+",
        default=[],
        help="pandoc filters")
    post_parser.add_argument(
        "--format",
        help="Content format: " + ", ".join(pandocInputFormats),
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
        help="Content format: " + ", ".join(pandocInputFormats),
        choices=pandocInputFormats,
        default="html")

    update_parser.add_argument(
        "-l",
        "--labels",
        help="comma separated list of labels", type=toUnicode)

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
        nargs="+",
        help="Post content - input file")

    config = os.path.expanduser("~/.easyblogger")
    if (os.path.exists(config)):
        sysargv = ["@" + config] + sysargv
    args = parser.parse_args(sysargv)
    verbosity = logging.getLevelName(args.verbose)
    # print(verbosity, logging.getLevelName(verbosity))
    coloredlogs.install(verbosity)
    if args.verbose != "critical":
        logger.setLevel(logging.INFO)
        logger.info("setting log level to: %s ", args.verbose)
    logger.setLevel(verbosity)

    logger.debug("Final args:")
    logger.debug(sysargv)

    return args


def main(sysargv=sys.argv):
    args = parse_args(sysargv[1:])
    return runner(args)


def processItem(args, contentArgs=None):
    blogger = EasyBlogger(args.clientid, args.secret, args.blogid,
                          args.url)
    print("In processItem")
    try:
        if args.command == "post":
            newPost = blogger.post(args.title,
                                   args.content or args.file,
                                   args.labels,
                                   args.filters,
                                   isDraft=not args.publish,
                                   fmt=args.format)
            postId = newPost['id']
            logger.debug("Created post: %s", postId)
            if contentArgs:
                contentArgs.updateFileWithPostId(postId)
            print(newPost['url'])

        if args.command == 'delete':
            logger.debug("Deleting post: %s", args.postIds)
            for postId in args.postIds:
                blogger.deletePost(postId)

        if args.command == 'update':
            logger.debug("Updating post: %s", args.postId)
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
            jobs = [gevent.spawn(printPosts,
                                 item, args.fields, args.doc, args.tofiles)
                    for item in posts]
            gevent.wait(jobs)
    except AccessTokenRefreshError:
        # The AccessTokenRefreshError exception is raised if the credentials
        # have been revoked by the user or they have expired.
        print('The credentials have been revoked or expired, please re-run'
              ' the application to re-authorize')
        return -1
    return 0


def runner(args):
    if args.command == "file":
        jobs = []
        files = frozenset()
        for fn in args.file:
            files = files.union(glob.iglob(fn))
        logger.info("Processing files: %s", files)
        for f in files:
            argsCopy = copy.deepcopy(args)
            with open(f, "r", newline="\n") as fh:
                argsCopy.file = fh
                contentArgs = ContentArgParser(fh)
                contentArgs.updateArgs(argsCopy)
                logger.debug("Updated args: %s", argsCopy)
                jobs.append(gevent.spawn(processItem, argsCopy, contentArgs))
        gevent.wait(jobs)
        return 0
    else:
        return processItem(args)


if __name__ == '__main__':
    # print sys.argv
    main()
