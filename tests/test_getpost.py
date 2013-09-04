from unittest import TestCase
from mock import Mock
from blogger import EasyBlogger
from apiclient.errors import HttpError


class GetPostsTests(TestCase):
    def setUp(self):
        self.blogger = EasyBlogger("id", "secret", "1234")
        self.blogger.service = Mock()

    def tearDown(self):
        self.blogger = None

    def test_should_get_blog_by_labels(self):
        # Arrange
        posts = self.blogger.service.posts.return_value

        # act
        self.blogger.getPosts(labels="abc", maxResults=4)

        #assert
        posts.list.assert_called_with(blogId="1234", labels="abc", maxResults=4)

    def test_should_default_search_by_labels(self):
        posts = self.blogger.service \
                        .posts       \
                        .return_value
        req = posts.get.return_value
        self.blogger.getPosts()
        posts.list.assert_called_with(blogId=self.blogger.blogId, labels="", maxResults=1)
        req.execute.assert_called()

    def test_should_use_search_when_query_is_provided(self):
        posts = self.blogger.service \
                        .posts       \
                        .return_value
        req = posts.get.return_value
        self.blogger.getPosts(query="test")
        posts.search.assert_called_with(blogId=self.blogger.blogId, q="test")
        req.execute.assert_called()


    def test_should_get_blog_by_id(self):
        posts = self.blogger.service \
                        .posts       \
                        .return_value
        req = posts.get.return_value
        item = {"id": 23234}
        req.execute.return_value = item

        post = self.blogger.getPosts(postId="234")

        posts.get.assert_called_with(blogId="1234", postId="234")
        req.execute.assert_called()
        assert "items" in post
        assert len(post["items"]) == 1
        assert post["items"][0] == item

    def test_should_return_empty_array_when_id_not_found(self):

        posts = self.blogger.service \
                        .posts       \
                        .return_value
        req = posts.get.return_value
        resp = Mock()
        resp.status = 404
        req.execute.side_effect = HttpError(resp, "")

        post = self.blogger.getPosts(postId="234")

        posts.get.assert_called_with(blogId="1234", postId="234")
        req.execute.assert_called()
        assert "items" in post
        assert len(post["items"]) == 0

    def test_should_rethrow_exception_other_than_404(self):

        posts = self.blogger.service \
                .posts       \
                .return_value
        req = posts.get.return_value
        resp = Mock()
        resp.status = 401
        req.execute.side_effect = HttpError(resp, "")

        with self.assertRaises(HttpError):
            post = self.blogger.getPosts(postId="234")

        posts.get.assert_called_with(blogId="1234", postId="234")
        req.execute.assert_called()
