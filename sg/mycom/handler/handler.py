import http.server as httpServer
import http.client as httpClient

import util.http as httpUtil


class MyCompanyHandler(httpUtil.Handler):
    def __init__(self):
        pass

    def handle(self, obj: httpServer.BaseHTTPRequestHandler):
        obj.send_response(httpClient.OK)
        obj.send_header('Content-type', 'text/plain')
        obj.end_headers()
        obj.wfile.write(bytearray(self.name, 'utf-8'))
        url_param_map = httpUtil.get_url_param_map(obj)
        obj.wfile.write(bytearray(str(url_param_map) if url_param_map is not None else str('{}'), 'utf-8'))
