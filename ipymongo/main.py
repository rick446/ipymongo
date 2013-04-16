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
    '''use <database>'''
    conn = self.shell.user_ns['conn']
    db = conn[arg]
    self.shell.user_ns.update(
        db=db, _curdb=db.name)
    shell_config = self.shell.prompt_manager
    shell_config.in_template = 'In [\\#] (%s): ' % db.name

def magic_show(self, arg):
    '''show (dbs | collections | users | profile | logs | log <name>)'''
    conn = self.shell.user_ns['conn']
    db = self.shell.user_ns['db']
    if arg in ('databases', 'dbs'):
        return conn.database_names()
    elif arg in ('tables', 'collections'):
        return db.collection_names()
    elif arg == 'users':
        return list(db.system.users.find())
    elif arg == 'profile':
        return list(db.system.profile.find())
    elif arg == 'logs':
        return conn.admin.command('getLog', '*')['names']
    elif arg.startswith('log '):
        cmd, rest = arg.split(' ', 1)
        return conn.admin.command('getLog', rest)['log']
    else:
        print 'usage: show (dbs | collections | users | profile | logs | log <name>)'

def magic_connect(self, arg):
    '''connect <mongodb uri>'''
    ns = self.shell.user_ns
    if arg:
        conn, db = set_uri(arg)
        ns.update(conn=conn, db=db)
    shell_config = self.shell.prompt_manager
    shell_config.in_template = 'In [\\#] (%s): ' % db.name
    return ns['conn']

def magic_login(self, arg):
    '''login [username [password] ]'''
    shell = self.shell
    args = arg.split()
    if len(args) == 0:
        username = shell.raw_input('Username: ')
        password = getpass.getpass('Password: ')
    if len(args) == 1:
        username = args[0]
        password = getpass.getpass('Password: ')
    elif len(args) == 2:
        username, password = args
    else:
        print '''usage: login [username [password] ]'''
    return shell.user_ns['db'].authenticate(username, password)

def set_uri(uri):
    if uri.startswith('mongodb://'):
        args = {}
        result = urlparse.urlparse(uri)
        db = result.path.strip('/') or 'test'
        auth_args = None
    else:
#        uri = uri.split(':', 1)[-1]
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
        uri = 'mongodb://%s:%s' % (hostname, port)
    conn = pymongo.Connection(
        uri,
        **args)
    if db:
        db = conn[db]
    if auth_args:
        db.authenticate(**auth_args)
    return conn, db
