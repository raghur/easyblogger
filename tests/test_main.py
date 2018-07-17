from unittest import TestCase
from mock import Mock, call, patch, mock_open, DEFAULT
from blogger.main import parse_args, runner, getFrontMatter
from oauth2client.client import AccessTokenRefreshError
from datetime import datetime
import toml
import yaml


@patch('blogger.main.EasyBlogger')
@patch('blogger.main.pypandoc')
class MainTests(TestCase):
    posts = {"items": [
            {
                "id": "100",
                "title": "title",
                "url": "url",
                "published": "2018-04-30T14:59:13",
                "status": "LIVE",
                "updated": "2018-04-30T14:59:13"
            }
    ]
    }

    def test_should_generate_yaml_frontmatter_for_markdown(self,
                                                           pypandocMock,
                                                           blogObjClass):
        item = MainTests.posts["items"][0]
        fm = getFrontMatter(item, "markdown", legacy=False, bare=True)
        fmObj = yaml.load(fm)
        assert fmObj["title"] == 'title'
        assert fmObj["id"] == '100'
        assert fmObj["aliases"][0] == 'url'

    def test_should_generate_toml_frontmatter_for_asciidoc(self,
                                                           pypandocMock,
                                                           blogObjClass):
        item = MainTests.posts["items"][0]
        fm = getFrontMatter(item, "asciidoc", legacy=False, bare=True)
        fmObj = toml.loads(fm)
        assert fmObj["title"] == 'title'
        assert fmObj["id"] == '100'
        assert fmObj["aliases"][0] == 'url'

    def test_should_generate_legacy_toml_frontmatter(self,
                                                     pypandocMock,
                                                     blogObjClass):
        item = MainTests.posts["items"][0]
        fm = getFrontMatter(item, "asciidoc", legacy=True, bare=True)
        print(fm)
        fmObj = toml.loads(fm)
        assert fmObj["Title"] == 'title'
        assert fmObj["PostId"] == '100'

    def test_should_generate_legacy_yaml_frontmatter(self,
                                                     pypandocMock,
                                                     blogObjClass):
        item = MainTests.posts["items"][0]
        fm = getFrontMatter(item, "markdown", legacy=True, bare=True)
        fmObj = yaml.load(fm)
        assert fmObj["Title"] == 'title'
        assert fmObj["PostId"] == '100'

    def test_should_process_files_for_update(self, pypandocMock, blogObjClass):
        mo = mock_open(read_data="""
+++
title= "t"
id= "1234"
tags= ["l", "a", "c"]
publishdate=2018-01-01T10:00:00
+++

this is the post """)

        def processItemSideEffect(*positionalArgs, **kwargs):
            args = positionalArgs[0]
            assert args.title == "t"
            assert args.postId == "1234"
            assert args.labels == ["l", "a", "c"]
            assert args.command == "update"
            assert args.publishDate.isoformat() == "2018-01-01T10:00:00"
            assert args.format == "asciidoc"
            assert not args.publish
            return DEFAULT

        blogObj = blogObjClass.return_value
        with patch('blogger.main.open', mo) as openmock, \
                patch('blogger.main.processItem') as mockProcessItem, \
                patch('blogger.main.glob') as glob:
            glob.iglob.return_value = iter(["file1.asciidoc"])
            pypandocMock.get_pandoc_formats.return_value = [['a'], ['b']]
            args = parse_args(['file', "file1.asciidoc"])
            mockProcessItem.side_effect = processItemSideEffect
            exitStatus = runner(args)

    def test_should_process_files_for_create(self, pypandocMock, blogObjClass):
        mo = mock_open(read_data="""
+++
title= "t"
tags= ["l", "a", "c"]
publishdate=2018-01-01T10:00:00
+++

this is the post """)

        def processItemSideEffect(*positionalArgs, **kwargs):
            args = positionalArgs[0]
            assert args.title == "t"
            assert args.labels == ["l", "a", "c"]
            assert args.command == "post"
            assert args.format == "asciidoc"
            print(args.publishDate.isoformat())
            assert args.publishDate.isoformat() == "2018-01-01T10:00:00"
            assert not args.publish
            return DEFAULT

        blogObj = blogObjClass.return_value
        with patch('blogger.main.open', mo) as openmock, \
                patch('blogger.main.processItem') as mockProcessItem, \
                patch('blogger.main.glob') as glob:
            glob.iglob.return_value = iter(["file1.asciidoc"])
            pypandocMock.get_pandoc_formats.return_value = [['a'], ['b']]
            args = parse_args(['file', "file1.asciidoc"])
            mockProcessItem.side_effect = processItemSideEffect
            exitStatus = runner(args)

    def test_should_invoke_post(self, pypandocMock, blogObjClass):
        pypandocMock.get_pandoc_formats.return_value = [['a'], ['b']]
        args = parse_args(['post', "-t", "t", "-c", "content", '--date',
                           '2018-01-01'])
        print(args)
        blogObj = blogObjClass.return_value
        blogObj.post.return_value = {"id": "100", "url": "someurl"}

        exitStatus = runner(args)

        blogObj.post.assert_called_with(
            "t", "content", None, [], isDraft=True, fmt="html",
            publishDate='2018-01-01')
        assert exitStatus == 0

    def test_should_invoke_delete(self, pypandocMock, blogObjClass):
        pypandocMock.get_pandoc_formats.return_value = [['a'], ['b']]
        args = parse_args(['delete', '100', "200"])
        blogObj = blogObjClass.return_value

        runner(args)

        assert blogObj.deletePost.call_count == 2
        expected = [call.deletePost('100'), call.deletePost('200')]
        assert blogObj.mock_calls == expected

    def test_should_invoke_update(self, pypandocMock, blogObjClass):
        pypandocMock.get_pandoc_formats.return_value = [['a'], ['b']]
        args = parse_args(
            ['update', "-t", "t", "-c", "content", "100", '--date',
             '2018-01-01'])
        blogObj = blogObjClass.return_value
        blogObj.updatePost.return_value = {"id": "100", "url": "someurl"}

        runner(args)

        blogObj.updatePost.assert_called_with(
            "100", "t", "content", None, [], isDraft=True, fmt="html",
            publishDate='2018-01-01')

    def test_should_invoke_getbyid(self, pypandocMock, blogObjClass):
        pypandocMock.get_pandoc_formats.return_value = [['a'], ['b']]
        args = parse_args(['get', "-p", "100"])
        blogObj = blogObjClass.return_value
        blogObj.getPosts.return_value = MainTests.posts

        runner(args)

        blogObj.getPosts.assert_called_with(postId="100")

    def test_should_return_error_exit_code_on_exception(self,
                                                        pypandocMock,
                                                        blogObjClass):
        pypandocMock.get_pandoc_formats.return_value = [['a'], ['b']]
        args = parse_args(['get', "-p", "100"])
        blogObj = blogObjClass.return_value
        blogObj.getPosts.side_effect = AccessTokenRefreshError

        rval = runner(args)
        assert rval == -1

    def test_should_invoke_bylabel_bydefault(self, pypandocMock, blogObjClass):
        pypandocMock.get_pandoc_formats.return_value = [['a'], ['b']]
        args = parse_args(['get'])
        blogObj = blogObjClass.return_value
        blogObj.getPosts.return_value = MainTests.posts

        runner(args)

        blogObj.getPosts.assert_called_with(labels=None, maxResults=None)

    def test_should_invoke_search(self, pypandocMock, blogObjClass):
        pypandocMock.get_pandoc_formats.return_value = [['a'], ['b']]
        args = parse_args(['get', "-q", "query"])
        blogObj = blogObjClass.return_value
        blogObj.getPosts.return_value = MainTests.posts

        runner(args)
        blogObj.getPosts.assert_called_with(query="query", maxResults=None)

    def test_should_invoke_get_by_url(self, pypandocMock, blogObjClass):
        pypandocMock.get_pandoc_formats.return_value = [['a'], ['b']]
        args = parse_args(['get', "-u", "https://some/url"])
        blogObj = blogObjClass.return_value
        blogObj.getPosts.return_value = MainTests.posts

        runner(args)
        blogObj.getPosts.assert_called_with(url="https://some/url")

    def test_empty_results_in_get(self, pypandocMock, blogObjClass):
        pypandocMock.get_pandoc_formats.return_value = [['a'], ['b']]
        args = parse_args(['get', "-q", "query"])
        blogObj = blogObjClass.return_value
        blogObj.getPosts.return_value = {"items": []}

        runner(args)
        blogObj.getPosts.assert_called_with(query="query", maxResults=None)

    def test_handle_non_existent_keys_in_fields(self, pypandocMock,
                                                blogObjClass):
        pypandocMock.get_pandoc_formats.return_value = [['a'], ['b']]
        args = parse_args(['get', "-q", "query", "-f", "id,b"])
        blogObj = blogObjClass.return_value
        blogObj.getPosts.return_value = MainTests.posts

        runner(args)
        blogObj.getPosts.assert_called_with(query="query", maxResults=None)
