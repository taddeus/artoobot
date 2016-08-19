#!/usr/bin/env python
import sys
from translate import request_audio, read_request


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print >>sys.stderr, 'Usage: python %s MESSAGE' % sys.argv[0]
        sys.exit(1)

    message = ' '.join(sys.argv[1:])
    sys.stdout.write(read_request(request_audio(message)))
