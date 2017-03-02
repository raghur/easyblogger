from unittest import TestCase
from mock import Mock, patch, DEFAULT, PropertyMock
from blogger import EasyBlogger


class PostsTests(TestCase):

    def setUp(self):
        self.blogger = EasyBlogger("id", "secret", "1234")
        self.blogger.service = Mock()
        self.posts = self.blogger.service.posts.return_value

    def test_should_post(self):
        def validateBody(blogId=None, body=None, isDraft=True):
            assert body["title"] == "t"
            assert body["content"] == "c"
            assert body["labels"] == ["l"]
            assert isDraft
            return DEFAULT

        self.posts.insert.side_effect = validateBody
        req = self.posts.insert.return_value

        self.blogger.post("t", "c", "l")

        assert self.posts.insert.call_count == 1
        self.posts.insert.assert_called()
        req.execute.assert_called()

    def test_labels_should_be_included_only_if_provided(self):

        def validateBody(blogId=None, body=None, isDraft=True):
            assert body["title"] == "t"
            assert body["content"] == "c"
            self.assertTrue(body["labels"] is None)
            assert isDraft
            return DEFAULT
        self.posts.insert.side_effect = validateBody
        req = self.posts.insert.return_value

        self.blogger.post("t", "c", None)

        self.posts.insert.assert_called()
        req.execute.assert_called()

    def test_labels_should_be_split_if_provided(self):
        def validateBody(blogId=None, body=None, isDraft=True):
            assert body["title"] == "t"
            assert body["content"] == "c"
            assert len(body["labels"]) == 3
            assert isDraft
            return DEFAULT
        self.posts.insert.side_effect = validateBody
        req = self.posts.insert.return_value

        self.blogger.post("t", "c", "a,b,c")

        self.posts.insert.assert_called()
        req.execute.assert_called()

    def test_should_read_content_from_file(self):
        def validateBody(blogId=None, body=None, isDraft=True):
            assert body["title"] == "t"
            assert body["content"] == "filecontent"
            assert len(body["labels"]) == 3
            assert isDraft
            return DEFAULT
        self.posts.insert.side_effect = validateBody
        req = self.posts.insert.return_value

        fileMock = Mock()
        fileMock.read.return_value = "filecontent"
        self.blogger.post("t", fileMock, "a,b,c")

        fileMock.read.assert_called()
        self.posts.insert.assert_called()
        req.execute.assert_called()

    def test_should_convert_to_markup(self):
        def validateBody(blogId=None, body=None, isDraft=True):
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
        self.blogger.post("t", fileMock, "a,b,c", fmt="markdown")

        fileMock.read.assert_called()
        converterMock.convert.assert_called_with(
            "filecontent",
            'html',
            filters=[],
            format="markdown")
        self.posts.insert.assert_called()
        req.execute.assert_called()

    @patch('tempfile.NamedTemporaryFile', autospec=True)
    @patch('subprocess.check_output', autospec=True)
    def test_should_convert_to_asciidoc_markup(self,mock_cp, mock_ntf ):
        def validateBody(blogId=None, body=None, isDraft=True):
            assert body["title"] == "t"
            assert body["content"] == "<filecontent>"
            assert len(body["labels"]) == 3
            return DEFAULT
        self.posts.insert.side_effect = validateBody
        req = self.posts.insert.return_value

        fileMock = Mock()
        fileMock.read.return_value = "filecontent"

        self.blogger.namedTemporaryFile = mock_ntf
        self.blogger.open = Mock()
        htmlFile = self.blogger.open.return_value
        mockTempFile = mock_ntf.return_value.__enter__.return_value
        htmlFile.read.return_value = "<filecontent>"
        type(mockTempFile).name = PropertyMock(return_value = "c:/some/path/file.adoc")
        self.blogger.check_output = mock_cp
        self.blogger.post("t", fileMock, "a,b,c", fmt="asciidoc")

        fileMock.read.assert_called()

        print("this is mock cp", mock_cp)
        assert mock_cp.call_count == 1
        list, kwargs = mock_cp.call_args
        print(list[0], kwargs)
        assert list[0][0] == 'asciidoctor'
        assert list[0][-1] == 'c:/some/path/file.adoc'
        self.posts.insert.assert_called()
        req.execute.assert_called()
