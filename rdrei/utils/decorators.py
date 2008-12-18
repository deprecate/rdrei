from werkzeug.routing import Rule
from functools import wraps

from rdrei.core.local import local

import time, logging, inspect

log = logging.getLogger(__name__)
application = local('application')
url_map = application.import_from_app("urls", "url_map")

def expose(rule, **kw):
    def decorate(f):
        kw['endpoint'] = f.__module__.split('.')[-1]+"/"+f.__name__
        url_map.add(Rule(rule, **kw))
        return f
    return decorate

def beaker_cache(key="cache_default", expire="never", type=None,
                 query_args=False,
                 cache_headers=('content-type', 'content-length'),
                 invalidate_on_startup=False, **b_kwargs):
    """Cache decorator utilizing Beaker. Caches action or other
    function that returns a pickle-able object as a result.

    Optional arguments:

    ``key``
        None - No variable key, uses function name as key
        "cache_default" - Uses all function arguments as the key
        string - Use kwargs[key] as key
        list - Use [kwargs[k] for k in list] as key
    ``expire``
        Time in seconds before cache expires, or the string "never". 
        Defaults to "never"
    ``type``
        Type of cache to use: dbm, memory, file, memcached, or None for
        Beaker's default
    ``query_args``
        Uses the query arguments as the key, defaults to False
    ``cache_headers``
        A tuple of header names indicating response headers that
        will also be cached.
    ``invalidate_on_startup``
        If True, the cache will be invalidated each time the application
        starts or is restarted.

    If cache.enabled is set to False in the .ini file, then cache is
    disabled globally.

    """
    if invalidate_on_startup:
        starttime = time.time()
    else:
        starttime = None
    cache_headers = set(cache_headers)

    def wrapper(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            self = args[0]
            request = self.request
            log.debug("Wrapped with key: %s, expire: %s, type: %s, query_args: %s",
                      key, expire, type, query_args)
            # Checking our ini, whether caching is globally disabled.
            enabled = local.application.config.getboolean("general", "cache.enabled")
            if not enabled:
                log.debug("Caching disabled. Skipping lookup.")
                return func(*args, **kwargs)
                                                           
            if key:
                if query_args:
                    # Put all query args into a dict
                    key_dict = request.values.to_dict()
                else:
                    # Otherwise make a dict from the kwargs
                    # and convert the args to a kwargs-style
                    # dict, so we can call it with **kwargs.
                    # self and request are ignored as args.
                    key_dict = kwargs.copy()
                    key_dict.update(_make_dict_from_args(func, args,
                                                         key_dict.keys()))

                if key != "cache_default":
                    if isinstance(key, dict):
                        # Use only listed keys for kwargs generation.
                        key_dict = dict((k, key_dict[k]) for k in key)
                    else:
                        # Treated as single value. Must exist in kwargs.
                        key_dict = {key: key_dict[key]}

            else:
                # key == None, don't cache args.
                key_dict = None

            # Generate namespace and cache key from args and controller
            namespace, cache_key = create_cache_key(func, key_dict, self)

            if type:
                # Update type for beaker kwargs
                b_kwargs['type'] = type

            # Finally access the cache object.
            my_cache = request.cache.get_cache(namespace, **b_kwargs)

            # Parse the expire argument
            if expire == "never":
                cache_expire = None
            else:
                # Hoping that this is a valid number. (;
                cache_expire = expire
            
            def create_func():
                log.debug("Creating new cache copy with key %r and type %r" %
                          (cache_key, type))
                # This is our response object.
                result = func(*args, **kwargs)
                # In contrast to pylons, our result includes all headers,
                # status values and so on, so we don't need to build another
                # pickable dictionary.
                return result
            # Tell beaker to check for our key and in case it's not found,
            # create a new entry with our create_func
            response = my_cache.get_value(cache_key, createfunc=create_func,
                                          expiretime=cache_expire,
                                          starttime=starttime)

            return response
        return _wrapper
    return wrapper


def create_cache_key(func, key_dict=None, self=None):
    """Get a cache namespace and key used by the beaker_cache decorator.
    
    Example::
        from pylons import cache
        from pylons.decorators.cache import create_cache_key
        namespace, key = create_cache_key(MyController.some_method)
        cache.get_cache(namespace).remove(key)
            
    """
    if key_dict:
        cache_key = " ".join(["%s=%s" % (k, v) for k, v in key_dict.iteritems()])
    else:
        if hasattr(self, 'im_func'):
            cache_key = func.im_func.__name__
        else:
            cache_key = func.__name__
    
    if self:
        return '%s.%s' % (func.__module__, self.__class__.__name__), cache_key
    else:
        return '%s.%s' % (func.__module__, func.im_class.__name__), cache_key

def _make_dict_from_args(func, args, exclude=None):
    """Inspects function for name of args"""
    args_keys = {}
    _exclude = ['self', 'request']
    if exclude:
        _exclude += exclude
    for i, arg in enumerate(inspect.getargspec(func)[0]):
        if arg not in _exclude:
            args_keys[arg] = args[i]
    return args_keys

