from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from urlparse import urlparse, parse_qs
from threading import Thread
import time
import sys
import logging
import hashlib

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
    print "Subscribing!"
    logging.debug("Subscribing!!!")
    for h in hook_register:
        hook = hook_register[h]()
        hook.subscribe()

def subVerify(handler, query):
    # respond 200 with verification token
    logging.info("Subscription Success!")
    sendResponse(handler, 200, {}, query['hub.challenge'][0])

def subDenied(handler, query):
    # figure out why. Not authed or max subscriptions...
    # send 200 response
    pass

def handleNotification(handler):
    # verify and handle notifications
    # check unique ID so we don't double notifications
    # figure out way to track notification ID's (max number?)
    # send 200 response!
    # verification done using X-Hub-Signature header
    # sha256(secret, notification_bytes)
    path = handler.path.lstrip('/')
    query = {}
    if path.find("?") > 0:
        query = path[path.index("?")+1:]
        path = path[0:path.index("?")]
        query = parse_qs(query)
    content_len = int(handler.headers.getheader('content-length', 0))
    post_body = self.rfile.read(content_len)
    hash = handler.headers.getheader('X-Hub-Signature')
    check = hashlib.sha256('secret' + post_body).hexdigest()
    print "Theirs: [" + hash + "]"
    print "Ours: [" + check + "]"
    if hash == check:
        hook = hook_register[path]()
        return hook.process(data)
    else:
        print "FAILFISH!"

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        # get requests are subscription verifications etc only.
        logging.debug("GET request!")
        path = self.path.lstrip('/')
        query = {}
        print self.headers['user-agent']
        if path.find("?") > 0:
            query = path[path.index("?")+1:]
            path = path[0:path.index("?")]
            query = parse_qs(query)
        try:
            if path in config.available_hooks and query:
                if query['hub.mode'][0] == 'subscribe':
                    logging.info("Subscribed: " + path)
                    subVerify(self, query)
                elif query['hub.mode'][0] == 'denied':
                    logging.info("Subscription denied: " + path)
                    subDenied(self, query)
                else:
                    # unhandled mode
                    logging.error("Unhandled mode: " + query['hub.mode'][0])
                    subDenied(path, query)
                return
            else:
                send404(self, path)
                return
        except IOError as details:
            self.send_error(404, 'IOError: '+str(details))
        pass


    def do_POST(self):
        path = handler.path.lstrip('/')
        # process Path
        try:
            if path in config.available_hooks:
                resp = handleNotification(self)
                sendResponse(self, 200, {'Content-Type':'text/html'}, resp)
                return
            else:
                send404(self, path)
                return
        except IOError as details:
            self.send_error(404, 'IOError: ' + str(details))

class HookServer(ThreadingMixIn, HTTPServer):
    def __init__(self, port):
        HTTPServer.__init__(self, ('',port), MyHandler)

def start_server():
    try:
        server = HookServer(config.port)
        logging.info('Started Webhook Server on port: '+str(config.port))
        server.serve_forever()

    except KeyboardInterrupt:
        logging.info('^C received, shutting down API server!')

def main(argv):
    logging.basicConfig(filename=config.log_file, format=config.log_format, datefmt=config.log_date_format, level=config.log_level)
    try:
        t = Thread(target=start_server)
        t.setDaemon(True)
        t.start()
        subscribe()
        t.join()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main(sys.argv[1:])
