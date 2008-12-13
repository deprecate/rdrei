def get_controller(name):
    if '/' in name:
        cname, hname = name.split('/')
    else:
        return __import__('rdrei.controllers.%s' % name, None, None, [''])

    module = __import__('rdrei.controllers.%s' % cname, None, None, [''])
    controller = module.controller()
    return getattr(controller, hname)

class BaseController(object):
    @classmethod
    def expose_all(cls):
        from rdrei.urls import url_map

        for controller in cls.__subclasses__():
            for func in vars(controller).values():
                if hasattr(func, 'rule'):
                    url_map.add(func.rule)

