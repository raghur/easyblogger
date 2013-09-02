from unittest import TestCase
from mock import Mock, DEFAULT
from blogger import EasyBlogger
from apiclient.errors import HttpError


class PostsTests(TestCase):
    def setUp(self):
        self.blogger = EasyBlogger("id", "secret", "1234")
        self.blogger.service = Mock()
        self.posts = self.blogger.service.posts.return_value

    def test_should_post(self):
        def validateBody( blogId = None, body = None): 
            assert body["title"] == "t"
            assert body["content"] == "c"
            assert body["labels"] ==["l"]
            return DEFAULT

        self.posts.insert.side_effect = validateBody
        req = self.posts.insert.return_value

        newPost = self.blogger.post("t", "c", "l")

        assert self.posts.insert.call_count == 1
        self.posts.insert.assert_called()
        req.execute.assert_called()

    def test_labels_should_be_included_only_if_provided(self):

        def validateBody( blogId = None, body = None): 
            assert body["title"] == "t"
            assert body["content"] == "c"
            self.assertTrue("labels" not in body)
            return DEFAULT
        self.posts.insert.side_effect = validateBody
        req = self.posts.insert.return_value

        newPost = self.blogger.post("t", "c", None)

        self.posts.insert.assert_called()
        req.execute.assert_called()

    def test_labels_should_be_split_if_provided(self):
        def validateBody( blogId = None, body = None): 
            assert body["title"] == "t"
            assert body["content"] == "c"
            assert len(body["labels"]) == 3
            return DEFAULT
        self.posts.insert.side_effect = validateBody
        req = self.posts.insert.return_value

        newPost = self.blogger.post("t", "c", "a,b,c")

        self.posts.insert.assert_called()
        req.execute.assert_called()


    def test_should_read_content_from_file(self):
        def validateBody( blogId = None, body = None): 
            assert body["title"] == "t"
            assert body["content"] == "filecontent"
            assert len(body["labels"]) == 3
            return DEFAULT
        self.posts.insert.side_effect = validateBody
        req = self.posts.insert.return_value

        fileMock = Mock()
        fileMock.read.return_value = "filecontent"
        newPost = self.blogger.post("t",fileMock, "a,b,c")

        fileMock.read.assert_called()
        self.posts.insert.assert_called()
        req.execute.assert_called()

    def test_should_convert_to_markup(self):
        def validateBody( blogId = None, body = None): 
            assert body["title"] == "t"
            assert body["content"] == "<filecontent>"
            assert len(body["labels"]) == 3
            return DEFAULT
        self.posts.insert.side_effect = validateBody
        req = self.posts.insert.return_value

        fileMock = Mock()
        fileMock.read.return_value = "filecontent"

        converterMock = Mock()
        self.blogger.converter = converterMock
        converterMock.convert.return_value = "<filecontent>"
        newPost = self.blogger.post("t",fileMock, "a,b,c", fmt="markdown")

        fileMock.read.assert_called()
        converterMock.convert.assert_called_with("filecontent", 'html', format = "markdown")
        self.posts.insert.assert_called()
        req.execute.assert_called()
