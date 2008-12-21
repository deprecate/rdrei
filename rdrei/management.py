# -*- coding: utf-8 -*-
"""
 <{rdrei.management}>
 ~~~~~~~~~~~~~~~~
 Mangement scripts for creating new rdrei instances.


 :copyright: 2008 by Pascal Hartig <phartig@rdrei.net>
 :license: GPL, see doc/LICENSE for more details.
 """

from werkzeug import Template
import os, re, shutil, sys

__all__ = ['Command', 'TemplateCommand']

class Command(object):
    answers = dict()
    vars = None

    def _ask_vars(self):
        for var in self.vars:
            if len(var) == 3:
                name, desc, type = var
                options = {}
            elif len(var) == 4:
                name, desc, type, options = var
            else:
                raise RuntimeError("Got unexpected parameter length.")
            
            message = desc
            default = options.get('default', None)
            validator = options.get('validator', None)

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
                    if validator:
                        answer = validator(answer)
                        if not answer:
                            continue
                    break

            self.answers[name] = answer

    def _get_appname(self):
        from ConfigParser import SafeConfigParser
        conf = SafeConfigParser()
        conf.read("config.ini")
        return conf.get("general", "application.name")

    def _patchcopy(self, fname, target, vars):
        if os.path.exists(target):
            raise RuntimeError("Cannot write to %r. Destination file already exists!" %
                               target)
        tmpl = open(fname, 'r+')
        dest = open(target, 'w')
        t = Template(tmpl.read())
        dest.write(t.render(vars))
        tmpl.close()
        dest.close()

    def run(self):
        raise NotImplementedError()

def _validate_appname(value):
    answer = value.strip()
    if ' ' in answer:
        sys.stderr.write("Application name must not contain spaces.")
        return False
    if not re.compile("[a-z0-9-_]+").match(answer):
        sys.stderr.write("Application name must only contain "
              "alphanumeric values, _ and -.")
        return False
    return answer

class TemplateCommand(Command):
    vars = (
        ('appname', "Application Name", 'string', {'validator':
                                                   _validate_appname}),
        ('debug_enabled', "Enable debug mode? (recommended)", 'bool',
         {'default': True}),
    )

    def _create_dir(self):
        appname = self.answers['appname']
        sys.stderr.write("Creating project directory %s …" % appname)
        os.mkdir(appname)

    def _copy_templates(self):
        appname = self.answers['appname']
        origin = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                              "project_templates"))
        os.chdir(appname)
        for fname in os.listdir(os.path.join(origin, "base")):
            print("Creating %s …" % fname)
            self._patchcopy(os.path.join(origin, "base", fname), fname,
                            self.answers)

        print("Creating project folder …")
        shutil.copytree(os.path.join(origin, "application"),
                        appname)
        print("Done.")

    def run(self):
        print("Creating new rdrei project.")
        self._ask_vars()
        self._create_dir()
        self._copy_templates()

class ControllerCommand(Command):
    
    def run(self, name):
        if name == "controller":
            sys.stderr.write("You have to specify the controller's name!")
            sys.exit(1)
        self._create_controller(name)

    def _create_controller(self, name):
        appname = self._get_appname()
        origin = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "project_templates"))
        os.chdir(appname)
        self._create_dirs()

        context = {'appname': appname, 'contname': name,
                   'contname_cap': name.capitalize()}
        
        print("Creating controller %s …" % name)
        self._patchcopy(os.path.join(origin, "controllers", "controller.py"),
                        os.path.join("controllers", "%s.py" % name),
                        context)
        print("Creating helper %s …" % name)
        self._patchcopy(os.path.join(origin, "controllers", "helper.py"),
                        os.path.join("helpers", "%s.py" % name),
                        context)
        print("Done.")

    def _create_dirs(self):
        if not os.path.exists("controllers"):
            print("Creating controllers/ …")
            os.mkdir("controllers")
            self._create_init("controllers")
        
        if not os.path.exists("helpers"):
            print("Creating helpers/ …")
            os.mkdir("helpers")
            self._create_init("helpers")
    
    def _create_init(self, dir):
        """Create an empty __init__.py file in dir/."""
        open(os.path.join(dir, "__init__.py"), 'w').close()

def make_controller(name="controller"):
    """Returns an action callback that creates a new controller."""
    def action(name=('n', name)):
        """Create a new controller and corresponding helper module."""
        cc = ControllerCommand()
        cc.run(name)
    return action

def make_project():
    """Starts a wizard to create a new project directory."""
    tc = TemplateCommand()
    tc.run()

