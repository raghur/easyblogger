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

~~~bash
sudo easy_install httplib2 python-gflags google-api-python-client
~~~

* Authorize the tool API access to your blog

~~~bash
# run through OAuth2 loops... following needs to be run as root
# First find your blog Id
cd /path/to/install
python blogger.py --blogid <yourblogid> get
# This will first open a browser and ask you to sign in and 
# approve access to your blog
~~~

Special notes for Linux:
This will open a browser. You may see a chrome warning that it can't 
be run as root - but you can ignore that.
Once you authorize, you will see a file 'credentials.dat' in the folder

since the file is created as root, you will need to change ownership of the 
credentials.dat file. 
you will need to repeat  this process if you ever change the blog, or revoke 
permissions or if the auth token expires.

~~~bash
# Change ownership
sudo chown <youruser>:<youruser> credentials.dat
~~~

That's it - you're all set!


## Usage

###Getting a list of posts
~~~bash
# get a list of posts
# param : Blog Id - look at your blog's atom pub url - its the number in the url.
blogger.py --blogid 7642453 get 

4424091495287409038,Moving from Wordpress.com to Blogger,http://blog.rraghur.in/2013/08/moving-from-wordpresscom-to-blogger.html
...
...
# 10 rows shown

# get only the last 5 with tag 'vim'
# you can specify multiple tags - separate them with commas
blogger.py --blogid 7642453 get -l vim -c 5

# search for all posts with 'vim'
blogger.py --blogid 7642453 get -q vim -c 5

# get a specific post by id
blogger.py --blogid 7642453 get -p 3728334747597998671

# output field control
raghu@desktop:~/code/vim-blogger > src/blogger.py  get -p 3728334747597998671 -f "id,title,url,labels"
3728334747597998671,Rewriting history with Git,http://blog.rraghur.in/2012/12/rewriting-history-with-git.html,[u'git', u'HOWTO', u'Tips']
~~~

### Create a new blog post

Note: Blogger API v3 does not allow creating posts as drafts. Please ask/crib about this - I'll add that capability once it becomes available.

~~~bash
# create a post from stdin with title and labels
raghu@desktop:~/code/vim-blogger > src/blogger.py --blogid 6136696198547817747 post -t "Hello World" -l "python,hello" -
Hello world!!!
4345108299270352601

# pipe out from pandoc
pandoc -f markdown -  | src/blogger.py   --blogid 6136696198547817747 post -t 'Hello from Pandoc' 
# Hello from Pandoc
this is a nice long post

3295765957555899963
~~~

### Update posts

Update works with a patch request - only specify what you need changed
Blogger API does not allow the blog permalink to be updated - so in case you want to change that you'll need to delete and create another post (though you will probably lose comments etc - so only viable if you've just published it)

~~~bash
src/blogger.py   --blogid 6136696198547817747 update -t 'A new title' -l "new,labels" 3295765957555899963

# you can also update the contents by passing in the --file argument

# pipe it in too - use --file -; like so

pandoc -f markdown -  | src/blogger.py   --blogid 6136696198547817747 update -t 'Hello from Pandoc' --file - 3295765957555899963 
~~~

### Deleting posts

To delete posts, you need to specify the post id

~~~bash
src/blogger.py   --blogid 6136696198547817747 delete 234546720561632959 
~~~
