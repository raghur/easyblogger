import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name="EasyBlogger",
      version="0.9.0",
      author="Raghu Rajagopalan",
      author_email="raghu.nospam@gmail.com",
      description=("A (very) easy CLI interface to Blogger blogs"),
      license = "BSD",
      keywords = "blogger, cli",
      url = "https://bitbucket.org/raghur/easyblogger",
      packages=['blogger'],
      install_requires = [
          'pypandoc',
          'google-api-python-client',
          'python-gflags',
          'httplib2'
      ],
      entry_points = {
          'console_scripts': [
    'easyblogger = blogger.blogger:main'
                         ]
                     },
      long_description='see https://bitbucket.org/raghur/easyblogger',
      classifiers=[
          "Development Status :: 4 - Beta",
          "Topic :: Utilities",
          "License :: OSI Approved :: BSD License",
          ],
)
