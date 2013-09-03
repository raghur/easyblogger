from unittest import TestCase
from mock import Mock, DEFAULT, call
from blogger import blogger
from apiclient.errors import HttpError

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

    def test_should_handle_empty_file(self):
        theFile = Mock()
        fileContent= """
            <!-- 
            -->
        """
        theFile.read.return_value = fileContent
        parser = blogger.ContentArgParser(theFile)
        args = Mock()
        parser.updateArgs(args)

        assert args.title == None
        assert args.labels == None
        assert args.format == "markdown"
        assert args.command == "post"
        assert args.content == fileContent

    def test_should_allow_format_to_be_specified(self):
        theFile = Mock()
        fileContent= """
            <!-- 
            format: markdown_strict
            -->
        """
        theFile.read.return_value = fileContent
        parser = blogger.ContentArgParser(theFile)
        args = Mock()
        parser.updateArgs(args)

        assert args.title == None
        assert args.labels == None
        assert args.format == "markdown_strict"
        assert args.command == "post"
        assert args.content == fileContent
