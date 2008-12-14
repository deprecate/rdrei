"""A class for the registration of applications, controllers and so on."""

from werkzeug.utils import find_modules
from rdrei.local import local

class ApplicationCache(object):
    def __init__(self, appname):
        self.controllers = []
        self.appname = appname
    
    def load_controllers(self):
        for mod in find_modules(appname+".controllers"):
            self.controllers[mod.split('.')[-1]] = __import__(mod, None, None, ['']).controller
        
    def get_controller(self, name):
        if name in self.controllers:
            return self.controllers[name]
        else:
            return False
        
cache = ApplicationCache
