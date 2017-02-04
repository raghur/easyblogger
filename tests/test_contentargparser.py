from unittest import TestCase
from mock import DEFAULT, MagicMock, Mock
from blogger import blogger


class ContentArgParserTests(TestCase):

    def test_should_infer_args_from_content(self):
        theFile = Mock()
        theFile.read.return_value = """
            <!--
            Title: t
            Labels: l
            PostId: 234
            -->
        """
        parser = blogger.ContentArgParser(theFile)
        args = Mock()
        parser.updateArgs(args)

        assert args.title == "t"
        assert args.labels == "l"
        assert args.postId == "234"
        assert args.format == "markdown"
        assert args.command == "update"

    def test_should_infer_args_for_post(self):
        theFile = Mock()
        theFile.read.return_value = """
            <!--
            Title: t
            Labels: l
            -->
        """
        parser = blogger.ContentArgParser(theFile)
        args = Mock()
        parser.updateArgs(args)

        assert args.title == "t"
        assert args.labels == "l"
        assert args.format == "markdown"
        assert args.command == "post"

    def test_should_infer_args_for_post2(self):
        theFile = Mock()
        theFile.read.return_value = """
            <!--
            Title: t
            PostId:
            Labels: l, a, c
            -->
        """
        parser = blogger.ContentArgParser(theFile)
        args = Mock()
        parser.updateArgs(args)

        assert args.title == "t"
        assert args.labels == "l, a, c"
        assert args.format == "markdown"
        assert args.command == "post"

    def test_should_infer_args_for_post3(self):
        theFile = Mock()
        theFile.read.return_value = """
            <!--
            Title: t
            PostId:
            Labels:
            -->
        """
        parser = blogger.ContentArgParser(theFile)
        args = Mock()
        parser.updateArgs(args)

        assert args.title == "t"
        assert args.labels == ""
        assert args.format == "markdown"
        assert args.command == "post"

    def test_should_handle_empty_file(self):
        theFile = Mock()
        fileContent = """
            <!--
            -->
        """
        theFile.read.return_value = fileContent
        parser = blogger.ContentArgParser(theFile)
        args = Mock()
        parser.updateArgs(args)

        assert args.title is None
        assert args.labels is None
        assert args.format == "markdown"
        assert args.command == "post"
        assert args.content == fileContent

    def test_should_allow_format_to_be_specified(self):
        theFile = Mock()
        fileContent = """
            <!--
            format : markdown_strict

            -->
        """
        theFile.read.return_value = fileContent
        parser = blogger.ContentArgParser(theFile)
        args = Mock()
        parser.updateArgs(args)

        assert args.title is None
        assert args.labels is None
        assert args.format == "markdown_strict"
        assert "\n" not in args.format
        assert args.command == "post"
        assert args.content == fileContent

    def test_should_update_doc_with_postid(self):
        def validateFileContent(content):
            print(content)
            assert blogger.ContentArgParser.rePostId.search(content)
            return DEFAULT

        fileContent = """
            <!--
            PostId:
            format: markdown_strict
            -->
        """
        try:
            from io import RawIOBase
            file = RawIOBase
        except ImportError:
            # do nothing
            pass
        theFile = MagicMock(spec=file)
        theFile.name = "thefilename"
        theFile.read.return_value = fileContent

        mock_open = Mock()
        mock_open.return_value = theFile
        fileHandle = theFile.__enter__.return_value
        fileHandle.write.side_effect = validateFileContent

        parser = blogger.ContentArgParser(theFile, open=mock_open)
        parser.updateFileWithPostId("1000")

        mock_open.assert_called_with(theFile.name, "w")
        fileHandle.flush.assert_called()
        fileHandle.write.assert_called()
