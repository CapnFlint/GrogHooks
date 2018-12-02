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

    def subscribed(self):
        pass

    def process(self, query):
        print "processing..."
        return query['action'][0]
        pass

    def get_instance(self):
        return self



def hook_follows(query):
    global has_config
    if not has_config:
        return '{"error":"No configuration loaded for Follows Hook"}'
    if query == "":
        return '{"error":"Empty query"}'
