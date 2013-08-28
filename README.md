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
cd /path/to/install
python blogger.py 132424086208.apps.googleusercontent.com DKEk2rvDKGDAigx9q9jpkyqI 7642453

# On Linux:
# this will open a browser. You may see a chrome warning that it can't 
# be run as root - but you can ignore that.
# chrome will start up and you will need to log in to your google account 
# and authorize the permission request.
# Once you authorize, you will see a file 'credentials.daT' in the folder.
# run the following
# you will need to repeat the above if you ever change the blog, or revoke 
# permissions or if the auth token expires.

sudo chown <youruser>:<youruser> credentials.dat
~~~

* Try out a call
Sample call
~~~bash
python blogger.py 132424086208.apps.googleusercontent.com DKEk2rvDKGDAigx9q9jpkyqI 7642453

# param 1: API key
# param 2: API secret
# param 3: Blog Id - look at your blog's atom pub url - its the number in the url.
~~~

