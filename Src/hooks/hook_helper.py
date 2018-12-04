import requests
import logging
import config

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

def sub_hook(config, secret):
    print "sub_hook called!"
    url = "https://api.twitch.tv/helix/webhooks/hub?client_id={client_id}".format(client_id=config.client_id)
    result = 1
    try:
        data = {
            'hub.callback': 'http://capnflint.com:9021/' + config.callback,
            'hub.mode': 'subscribe',
            'hub.topic': config.topic,
            'hub.lease_seconds': 864000,
            'hub.secret': secret
        }
        headers = {
            'Client-ID': config.client_id,
            'Authorization': 'OAuth ' + config.oauth_key
        }
        print data
        logging.debug("Sending subscription request: " + str(data))
        r = requests.post(url, headers=headers, data=data)
        print r.status_code
        print r.headers
        print r.text


    except requests.exceptions.RequestException:
        return None
    return result

def register_hook(path):
    def wrap(hook):
        global hook_register
        print "Registering Hook: " + path
        class NewCls(hook):
            def __init__(self,*args,**kwargs):
                self.oInstance = hook(*args,**kwargs)
            def __getattribute__(self,s):
                """
                this is called whenever any attribute of a NewCls object is accessed. This function first tries to
                get the attribute off NewCls. If it fails then it tries to fetch the attribute from self.oInstance (an
                instance of the decorated class). If it manages to fetch the attribute from self.oInstance, and
                the attribute is an instance method then `time_this` is applied.
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
        ws = create_connection("ws://capnflint.com:9001")
        #logging.debug("Sending Auth: " + config['websocket']['secret'])
        ws.send("AUTH:" + config['websocket']['secret'])
        #logging.debug("Sending Message: " + json.dumps(message))
        ws.send(json.dumps(message))
        ws.recv()
        ws.close()
    except Exception as e:
        print "Websocket borkeded"
        print e
        logging.error("Websocket not available...")
