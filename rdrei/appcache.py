"""A class for the registration of applications, controllers and so on."""

from werkzeug.utils import find_modules

class ApplicationCache(object):
    _loaded = False
    controllers = dict()

    def __init__(self, appname):
        self.appname = appname
        self.load_controllers()
    
    def load_controllers(self):
        for mod in find_modules(self.appname+".controllers"):
            self.controllers[mod.split('.')[-1]] = __import__(mod, None, None, ['']).controller

        self._loaded = True
        
    def get_controller(self, name):
        if name in self.controllers:
            return self.controllers[name]
        else:
            return False
        
