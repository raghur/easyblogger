import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name="EasyBlogger",
      version="2.1.2",
      author="Raghu Rajagopalan",
      author_email="raghu.nospam@gmail.com",
      description=("A (very) easy CLI interface to Blogger blogs"),
      license="BSD",
      keywords="blogger, cli, markdown, asciidoc",
      url="https://github.com/raghur/easyblogger",
      packages=['blogger'],
      install_requires=[
          'pypandoc',
          'google-api-python-client',
          'python-gflags',
          'httplib2',
          'toml',
          'gevent',
          'coloredlogs',
          'chardet'
      ],
      entry_points={
          'console_scripts': [
              'easyblogger = blogger.main:main'
          ]
      },
      long_description=readme(),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Topic :: Utilities",
          "Topic :: Internet :: WWW/HTTP :: Site Management",
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6"
      ],
      )
