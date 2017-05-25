from unittest import TestCase
from mock import Mock, call, patch
from blogger.main import parse_args, runner
from oauth2client.client import AccessTokenRefreshError


@patch('blogger.main.pypandoc')
class MainTests(TestCase):
    posts = {"items": [
            {
                "id": "100",
                "title": "title",
                "url": "url"
            }
    ]
    }

    def test_should_invoke_post(self, pypandocMock):
        pypandocMock.get_pandoc_formats.return_value = [['a'], ['b']]
        args = parse_args(['post', "-t", "t", "-c", "content"])
        print(args)
        blogObj = Mock()
        blogObj.post.return_value = {"id": "100", "url": "someurl"}

        exitStatus = runner(args, blogObj)

        blogObj.post.assert_called_with(
            "t", "content", None, [], isDraft=True, fmt="html")
        assert exitStatus == 0

    def test_should_invoke_delete(self, pypandocMock):
        pypandocMock.get_pandoc_formats.return_value = [['a'], ['b']]
        args = parse_args(['delete', '100', "200"])
        blogObj = Mock()

        runner(args, blogObj)

        assert blogObj.deletePost.call_count == 2
        expected = [call.deletePost('100'), call.deletePost('200')]
        assert blogObj.mock_calls == expected

    def test_should_invoke_update(self, pypandocMock):
        pypandocMock.get_pandoc_formats.return_value = [['a'], ['b']]
        args = parse_args(
            ['update', "-t", "t", "-c", "content", "100"])
        blogObj = Mock()
        blogObj.updatePost.return_value = {"id": "100", "url": "someurl"}

        runner(args, blogObj)

        blogObj.updatePost.assert_called_with(
            "100", "t", "content", None, [], isDraft=True, fmt="html")

    def test_should_invoke_getbyid(self, pypandocMock):
        pypandocMock.get_pandoc_formats.return_value = [['a'], ['b']]
        args = parse_args(['get', "-p", "100"])
        blogObj = Mock()
        blogObj.getPosts.return_value = MainTests.posts

        runner(args, blogObj)

        blogObj.getPosts.assert_called_with(postId="100")

    def test_should_return_error_exit_code_on_exception(self, pypandocMock):
        pypandocMock.get_pandoc_formats.return_value = [['a'], ['b']]
        args = parse_args(['get', "-p", "100"])
        blogObj = Mock()
        blogObj.getPosts.side_effect = AccessTokenRefreshError

        rval = runner(args, blogObj)
        assert rval == -1

    def test_should_invoke_bylabel_bydefault(self, pypandocMock):
        pypandocMock.get_pandoc_formats.return_value = [['a'], ['b']]
        args = parse_args(['get'])
        blogObj = Mock()
        blogObj.getPosts.return_value = MainTests.posts

        runner(args, blogObj)

        blogObj.getPosts.assert_called_with(labels=None, maxResults=None)

    def test_should_invoke_search(self, pypandocMock):
        pypandocMock.get_pandoc_formats.return_value = [['a'], ['b']]
        args = parse_args(['get', "-q", "query"])
        blogObj = Mock()
        blogObj.getPosts.return_value = MainTests.posts

        runner(args, blogObj)
        blogObj.getPosts.assert_called_with(query="query", maxResults=None)

    def test_should_invoke_get_by_url(self, pypandocMock):
        pypandocMock.get_pandoc_formats.return_value = [['a'], ['b']]
        args = parse_args(['get', "-u", "https://some/url"])
        blogObj = Mock()
        blogObj.getPosts.return_value = MainTests.posts

        runner(args, blogObj)
        blogObj.getPosts.assert_called_with(url="https://some/url")

    def test_empty_results_in_get(self, pypandocMock):
        pypandocMock.get_pandoc_formats.return_value = [['a'], ['b']]
        args = parse_args(['get', "-q", "query"])
        blogObj = Mock()
        blogObj.getPosts.return_value = {"items": []}

        runner(args, blogObj)
        blogObj.getPosts.assert_called_with(query="query", maxResults=None)

    def test_handle_non_existent_keys_in_fields(self, pypandocMock):
        pypandocMock.get_pandoc_formats.return_value = [['a'], ['b']]
        args = parse_args(['get', "-q", "query", "-f", "id,b"])
        blogObj = Mock()
        blogObj.getPosts.return_value = MainTests.posts

        runner(args, blogObj)
        blogObj.getPosts.assert_called_with(query="query", maxResults=None)
