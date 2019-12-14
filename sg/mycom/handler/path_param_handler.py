import http.server as httpServer
import http.client as httpClient
import json

import util.http as httpUtil


class MyCompanyPathParamHandler(httpUtil.Handler):
    def __init__(self):
        pass

    def handle(self, obj: httpServer.BaseHTTPRequestHandler, param_map: dict):
        obj.send_response(httpClient.OK)
        obj.send_header('Content-type', 'text/plain')
        obj.end_headers()
        obj.wfile.write(bytearray(self.name, 'utf-8'))
        obj.wfile.write(bytearray(json.dumps(param_map, indent=4), 'utf-8'))
