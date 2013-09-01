# Vim-Blogger

Blog to blogger with Vim.


## Why not googlecl?
I tried. Didn't work. `googlecl` is just too rough and isn't easy to script. For ex:

1. No way to update a post
2. Doesn't work with blog and post ids.
3. and others...

## So what does this do
Blogger integration is planned through `gdata-python-client` using gdata apis.


# Blogger.py

## Installation

* Install dependencies

1. From source

~~~bash
git clone https://bitbucket.org/raghur/vim-blogger
cd vim-blogger
python setup.py install
~~~

2. Pandoc
Install [pandoc](http://johnmacfarlane.net/pandoc/installing.html)

If you're on cygwin, you can just install the windows dl and put `pandoc.exe` somewhere on path

* Authorize the tool API access to your blog

~~~bash
# run through OAuth2 hoops... following needs to be run as root
# First find your blog Id

blogger --blogid <yourblogid> get

# This will first open a browser and ask you to sign in and 
# approve access to your blog
~~~

###Windows: 
you might have to do python blogger --blogid <yourblogid> get from the Scripts folder

###Linux:

This will open a browser. You may see a chrome warning that it can't 
be run as root - but you can ignore that.
Once you authorize, you will see a file '~/vim-blogger.credentials' in the folder

since the file is created as root, you will need to change ownership of the 
'~/vim-blogger.credentials' file. 
you will need to repeat  this process if you ever change the blog, or revoke 
permissions or if the auth token expires.

~~~bash
# Change ownership
sudo chown <youruser>:<youruser> ~/vim-blogger.credentials 
~~~

That's it - you're all set!


## Usage

###Getting a list of posts

~~~bash
# get a list of posts
# param : Blog Id - look at your blog's atom pub url - its the number in the url.
blogger --blogid 7642453 get 

4424091495287409038,Moving from Wordpress.com to Blogger,http://blog.rraghur.in/2013/08/moving-from-wordpresscom-to-blogger.html
...
...
# 10 rows shown

# get only the last 5 with tag 'vim'
# you can specify multiple tags - separate them with commas
blogger --blogid 7642453 get -l vim -c 5

# search for all posts with 'vim'
blogger --blogid 7642453 get -q vim -c 5

# get a specific post by id
blogger --blogid 7642453 get -p 3728334747597998671

# output field control
blogger  get -p 3728334747597998671 -f "id,title,url,labels"
3728334747597998671,Rewriting history with Git,http://blog.rraghur.in/2012/12/rewriting-history-with-git.html,[u'git', u'HOWTO', u'Tips']
~~~

### Create a new blog post

Note: Blogger API v3 does not allow creating posts as drafts. Please ask/crib about this - I'll add that capability once it becomes available.

~~~bash
# create a post from stdin with title and labels
blogger --blogid 6136696198547817747 post -t "Hello World" -l "python,hello" -
Hello world!!!
4345108299270352601

# pipe out from pandoc or any other conversion - choose your poison
pandoc -f markdown -  | blogger   --blogid 6136696198547817747 post -t 'Hello from Pandoc' 
# Hello from Pandoc
this is a nice long post

3295765957555899963

# Or just tell blogger.py to convert markdown using pandoc with the --md arg
blogger   --blogid 6136696198547817747 post -t 'Hello from Pandoc' --md -f -
Type anything in markdown

2342323423423423423
~~~

### Update posts

Update works with a patch request - only specify what you need changed
Blogger API does not allow the blog permalink to be updated - so in case you want to change that you'll need to delete and create another post (though you will probably lose comments etc - so only viable if you've just published it)

~~~bash
blogger   --blogid 6136696198547817747 update -t 'A new title' -l "new,labels" 3295765957555899963

# you can also update the contents by passing in the --file argument

# pipe it in too - use --file -; like so

pandoc -f markdown -  | blogger   --blogid 6136696198547817747 update -t 'Hello from Pandoc' --file - 3295765957555899963 
# This is h1
## this is h2

Some para text
[EOF]
~~~

### Deleting posts

To delete posts, you need to specify the post id

~~~bash
blogger   --blogid 6136696198547817747 delete 234546720561632959 
~~~

## Default Args file
Specifying --blogid each time is just painful.

you can create a default args file in `~/.vim-blogger` as follows:

~~~bash
cat > ~/.vim-blogger
--blogid
234567
~~~

And now you can type the command as:

~~~bash
blogger get
~~~

### Client API ids
If you'd rather use your own API client ids rather than the ones in vim-blogger (aka mine), then register for API 
access at [Google's API console](https://code.google.com/apis/console). Create a client id and secret key at the API access 
page and request for Blogger API access. Stick the API key and client id in the command line with `--clientid` and `--secret`
args. You can also stick them in the `~/.vim-blogger` file to avoid specifying them each time
