import cgi
import logging
import json

from ..hook_helper import *

has_config = False

try:
    import config
    has_config = True
except ImportError:
    has_config = False
    logging.error('Cannot load config for Follows Hook. Will not function.')

'''
{
   "data":
      [{
         "from_id":"1336",
         "from_name":"ebi",
         "to_id":"1337",
         "to_name":"oliver0823nagy",
         "followed_at": "2017-08-22T22:55:24Z"
      }]
}
'''

@register_hook("follows")
class hook_follows():

    def subscribed(self):
        pass

    def process(self, data):
        print "processing..."
        print data
        data = json.loads(data)
        print data['from_id']
        return "foobar"

    def get_instance(self):
        return self



def hook_follows(query):
    global has_config
    if not has_config:
        return '{"error":"No configuration loaded for Follows Hook"}'
    if query == "":
        return '{"error":"Empty query"}'
