def get_controller(name):
    cname, hname = name.split('/')
    module = __import__('rdrei.controllers.%s' % cname, None, None, [''])
    controller = module.controller()
    return getattr(controller, hname)

