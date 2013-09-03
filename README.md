# EasyBlogger
Blog to blogger from the command line.


## Why not googlecl?
I tried. Didn't work. `googlecl` is just too rough and isn't easy to script. For ex:

1. No way to update a post
2. Doesn't work with blog and post ids.
3. and others...

## So what does this do?
Uses Blogger api via  `gdata-python-client` to provide you a cli tool to create, update, delete posts on Blogger.

# Installation, Configurationa and Usage

## Installation

~~~bash
pip install git+https://raghur@bitbucket.org/raghur/easyblogger#egg=EasyBlogger
~~~
This installs EasyBlogger and its dependencies. It also installs the `easyblogger` script
2. Pandoc
Install [pandoc](http://johnmacfarlane.net/pandoc/installing.html)
If you're on cygwin, you can just install the windows dl and put `pandoc.exe` somewhere on path

## OAuth2 API Authentication and Authorization
~~~bash
 # run through OAuth2 hoops... following needs to be run as root
 # First find your blog Id

 easyblogger --blogid <yourblogid> get

 # This will first open a browser and ask you to sign in and
 # approve access to your blog
~~~

###Windows:

You might have to do `python easyblogger --blogid <yourblogid> get` from the Scripts folder

###Linux:

This will open a browser. You may see a chrome warning that it can't
be run as root - but you can ignore that.
Once you authorize, `~/.easyblogger.credentials` is created with your OAuth2 token

Since the file is created as root, you will need to change ownership of the
`~/.easyblogger.credentials` file.

~~~bash
 # Change ownership
sudo chown <youruser>:<youruser> ~/.easyblogger.credentials
~~~
You will need to repeat  this process if you ever change the blog, or revoke
permissions or if the auth token expires.

That's it - you're all set!


## Usage

### Getting a list of posts

~~~bash
 # get a list of posts
 # param : Blog Id - look at your blog's atom pub url - its the number in the url.
 easyblogger --blogid 7642453 get

 4424091495287409038,Moving from Wordpress.com to Blogger,http://blog.rraghur.in/2013/08/moving-from-wordpresscom-to-blogger.html
 ...
 ...
 # 10 rows shown

 # get only the last 5 with tag 'vim'
 # you can specify multiple tags - separate them with commas
 easyblogger --blogid 7642453 get -l vim -c 5

 # search for all posts with 'vim'
 easyblogger --blogid 7642453 get -q vim -c 5

 # get a specific post by id
 easyblogger --blogid 7642453 get -p 3728334747597998671

 # output field control
 easyblogger  get -p 3728334747597998671 -f "id,title,url,labels"
3728334747597998671,Rewriting history with Git,http://blog.rraghur.in/2012/12/rewriting-history-with-git.html,[u'git', u'HOWTO', u'Tips']
~~~

### Default Args file
Specifying --blogid each time is just painful.

you can create a default args file in `~/.easyblogger` as follows:

~~~bash
cat > ~/.easyblogger
--blogid
234567
~~~

And now you can type the command as:

~~~bash
easyblogger get
~~~
You can override the args from file by providing the argument on the command line

### Create a new blog post

Note: Blogger API v3 does not support/expose API for creating posts as drafts.
Please ask for this feature on Google's blogger dev group - I'll add that capability once it becomes available.

~~~bash
 # create a post from stdin with title and labels
easyblogger --blogid 6136696198547817747 post -t "Hello World" -l "python,hello" -
Hello world!!!
4345108299270352601

 # pipe out from pandoc or any other conversion - choose your poison
pandoc -f markdown -  | easyblogger   --blogid 6136696198547817747 post -t 'Hello from Pandoc'
 # Hello from Pandoc
this is a nice long post

3295765957555899963

 # Or just tell easyblogger to convert markdown using pandoc with the --md arg
easyblogger   --blogid 6136696198547817747 post -t 'Hello from Pandoc' --md -f -
Type anything in markdown

2342323423423423423
~~~

### Posting or Updating from a file

I wrote `EasyBlogger` primarily so I can blog from Vim. If your file has properly formatted comments, then
it will `EasyBlogger` will figure out what to do (insert or update) based on the metadata.

So, given a file like this:
~~~bash
    cat MyBlogPost.md
    <!--
    Title: This is your title
    PostId:
    Labels: a,b,c
    format: markdown
    -->
    # This is my content
~~~

You can post this to your blog like so:

~~~bash
    easyblogger file MyBlogPost.md
~~~
Once its posted, the tool will also update the `MyBlogPost.md` file with the `postId` of the generated post

### Update posts

Update works with a patch request - only specify what you need changed
Blogger API does not allow the blog permalink to be updated - so in case you want to change that you'll need to delete and create another post (though you will probably lose comments etc - so only viable if you've just published it)

~~~bash
 easyblogger update -t 'A new title' -l "new,labels" 3295765957555899963

 # you can also update the contents by passing in the --file argument

 # pipe it in too - use --file -; like so

 pandoc -f markdown -  | easyblogger  update -t 'Hello from Pandoc' --file - 3295765957555899963
 # This is h1
 ## this is h2

 Some para text
 [EOF]
~~~


### Deleting posts

To delete posts, you need to specify the post id

~~~bash
easyblogger delete 234546720561632959
~~~


# Using EasyBlogger as a library

## Using EasyBlogger class
Feel free to use the EasyBlogger class in your own tool/utility whatever else. Just remember:

1. Use your own API client id (see below)
2. Include an attribution and a link to EasyBlogger - not mandatory - but just be nice:)

### Client API ids
If you're using EasyBlogger class in your tool/utility, please  then register for API access at [Google's API console](https://code.google.com/apis/console). Create a client id and secret key at the API access page and request for Blogger API access. Once you have API access authorized, you're good to get started. Just create the `EasyBlogger` constructor with your client id and secret

If you're integrating by shelling out, then stick the API key and client id in the command line with `--clientid` and `--secret`
args. You can also stick them in the `~/.easyblogger` file to avoid specifying them each time
