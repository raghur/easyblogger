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
            PostId: "234"
            Published: false
            PublishDate: 2018-01-01T10:00:00
            -->
        """
        parser = blogger.ContentArgParser(theFile)
        args = Mock()
        parser.updateArgs(args)

        assert args.title == "t"
        assert args.labels == ["l"]
        assert args.postId == "234"
        assert args.format == "markdown"
        assert args.command == "update"
        assert args.publishDate.isoformat() == "2018-01-01T10:00:00"
        assert args.publish == False

    def test_should_infer_args_for_post(self):
        theFile = Mock()
        theFile.read.return_value = """
            <!--
            Title: t
            Labels: l
            Published: true
            PublishDate: 2018-01-01T10:00:00
            -->
        """
        parser = blogger.ContentArgParser(theFile)
        args = Mock()
        parser.updateArgs(args)

        assert args.publishDate.isoformat() == "2018-01-01T10:00:00"
        assert args.title == "t"
        assert args.labels == ["l"]
        assert args.format == "markdown"
        assert args.command == "post"
        assert args.publish

    def test_should_infer_args_from_toml_header(self):
        theFile = Mock()
        theFile.read.return_value = """
+++
title= "t"
id= "1234"
tags= ["l", "a", "c"]
publishdate=2018-01-01T10:00:00
+++

this is the post
        """
        parser = blogger.ContentArgParser(theFile)
        args = Mock()
        parser.updateArgs(args)

        assert args.title == "t"
        assert args.labels == ["l", "a", "c"]
        assert args.format == "asciidoc"
        assert args.command == "update"
        assert args.publishDate.isoformat() == "2018-01-01T10:00:00"
        assert not args.publish

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
        print(args.labels)
        assert args.labels == ["l", "a", "c"]
        assert args.format == "markdown"
        assert args.command == "post"
        assert not args.publish

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
        assert args.labels == ["untagged"]
        assert args.format == "markdown"
        assert args.command == "post"
        assert not parser.publishDate
        assert not args.publish

    def test_should_handle_empty_file(self):
        theFile = Mock()
        fileContent = """
            <!--
            -->
abc"""
        theFile.read.return_value = fileContent
        parser = blogger.ContentArgParser(theFile)
        args = Mock()
        parser.updateArgs(args)

        assert args.title is None
        assert args.labels == ["untagged"]
        assert args.format == "markdown"
        assert args.command == "post"
        assert args.content == "\nabc"
        assert not parser.publishDate
        assert not args.publish

    def test_should_allow_format_to_be_specified(self):
        theFile = Mock()
        fileContent = """<!--
            Format : markdown_strict

            -->
abc"""
        theFile.read.return_value = fileContent
        parser = blogger.ContentArgParser(theFile)
        args = Mock()
        parser.updateArgs(args)

        assert args.title is None
        assert args.labels == ['untagged']
        assert args.format == "markdown_strict"
        assert "\n" not in args.format
        assert args.command == "post"
        assert args.content == "\nabc"
        assert not args.publish

    def test_should_update_doc_with_postid(self):
        def validateFileContent(content):
            # print(content)
            assert content.index("1000") > 0
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
        args = Mock()
        parser.updateArgs(args)
        parser.updateFileWithPostId("1000")

        mock_open.assert_called_with(theFile.name, "w")
        fileHandle.flush.assert_called()
        fileHandle.write.assert_called()
