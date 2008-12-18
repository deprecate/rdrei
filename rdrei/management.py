# -*- coding: utf-8 -*-
"""
 <{rdrei.management}>
 ~~~~~~~~~~~~~~~~
 Mangement scripts for creating new rdrei instances.


 :copyright: 2008 by Pascal Hartig <phartig@rdrei.net>
 :license: GPL, see doc/LICENSE for more details.
 """

from werkzeug import Template
import os, re, shutil

class TemplateCommand(object):
    vars = (
        ('appname', "Application Name", 'string'),
        ('debug_enabled', "Enable debug mode? (recommended)", 'bool', True),
    )

    answers = dict()

    def _ask_vars(self):
        for var in self.vars:
            if len(var) == 3:
                name, desc, type = var
                default = None
            elif len(var) == 4:
                name, desc, type, default = var
            else:
                raise RuntimeException("Got unexpected parameter length.")
            
            message = desc
            if default:
                message += " [%r]: " % default
            else:
                message += ": "
            while True:
                answer = raw_input(message)
                if not answer:
                    if default:
                        answer = default
                        break
                else:
                    if type == "bool":
                        answer = answer in ('true', 'True', '1','on', 'yes')
                    if name == "appname":
                        answer = answer.strip()
                        if ' ' in answer:
                            print("Application name must not contain spaces.")
                            continue
                        if not re.compile("[a-z0-9-_]+").match(answer):
                            print("Application name must only contain "
                                  "alphanumeric values, _ and -.")
                            continue
                    break

            self.answers[name] = answer

    def _create_dir(self):
        appname = self.answers['appname']
        print("Creating project directory %s …" % appname)
        os.mkdir(appname)

    def _copy_templates(self):
        appname = self.answers['appname']
        origin = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                              "project_templates"))
        os.chdir(appname)
        for fname in os.listdir(os.path.join(origin, "base")):
            print("Creating %s …" % fname)
            self._patchcopy(os.path.join(origin, "base", fname), fname)

        print("Creating project folder …")
        shutil.copytree(os.path.join(origin, "application"),
                        appname)
        print("Done.")

    def _patchcopy(self, fname, target):
        tmpl = open(fname, 'r+')
        dest = open(target, 'w')
        t = Template(tmpl.read())
        dest.write(t.render(self.answers))
        tmpl.close()
        dest.close()

    def run(self):
        print("Creating new rdrei project.")
        self._ask_vars()
        self._create_dir()
        self._copy_templates()

if __name__ == '__main__':
    TemplateCommand().run()