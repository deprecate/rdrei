from rdrei.local import local
from rdrei.utils import render_template

def get_controller(request, name):
    application = local.application
    if '/' in name:
        cname, hname = name.split('/')
    else:
        return application.import_from_app('controllers.%s' % name)

    controller = application.cache.get_controller(cname)
    if not controller:
        module = application.import_from_app('controllers.%s' % cname)
        controller = module.controller
    return getattr(controller(request), hname)

class BaseController(object):
    def __init__(self, request):
        self.request = request
        self.translations = self.request.translations

    def render_to_response(self, template, context = None):
        return render_template(self.request, template, context)

