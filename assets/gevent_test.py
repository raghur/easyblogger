import sys
import pypandoc
import gevent
from gevent import monkey
from io import open
import argparse

monkey.patch_all()

# passing input via stdin seems problematic with pypandoc (and internally,
# Subprocess) on windows. It just hangs. OTOH, passing a real file in seems to
# fix the problem and spawned processes don't hang anymore

# >d:\sdks\python3\python gevent_test.py -f file1.html -c 20 --stdin
# Namespace(count=20, file='file1.html', stdin=True)
# KeyboardInterrupt
# Thu May 25 11:24:32 2017
# Traceback (most recent call last):

# >d:\sdks\python3\python gevent_test.py -f file1.html -c 20
# Namespace(count=20, file='file1.html', stdin=False)

def convert(file, stdin, instanceid):
    if stdin:
        text = ""
        with open(file, 'r') as filehandle:
            text = filehandle.read()
        # this fails
        pypandoc.convert_text(text, "asciidoc",
                              format="html",
                              outputfile="%s.asciidoc" % instanceid)
    else:  # this works
        output = pypandoc.convert_file(file, "asciidoc",
                                       format="html")


def main(sysargv=sys.argv):
    args = parse_args(sysargv[1:])
    print(args)
    jobs = [gevent.spawn(convert, args.file, args.stdin, i)
            for i in range(args.count)]
    gevent.wait(jobs)


def parse_args(sysargv):
    parser = argparse.ArgumentParser(
        prog='gevent_test',
        description="Easily manage posts on Blogger blogs",
        fromfile_prefix_chars='@')
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        help="number of processes to spawn",
        default=10)

    parser.add_argument(
        "-f",
        "--file",
        help="file to convert")

    parser.add_argument(
        "--stdin",
        action='store_true',
        default=False,
        help="Pass input as text via stdin")
    args = parser.parse_args(sysargv)
    return args


if __name__ == '__main__':
    # print sys.argv
    main(sys.argv)
