import os
def app(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    if path == '/':
        filename = 'index.html'
    else:
        filename = path.lstrip('/')
    if not os.path.exists(filename):
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b'404 Not Found']

    with open(filename, 'rb') as f:
        data = f.read()

    start_response('200 OK', [('Content-Type', 'text/html')])
    return [data]
