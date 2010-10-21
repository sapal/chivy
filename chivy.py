# coding=utf-8
import chivySources.config
import start
import sys
import codecs
if __name__ == "__main__":
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf8')(sys.stderr)
    start.main()
