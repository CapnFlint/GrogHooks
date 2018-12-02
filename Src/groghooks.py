from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from urlparse import urlparse, parse_qs
import time
import sys
import logging

import hooks.follows.hook as follows

from hooks.hook_helper import *

import config

def send404(handler, path):
    print "sending 404"
    sendResponse(handler, 404, {'Content-Type':'application/xml'}, "<error>Path Error: /"+path+"</error>")
    return

def sendResponse(handler, code, headers, data):
    handler.send_response(code)
    items = headers.items()
    for item in items:
        handler.send_header(item[0], item[1])
    handler.end_headers()
    handler.wfile.write(data)
    return

def subscribe():
    # subscribe to all the topics I want. Can also be used to resubscribe.
    # Must resubscribe at least every 10 days. Probably do it weekly (7 days)
    pass

def subVerify(handler, token):
    # respond 200 with verification token
    pass

def subDenied(handler):
    # figure out why. Not authed or max subscriptions...
    # send 200 response
    pass

def handleNotification(data):
    # verify and handle notifications
    # check unique ID so we don't double notifications
    # figure out way to track notification ID's (max number?)
    # send 200 response!
    pass

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        # get requests are subscription verifications etc only.
        path = self.path.lstrip('/')
        query = {}
        if path.find("?") > 0:
            query = path[path.index("?")+1:]
            path = path[0:path.index("?")]
            query = parse_qs(query)
        try:
            if path in config.available_hooks and query:
                if query['hub.mode'] == 'subscribe':
                    logging.info("Subscribed: " + path)
                    subVerify(path, query)
                elif query['hub.mode'] == 'denied':
                    logging.info("Subscription denied: " + path)
                    subDenied(path, query)
                else:
                    # unhandled mode
                    logging.error("Unhandled mode: " + query['hub.mode'])
                    subDenied(path, query)
                sendResponse(self, 200, {}, query['hub.challenge'][0])
                return
            else:
                send404(self, path)
                return
        except IOError as details:
            self.send_error(404, 'IOError: '+str(details))
        pass


    def do_POST(self):
        path = self.path.lstrip('/')
        # process Path
        try:
            print config.available_hooks
            print path
            if path in config.available_hooks:
                hook = hook_register[path]
                sendResponse(self, 200, hook_headers[hook], hook.process(query))
                return
            else:
                send404(self, path)
                return
        except IOError as details:
            self.send_error(404, 'IOError: ' + str(details))

class HookServer(ThreadingMixIn, HTTPServer):
    def __init__(self, port):
        HTTPServer.__init__(self, ('',port), MyHandler)

def main(argv):
    logging.basicConfig(filename=config.log_file, format=config.log_format, datefmt=config.log_date_format, level=config.log_level)

    try:
        server = HookServer(config.port)
        logging.info('Started Webhook Server on port: '+str(config.port))
        server.serve_forever()

    except KeyboardInterrupt:
        logging.info('^C received, shutting down API server!')

if __name__ == '__main__':
    main(sys.argv[1:])
