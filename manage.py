#!/usr/bin/env python
from werkzeug import script
from rdrei.management import make_project

action_project = make_project

if __name__ == '__main__':
    script.run()

