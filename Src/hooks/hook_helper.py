hook_register = dict()
hook_headers = dict()

def register_hook(path):
    global hook_register
    def wrap(hook):
        print "Registering Hook: " + path
        def wrapped(query):
            return hook(query)
        hook_register[path] = wrapped
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
