from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from urlparse import urlparse, parse_qs
from threading import Thread
import time
import sys
import logging
import hashlib
import hmac

import hooks.follows.hook as follows

from hooks.hook_helper import *

import config

seen_IDs = []

class MyHandler(BaseHTTPRequestHandler):

    def check_id(self, id):
        global seen_IDs

        if not id in seen_IDs:
            seen_IDs.append(id)
            if len(seen_IDs) > 10:
                seen_IDs.pop(0)
            return True
        else:
            return False

    def sendResponse(self, code, headers, data):
        self.send_response(code)
        items = headers.items()
        for item in items:
            self.send_header(item[0], item[1])
        self.end_headers()
        self.wfile.write(data)

    def send404(self, path):
        print "sending 404"
        self.sendResponse(404, {'Content-Type':'application/xml'}, "<error>Path Error: /"+path+"</error>")

    def subVerify(self, query):
        # respond 200 with verification token
        logging.info("Subscription Success: " + self.path)
        self.sendResponse(200, {}, query['hub.challenge'][0])

    def subDenied(self, query):
        # figure out why. Not authed or max subscriptions...
        # send 200 response
        self.sendResponse(200, {}, "")

    def handleNotification(self):
        # verify and handle notifications
        # check unique ID so we don't double notifications
        # figure out way to track notification ID's (max number?)

        path = self.path.lstrip('/')
        query = {}
        if "?" in path:
            query = path[path.index("?")+1:]
            path = path[0:path.index("?")]
            query = parse_qs(query)

        content_len = int(self.headers.getheader('content-length', 0))
        data = self.rfile.read(content_len)

        hash = self.headers.getheader('X-Hub-Signature')
        check = "sha256=" + hmac.new('secret', data, hashlib.sha256).hexdigest()

        notification_id = self.headers.getheader('Twitch-Notification-Id')

        resp = ""

        if hmac.compare_digest(hash, check):
            if self.check_id(notification_id):
                hook = hook_register[path]()
                resp = hook.process(data)
        else:
            logging.warning("Bad request, someone is being naughty!")

        self.sendResponse(200, {'Content-Type':'text/html'}, resp)


    def do_GET(self):
        # get requests are subscription verifications etc only.
        # Move all this out into the subVerify function
        path = self.path.lstrip('/')
        query = {}
        if "?" in path:
            query = path[path.index("?")+1:]
            path = path[0:path.index("?")]
            query = parse_qs(query)
        try:
            if path in config.available_hooks and query:
                if query['hub.mode'][0] == 'subscribe':
                    self.subVerify(query)
                elif query['hub.mode'][0] == 'denied':
                    self.subDenied(query)
                else:
                    # unhandled mode
                    logging.error("Unhandled mode: " + query['hub.mode'][0])
                    self.subDenied(query)
                return
            else:
                self.send404(path)
                return
        except IOError as details:
            self.send_error(404, 'IOError: '+str(details))
        pass


    def do_POST(self):
        print self.headers
        print self.path

        path = self.path.lstrip('/')
        if "?" in path:
            path = path[0:path.index("?")]

        try:
            if path in config.available_hooks:
                resp = self.handleNotification()

                return
            else:
                self.send404(path)
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

def subscribe():
    # subscribe to all the topics I want. Can also be used to resubscribe.
    # Must resubscribe at least every 10 days. Probably do it weekly (7 days)
    for h in hook_register:
        hook = hook_register[h]()
        hook.subscribe()

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
