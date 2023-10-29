from django.apps import apps
from django.utils.module_loading import import_string

class Filters(object):
    _app_filters_loaded = False
    FILTERS = {}


def register_filter(name):
    def filter_decorator(func):
        Filters.FILTERS[name] = func
        return func
    return filter_decorator


def get_filter_by_name(name):
    load_app_filters()
    if isinstance(name, str):
        return Filters.FILTERS[name]
    else:
        ret = Filters.FILTERS[name]
        setattr(ret, "_config", name.get('config',{}))
        return ret

def load_app_filters():
    if Filters._app_filters_loaded:
        return
    Filters._app_filters_loaded = True
    for app_cfg in apps.get_app_configs():
        try:
            __import__(app_cfg.name+'.assetfilters')
        except:
            pass

def get_all_filters():
    load_app_filters()
    return Filters.FILTERS.items()

from .cssmin import *
from .sass import *
from .clojure import *
from .ttf2woff2 import *
from .babel import *

