import getpass
import urlparse

import pymongo

default_uri = 'mongodb://localhost:27017/test'

def load_ipython_extension(ipython):
    # The `ipython` argument is the currently active `InteractiveShell`
    # instance, which can be used in any way. This allows you to register
    # new magics, plugins or aliases, for example.
    ipython.define_magic('use', magic_use)
    ipython.define_magic('connect', magic_connect)
    ipython.define_magic('login', magic_login)
    ipython.define_magic('show', magic_show)
    conn, db = set_uri(default_uri)
    ipython.user_ns.update(conn=conn, db=db)
    shell_config = ipython.prompt_manager
    shell_config.in_template = 'In [\\#] (%s): ' % db.name
    

def unload_ipython_extension(ipython):
    # If you want your extension to be unloadable, put that logic here.
    pass

def magic_use(self, arg):
    conn = self.shell.user_ns['conn']
    db = conn[arg]
    self.shell.user_ns.update(
        db=db, _curdb=db.name)
    shell_config = self.shell.prompt_manager
    shell_config.in_template = 'In [\\#] (%s): ' % db.name

def magic_show(self, arg):
    conn = self.shell.user_ns['conn']
    db = self.shell.user_ns['db']
    if arg in ('databases', 'dbs'):
        return conn.database_names()
    elif arg in ('tables', 'collections'):
        return db.collection_names()
    else:
        print 'usage: show <dbs|tables>'

def magic_connect(self, arg):
    ns = self.shell.user_ns
    if arg:
        conn, db = set_uri(arg)
        ns.update(conn=conn, db=db)
    shell_config = self.shell.prompt_manager
    shell_config.in_template = 'In [\\#] (%s): ' % db.name
    return ns['conn']

def magic_login(self, arg):
    shell = self.shell
    if arg:
        username, password = arg.split()
    else:
        name = shell.raw_input('Username: ')
        password = getpass.getpass('Password: ')
    return shell.user_ns['db'].authenticate(name, password)
    
def set_uri(uri):
    if uri.startswith('mongodb://'):
        uri = uri.split(':', 1)[-1]
    result = urlparse.urlparse(uri)
    hostname = result.hostname or '127.0.0.1'
    port = result.port or '27017'
    db = result.path.strip('/') or 'test'
    args = urlparse.parse_qs(result.query)
    for k,vs in args.items():
        if len(vs) == 1:
            args[k] = vs[0]
    if 'name' in args or result.username:
        auth_args = dict(
            name=args.pop('name', result.username),
            password=args.pop('password', result.password))
        if not auth_args['password']:
            auth_args['password'] = getpass.getpass('Password: ')
    else:
        auth_args = None
    conn = pymongo.Connection(
        'mongodb://%s:%s' % (hostname, port),
        **args)
    db = conn[db]
    if auth_args:
        db.authenticate(**auth_args)
    return conn, db
                
