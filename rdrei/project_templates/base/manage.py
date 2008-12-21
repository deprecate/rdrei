#!/usr/bin/env python
from werkzeug import script
from rdrei.management import make_controller

import logging

def make_app():
    from rdrei.application import RdreiApplication
    # Choose another config file name, to provide a debug environment.
    return RdreiApplication("config.ini")

def make_shell():
    from rdrei import utils
    from ${appname} import models
    application = make_app()
    return locals()

def setup_logging():
    logging.basicConfig(level=logging.DEBUG,
                    format="[%(asctime)s::%(levelname)s] "\
                    "%(filename)s:%(lineno)d:%(funcName)s: %(message)s",
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='/tmp/rdrei.log',
                    filemode='w')


action_runserver = script.make_runserver(make_app, use_reloader=True,
                                         use_debugger=True)
action_shell = script.make_shell(make_shell)
action_initdb = lambda: make_app().init_database()
action_controller = make_controller()

if __name__ == '__main__':
    setup_logging()
    script.run()

