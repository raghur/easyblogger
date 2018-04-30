EasyBlogger
===========

[![Build Status](https://travis-ci.org/raghur/easyblogger.svg?branch=master)](https://travis-ci.org/raghur/easyblogger)
[![Coverage Status](https://coveralls.io/repos/github/raghur/easyblogger/badge.svg?branch=master)](https://coveralls.io/github/raghur/easyblogger?branch=master)
[![PyPI](https://img.shields.io/pypi/v/easyblogger.svg)](https://pypi.python.org/pypi/easyblogger)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/Easyblogger.svg)](https://pypi.python.org/pypi/easyblogger)
[![Updates](https://pyup.io/repos/github/raghur/easyblogger/shield.svg)](https://pyup.io/account/repos/github/raghur/easyblogger/)

Blog to blogger from the command line.

Why not googlecl?
-----------------

I tried. Didn't work. `googlecl` is just too rough and isn't easy to
script. For ex:

1.  No way to update a post
2.  Doesn't work with blog and post ids.
3.  and others...

So what does this do?
---------------------

1.  Provides a command line tool and create, update or delete posts on
    Blogger hosted blogs.
2.  Post content can be piped in - so you can use your favourite way to
    generate html markup
3.  Pandoc goodness - so that you can write your doc in any of the input
    formats that Pandoc supports
3.  More Pandoc goodness - supports pandoc filters so you can do nice things like
    create diagrams with [`mermaid-filter`](https://github.com/raghur/mermaid-filter)
4.  AsciiDoc support - Supports asciidoc as a source format as well using
    `asciidoctor` & `asciidoctor-diagram`
4.  You can also export your existing posts to your favourite
    lightweight markup format like markdown etc as individual files.
    Then edit them in a real editor, and publish them back! All pandoc
    output formats!
5.  Understands specially marked comments - so you can just hand it a
    file and it'll figure out what to do - great for posting from vim
    etc.

Installation, Configuration and Usage
=====================================

Installation
------------

``` {.sourceCode .bash}
# Now live on PyPI
sudo pip install EasyBlogger
```

This installs EasyBlogger and its dependencies. It also installs the
`easyblogger` script

### Pandoc

Install [pandoc](http://johnmacfarlane.net/pandoc/installing.html) If
you're on cygwin, you can just install the windows dl and put
`pandoc.exe` somewhere on path

OAuth2 API Authentication and Authorization
-------------------------------------------

The tool needs to be granted access to manage the blog. Google APIs use
OAuth2.

1.  First, get your blog id. You can find the blog id by viewing the
    source. For ex. on my blog, I have the following lines near the top:

    ``` {.sourceCode .html}
    <link rel="alternate" type="application/atom+xml" title="Nifty Tidbits - Atom" href="http://blog.rraghur.in/feeds/posts/default" />
    <link rel="alternate" type="application/rss+xml" title="Nifty Tidbits - RSS" href="http://blog.rraghur.in/feeds/posts/default?alt=rss" />
    <link rel="service.post" type="application/atom+xml" title="Nifty Tidbits - Atom" href="http://www.blogger.com/feeds/7642453/posts/default" />
    ```

    On the last link, the number `7642453` is the blogId

2.  Authorize

    **On Linux**

    ``` {.sourceCode .bash}
    # run through OAuth2 hoops... following needs to be run as root
    # First find your blog Id

    easyblogger --blogid <yourblogid> get

    # This will first open a browser and ask you to sign in and
    # approve access to your blog
    ```

    This will open a browser. You may see a chrome warning that it can't
    be run as root - but you can ignore that. Once you authorize,
    `~/.easyblogger.credentials` is created with your OAuth2 token


    **On Windows**

    If your `PATH` variable has the python Scripts folder, then you
    should just be able to run `easyblogger --blogid <id> get` in a
    command window. If not, then open a `cmd` window and navigate to
    `<python install folder>\Scripts` and run
    `python easyblogger --blogid <yourblogid> get`

3.  All set!

    That's it - you're all set!

    You will need to repeat the OAuth2 authorization process if you ever
    change the blog, or revoke permissions or if the auth token expires.

VIM Configuration
-------------------

1. Stick the following in your `~/.vimrc`
```vim
func! s:systemwrapper(cmd)
    echom a:cmd
    let output=system(a:cmd)
    return output
endfunction
func! BlogSave(file)
    " to debug, replace with
    " exec "!easyblogger file " . a:file
    let output=s:systemwrapper("easyblogger file ". a:file)
    echom output
endfunction
command! BlogSave call BlogSave(expand("%:p"))
```

1. Start writing a post - create a markdown file (.md) with frontmatter in a comment
```markdown
<!--
id:
title    : title
labels   : [any, comma, separated, labels]
format	 : markdown
published: true
filters: <path to your filter>
-->
```
Note that as of Easyblogger 3.0, the preferred frontmatter format is borrowed from Hugo.
The original frontmatter header in earlier versions is deprecated. However, if `easyblogger`
finds header using the older keys, then it will use them.
While there should be no reason to prefer the old format, if you need that for whatever
reason, you must specify `--legacy-frontmatter` flag in the `get` subcommand. For more
details, refer to the Frontmatter section

*LEGACY FRONTMATTER FORMAT*
__still supported but you're encouraged to use the new format__
```
<!--
PostId:
Title    : title
Labels   : any, comma, separated, labels
Format	 : markdown
Published: true
filters: <path to your filter>
-->
```

2. If you prefer using `asciidoc`, then use the following comment header:
```asciidoc
+++
id:
title    : title
labels   : [any, comma, separated, labels]
format	 : asciidoc
published: true
+++
```

*LEGACY FRONTMATTER FORMAT*
__still supported but you're encouraged to use the new format__
```asciidoc
////
PostId:
Title    : title
Labels   : any, comma, separated, labels
Format	 : asciidoc
Published: true
////
```

Asciidoc does not require filters - it has a better system of plugins. Just
ensure that you have installed `asciidoctor` and `asciidoctor-diagram` gems

1. When done, call `:BlogSave` and your blog will be published

Usage
-----

### Getting posts

1.  Get a list of posts post Id, title and url are output by default.

    ``` {.sourceCode .bash}
    # get a list of posts
    # param : Blog Id - look at your blog's atom pub url - its the number in the url.
    easyblogger --blogid 7642453 get

    4424091495287409038,Moving from Wordpress.com to Blogger,http://blog.rraghur.in/2013/08/moving-from-wordpresscom-to-blogger.html
    ...
    ...
    # 10 rows shown
    ```

2.  Filter by labels or search; specify `max` results to be returned.

    ``` {.sourceCode .bash}
    # get only the last 5 with tag 'vim'
    # you can specify multiple tags - separate them with commas
    easyblogger --blogid 7642453 get -l vim -c 5

    # search for all posts with 'vim'
    easyblogger --blogid 7642453 get -q vim -c 5
    ```

3.  Get a specific post by its id

    ``` {.sourceCode .bash}
    # get a specific post by id
    easyblogger --blogid 7642453 get -p 3728334747597998671
    ```

4.  Get a specific post by its url

    ``` {.sourceCode .bash}
    # get a specific post by url
    easyblogger --blogid 7642453 get -u https://blog.rraghur.in/2015/06/js-development-2015.html
    ```

5.  Control which fields are printed out.

    ``` {.sourceCode .bash}
    # output field control
    easyblogger  get -p 3728334747597998671 -f "id,title,url,labels"
    3728334747597998671,Rewriting history with Git,http://blog.rraghur.in/2012/12/rewriting-history-with-git.html,[u'git', u'HOWTO', u'Tips']
    ```

5.  Output in (lightweight) markup - very good for updates.
    -   If its a single post, then its printed to console.

        ``` {.sourceCode .bash}
        easyblogger --blogid 7642453 get -p 3728334747597998671 -d markdown
        ```

        It also includes a header that will allow you to edit the file
        and update the post back with the file subcommand below

    -   if more than one post, then each post is written to a file (name
        derived from the title)

        ``` {.sourceCode .bash}
        easyblogger --blogid 7642453 get -l vim -d markdown
        ```

    -   If you'd like to get a single post as a file, specific `-w` or
        `--write-files`

        ``` {.sourceCode .bash}
        easyblogger --blogid 7642453 get -p 3728334747597998671 -d markdown --write-files
        ```

    -   Supports all mark up formats supported by `pandoc`

        ``` {.sourceCode .bash}
        # Output formats: native, json, docx, odt, epub, epub3, fb2, html, html5, s5,
                 slidy, slideous, dzslides, docbook, opendocument, latex, beamer,
                 context, texinfo, man, markdown, markdown_strict,
                 markdown_phpextra, markdown_github, markdown_mmd, plain, rst,
                 mediawiki, textile, rtf, org, asciidoc
        ```

### Default Args file

Specifying --blogid each time is just painful. You can set a default
blogId by creating a default args file `~/.easyblogger` as follows:

``` {.sourceCode .bash}
cat > ~/.easyblogger
--blogid
234567
```

And now you can type the command as:

``` {.sourceCode .bash}
easyblogger get
```

You can override the args from file by providing the argument on the
command line

### Create a new blog post

Note: ~~Blogger API v3 does not support/expose API for creating posts as drafts. Please ask for this feature on Google's blogger dev group - I'll add that capability once/if it becomes available.~~

Blogs are created as drafts by default now. You can override this with the `--publish` flag
which will post the blog directly (current behavior)

``` {.sourceCode .bash}
# create a post from stdin with title and labels


easyblogger post -t "Hello World" -l "python,hello" -c "Hello world!!!"
```

Pipe out from any HTML generation mechanism

``` {.sourceCode .bash}
pandoc -f markdown -  | easyblogger   --blogid 6136696198547817747 post -t 'Hello from Pandoc' -f -
 # Hello from Pandoc
this is a nice long post

3295765957555899963
```

Or just tell easyblogger to convert from `markdown` with the --format
arg

``` {.sourceCode .bash}
# --format supports
#                native,json,markdown,
#                markdown_strict,markdown_phpextra,
#                markdown_mmd,rst,mediawiki,
#                docbook,textile,html,latex

easyblogger post -t 'Hello from Pandoc' --format markdown -c "##heading2"

2342323423423423423
```

### Update posts

Update works with a patch request - only specify what you need changed
Blogger API does not allow the blog permalink to be updated - so in case
you want to change that you'll need to delete and create another post
(though you will probably lose comments etc - so only viable if you've
just published it)

``` {.sourceCode .bash}
easyblogger update -t 'A new title' -l "new,labels" 3295765957555899963
```

You can also update the contents by passing in the `--file` argument.
Piping it in works too - use `--file -`; like so

``` {.sourceCode .bash}
pandoc -f markdown -  | easyblogger  update -t 'Hello from Pandoc' --file - 3295765957555899963
# This is h1
## this is h2

Some para text
[EOF]
```

### Posting or Updating from a file

I wrote `easyblogger` script primarily so I can blog from Vim. If your
file has properly formatted comments, then `EasyBlogger` will figure out
what to do (insert or update) based on the metadata.

So, you can author a post like so:

``` {.sourceCode .bash}
cat MyBlogPost.md
<!--
Title: This is your title
PostId:
Labels: a,b,c
format: markdown
published: false
filters: <path to your installed filter>
-->
# This is my content
```
The example above uses legacy frontmatter format. You're encouraged to use the new
format which allows for additional metadata.

And post it to your blog like so:

``` {.sourceCode .bash}
easyblogger file MyBlogPost.md
```

And `easyblogger` will update your post doc back with the `postId` of
the generated post. Now, if you edit the doc and publish again with the
same command, your post will be updated.

### Deleting posts

To delete posts, you need to specify the post id

``` {.sourceCode .bash}
easyblogger delete 234546720561632959
```

Frontmatter
==============

As you've seen, easyblogger relies on a comment header with specific keys for
metadata about the post as well as to drive the behavior of the program.
When `EasyBlogger` started, I had come up with my own set of (minimal) keys.
Somewhere in the 2.x days, I built support for the frontmatter format as defined
in Hugo project(along with some specific keys used for Blogger) - this is especially
useful if you want to migrate off Blogger to Hugo.

The header format can be either TOML or YAML. The new frontmatter keys are the default both for input and output.

Output Rules
--------------
When writing to output files with `get`, easyblogger will write the header in
1. Document format - asciidoc: Header in TOML enclosed by `+++`
2. Legacy header keys - only if the command line specifies the `--legacy-frontmatter` flag

Input Rules
-------------
1. Header enclosed with `+++` - parse as TOML
2. Header encosed with HTML comment or `////` - parse as YAML
3. If doc is TOML, then default format is supposed to be 'asciidoc' if not specified.
4. If doc is YAML, then default format is supposed to be 'markdown' if not specified.

If any of the legacy frontmatter keys (`Title`, `PostId` etc) are present, then the legacy keys
are expected. Otherwise the new style Hugo compliant headers are expected.

### Frontmatter keys

* New style (Hugo)
    ```toml
    +++
    title = "Proxy PAC file for work"
    id = "293493242234"
    tags = [ "Rants", "Tips", "Utilities",]
    aliases = [ "http://niftybytes.blogspot.com/2018/04/proxy-pac-file-for-work_30.html",]
    publishdate = "2018-04-30T12:42:00+05:30"
    draft = false
    date = "2018-04-30T12:42:00+05:30"
    lastmod = "2018-04-30T12:47:37+05:30"
    +++
    ```
* Old style (Easyblogger)
    ```
    <!--
    Labels: [Rants, Tips, Utilities]
    PostId: '8010087245053438499'
    Published: true
    Title: Proxy PAC file for work
    -->
    ```

Using EasyBlogger as a library
==============================

Using EasyBlogger class
-----------------------

Feel free to use the EasyBlogger class in your own tool/utility whatever
else. Just remember:

1.  Use your own API client id (see below)
2.  Include an attribution and a link to EasyBlogger - not mandatory
    -but just be nice:)

### Client API ids

If you're using EasyBlogger class in your tool/utility, please then
register for API access at [Google's API
console](https://code.google.com/apis/console). Create a client id and
secret key at the API access page and request for Blogger API access.
Once you have API access authorized, you're good to get started. Just
create the `EasyBlogger` constructor with your client id and secret

If you're integrating by shelling out, then stick the API key and client
id in the command line with `--clientid` and `--secret` args. You can
also stick them in the `~/.easyblogger` file to avoid specifying them
each time

Dev Guide
=========

1.  Clone the repo
2.  Start a virtualenv - `virtualenv .dev`
3.  Activate it - `.dev\Scripts\activate`
4.  Install dependencies - `pip install -r requirements.txt`
5.  `pip install -e .`

### Running tests

1.  Exit out of any virtualenvs
2.  Run `tox`



