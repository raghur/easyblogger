import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
        name = "blogger-cli",
        version = "0.0.4",
        author = "Raghu Rajagopalan",
        author_email = "raghu.nospam@gmail.com",
        description = ("CLI interface to Blogger blogs"),
        license = "BSD",
        keywords = "blogger, cli",
        url = "http://packages.python.org/an_example_pypi_project",
        packages=['blogger'],
        install_requires = [
            'pypandoc',
            'google-api-python-client',
            'python-gflags',
            'httplib2'
            ],
        scripts = ['blogger/blogger'],
        long_description=read('README.md'),
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Topic :: Utilities",
            "License :: OSI Approved :: BSD License",
            ],
)
