# -*- coding: utf-8 -*-
"""
 rdrei.appcache
 ~~~~~~~~~~~~~~~~
 <{A class for registration of application. Used for proloading models and
 controllers.}>


 :copyright: 2008 by Pascal Hartig <phartig@rdrei.net>
 :license: GPL, see doc/LICENSE for more details.
 """

from werkzeug.utils import find_modules

class ApplicationCache(object):
    _loaded_controllers = False
    controllers = dict()
    models = dict()

    def __init__(self, appname, application):
        self.appname = appname
        self.application = application
        self.load_controllers()
        self.load_models()
    
    def load_controllers(self):
        """Load all controllers from the application, so the routing cache gets
        filled."""
        for mod in find_modules(self.appname+".controllers"):
            self.controllers[mod.split('.')[-1]] = __import__(mod, None, None, ['']).controller

        self.loaded_controllers = True

    def load_models(self):
        """Recursivly import all models from our application, so SQLAlchemy can
        track them and we can create_all() them. (;"""
        
        try:
            for mod in find_modules(self.appname+".models"):
                __import__(mod, None, None, [''])
        except ValueError:
            # Models is not a package, so we treat it as module
            self.application.import_from_app("models")
        
    def get_controller(self, name):
        if not self.loaded_controllers:
            self.load_controllers()
        if name in self.controllers:
            return self.controllers[name]
        else:
            return False
        
