import re
import settings


def sanitize(string):
    return re.sub("\W+", "", string)


def printVerbose(*args):
    if settings.verbose:
        print(*args)
