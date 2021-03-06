import requests
import logging
import json
import server_config

from websocket import create_connection

hook_register = dict()
hook_headers = dict()

def _register_hook(path):
    global hook_register
    def wrap(hook):
        print "Registering Hook: " + path
        def wrapped(query):
            return hook(query)
        hook_register[path] = wrapped()
        return wrapped
    return wrap

def set_headers(headers):
    global hook_headers
    def wrap(func):
        print "Adding headers: " + str(headers)
        def wrapped(query):
            return func(query)
        wrapped.func_name = fun.func_name
        hook_headers[func] = headers
        return wrapped
    return wrap

def sub_hook(config, secret, callback, client_id, oauth_key):
    url = "https://api.twitch.tv/helix/webhooks/hub?client_id={client_id}".format(client_id=client_id)
    result = 1
    try:
        data = {
            'hub.callback': '%s:%s/%s' % (server_config.host, server_config.port, callback),
            'hub.mode': 'subscribe',
            'hub.topic': config.topic,
            'hub.lease_seconds': 864000,
            'hub.secret': secret
        }
        headers = {
            'Client-ID': client_id,
            'Authorization': 'OAuth ' + oauth_key
        }
        logging.debug("Sending subscription request: " + str(data))
        r = requests.post(url, headers=headers, data=data)
        logging.debug(r.status_code)
        logging.debug(r.headers)
        logging.debug(r.text)


    except requests.exceptions.RequestException:
        return None
    return result

def register_hook(path):
    def wrap(hook):
        global hook_register
        logging.info("Registering Hook: " + path)
        class NewCls(hook):
            def __init__(self,*args,**kwargs):
                self.oInstance = hook(*args,**kwargs)
            def __getattribute__(self,s):
                """
                This is called whenever any attribute of a NewCls object is accessed. This function first tries to
                get the attribute off NewCls. If it fails then it tries to fetch the attribute from self.oInstance (an
                instance of the decorated class).
                """
                try:
                    x = super(NewCls,self).__getattribute__(s)
                except AttributeError:
                    pass
                else:
                    return x
                x = self.oInstance.__getattribute__(s)
                return x
        hook_register[path] = NewCls
        return NewCls
    return wrap

''' Websocket handler '''

def send_message(handler, data):
    try:
        print "Trying to send an alert message: " + ', '.join([handler, data['text']])
        message = {}
        message['handler'] = handler
        message['data'] = data
        ws = create_connection(server_config.ws_server)
        #logging.debug("Sending Auth: " + config['websocket']['secret'])
        ws.send("AUTH:" + server_config.websocket_secret)
        #logging.debug("Sending Message: " + json.dumps(message))
        ws.send(json.dumps(message))
        ws.recv()
        ws.close()
    except Exception as e:
        print "Websocket failed: "
        print e
        logging.error("Websocket not available...")
