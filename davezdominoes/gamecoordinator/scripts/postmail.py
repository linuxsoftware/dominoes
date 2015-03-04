#!/bin/env python
import sys
import logging

from repoze.sendmail.queue import ConsoleApp

def main():
    logging.basicConfig(format='%(asctime)s %(message)s')
    app = ConsoleApp(argv=sys.argv)
    # fix up the debug_smtp flag... did this actualy work in Py2?
    if (not app.mailer.debug_smtp or 
        app.mailer.debug_smtp.lower() in ("false", "0", "none", "no", "off")):
        app.mailer.debug_smtp = 0
    else:
        app.mailer.debug_smtp = 1
    try:
        app.main()
    except ConnectionRefusedError:
        print("Cannot connect to mail socket")

if __name__ == '__main__':
    main()
