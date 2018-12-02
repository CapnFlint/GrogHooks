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

def register_hook(path):
    global hook_register
    print "Registering Hook: " + path
    class NewCls(hook):
        def __init__(self,*args,**kwargs):
            self.oInstance = Cls(*args,**kwargs)
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
            if type(x) == type(self.__init__): # it is an instance method
                return time_this(x)                 # this is equivalent of just decorating the method with time_this
            else:
                return x
    hook_register[path] = NewCls
    return NewCls
