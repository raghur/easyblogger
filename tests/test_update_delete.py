from unittest import TestCase
from mock import Mock, DEFAULT
from blogger import EasyBlogger
from apiclient.errors import HttpError


class UpdateDeleteTests(TestCase):
    def setUp(self):
        self.blogger = EasyBlogger("id", "secret", "1234")
        self.blogger.service = Mock()
        self.posts = self.blogger.service.posts.return_value

    def test_should_update_post(self):
        def validateBody(blogId, postId, body):
            assert blogId == "1234"
            assert postId == "4321"
            assert body["title"] == "t"
            assert body["content"] == "c"
            assert body["labels"] == ["l"]
            return DEFAULT

        self.posts.patch.side_effect = validateBody
        req = self.posts.return_value

        self.blogger.updatePost("4321", "t", "c", "l")
        
        self.posts.patch.assert_called()
        assert self.posts.patch.call_count == 1
        req.execute.assert_called()
        
    def test_update_post_should_take_label_array(self):
        def validateBody(blogId, postId, body):
            assert blogId == "1234"
            assert postId == "4321"
            assert body["title"] == "t"
            assert body["content"] == "c"
            assert body["labels"] == ["l"]
            return DEFAULT

        self.posts.patch.side_effect = validateBody
        req = self.posts.return_value

        self.blogger.updatePost("4321", "t", "c", ["l"])
        
        self.posts.patch.assert_called()
        assert self.posts.patch.call_count == 1
        req.execute.assert_called()

    def test_update_should_fail_if_nothing_specified(self):
        with self.assertRaises(ValueError) as ve:
            self.blogger.updatePost("4321" )
        

    def test_should_delete_post(self):
        req = self.posts.delete.return_value

        self.blogger.deletePost("12345")

        self.posts.delete.assert_called_with(blogId = "1234", postId = "12345")
        req.assert_called()
