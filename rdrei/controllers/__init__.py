from rdrei.local import local

def get_controller(name):
    application = local.application
    if '/' in name:
        cname, hname = name.split('/')
    else:
        return application.import_from_app('controllers.%s' % name)

    controller = application.cache.get_controller(cname)
    if not controller:
        module = application.import_from_app('controllers.%s' % cname)
        controller = module.controller
    return getattr(controller(), hname)

class BaseController(object):
    pass

