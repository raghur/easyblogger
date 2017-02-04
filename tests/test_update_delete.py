from unittest import TestCase
from mock import Mock, DEFAULT
from blogger import EasyBlogger


class UpdateDeleteTests(TestCase):

    def setUp(self):
        self.blogger = EasyBlogger("id", "secret", "1234")
        self.blogger.service = Mock()
        self.posts = self.blogger.service.posts.return_value

    def test_should_update_draft(self):
        def validateBody(blogId, postId, body, revert, publish):
            assert blogId == "1234"
            assert postId == "4321"
            assert body["title"] == "t"
            assert body["content"] == "c"
            assert body["labels"] == ["l"]
            assert not revert
            assert not publish
            return DEFAULT

        self.posts.patch.side_effect = validateBody
        getreq = self.posts.get.return_value
        getreq.execute.return_value = {"status": "DRAFT"}

        self.blogger.updatePost("4321", "t", "c", "l")

        req = self.posts.patch.return_value
        self.posts.patch.assert_called()
        assert self.posts.patch.call_count == 1
        req.execute.assert_called()

    def test_publish_a_draft(self):
        def validateBody(blogId, postId, body, revert, publish):
            assert not revert
            assert publish
            return DEFAULT

        self.posts.patch.side_effect = validateBody
        getreq = self.posts.get.return_value
        getreq.execute.return_value = {"status": "DRAFT"}

        self.blogger.updatePost("4321", "t", "c", "l", isDraft=False)

        req = self.posts.patch.return_value
        self.posts.patch.assert_called()
        assert self.posts.patch.call_count == 1
        req.execute.assert_called()

    def test_must_revert_live_post_on_update(self):
        def validateBody(blogId, postId, body, revert, publish):
            assert revert
            assert not publish
            return DEFAULT

        self.posts.patch.side_effect = validateBody
        getreq = self.posts.get.return_value
        getreq.execute.return_value = {"status": "LIVE"}

        self.blogger.updatePost("4321", "t", "c", "l", isDraft=True)

        req = self.posts.patch.return_value
        self.posts.patch.assert_called()
        assert self.posts.patch.call_count == 1
        req.execute.assert_called()

    def test_should_update_post(self):
        def validateBody(blogId, postId, body, revert, publish):
            assert blogId == "1234"
            assert postId == "4321"
            assert body["title"] == "t"
            assert body["content"] == "c"
            assert body["labels"] == ["l"]
            assert revert
            assert not publish
            return DEFAULT

        self.posts.patch.side_effect = validateBody
        getreq = self.posts.get.return_value
        getreq.execute.return_value = {"status": "LIVE"}

        self.blogger.updatePost("4321", "t", "c", "l")

        req = self.posts.patch.return_value
        self.posts.patch.assert_called()
        assert self.posts.patch.call_count == 1
        req.execute.assert_called()

    def test_update_post_should_take_label_array(self):
        def validateBody(blogId, postId, body, revert, publish):
            assert blogId == "1234"
            assert postId == "4321"
            assert body["title"] == "t"
            assert body["content"] == "c"
            assert body["labels"] == ["l"]
            assert revert
            assert not publish
            return DEFAULT

        self.posts.patch.side_effect = validateBody
        getreq = self.posts.get.return_value
        getreq.execute.return_value = {"status": "LIVE"}

        self.blogger.updatePost("4321", "t", "c", ["l"])

        req = self.posts.patch.return_value
        self.posts.patch.assert_called()
        assert self.posts.patch.call_count == 1
        req.execute.assert_called()

    def test_update_should_fail_if_nothing_specified(self):
        with self.assertRaises(ValueError):
            self.blogger.updatePost("4321")

    def test_should_delete_post(self):
        req = self.posts.delete.return_value

        self.blogger.deletePost("12345")

        self.posts.delete.assert_called_with(blogId="1234", postId="12345")
        req.execute.assert_called()
