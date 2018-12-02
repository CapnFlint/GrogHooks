import cgi
import logging

from ..hook_helper import *

has_config = False

try:
    import config
    has_config = True
except ImportError:
    has_config = False
    logging.error('Cannot load config for Follows Hook. Will not function.')

@register_hook("follows")
class hook_follows():
    def __init__():
        pass

    def subscribed():
        pass

    def process(query):
        qs = cgi.parse_qs(query)
        print "processing..."
        return qs['action']
        pass

    def get_instance(self):
        return self



def hook_follows(query):
    global has_config
    if not has_config:
        return '{"error":"No configuration loaded for Follows Hook"}'
    if query == "":
        return '{"error":"Empty query"}'