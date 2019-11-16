import http.server as httpServer
import socketserver as socketServer
import http.client as httpClient
import re
import collections
import logging
from abc import ABC, abstractmethod

class RequestHandler(httpServer.BaseHTTPRequestHandler):
	def initialize(self, config1):
		self.config = config1
		
	def do_POST(self):
		logging.debug("http post")
		process(self, HTTP_METHOD["POST"])
		
	def do_GET(self):
		logging.debug("http get")
		process(self, HTTP_METHOD["GET"])
	
	def do_HEAD(self):
		logging.debug("http head")
		process(self, HTTP_METHOD["HEAD"])
	
	def log_message(self, format, *args):
		return
		
class Handler(ABC):	
	@abstractmethod
	def handle(self, obj : httpServer.BaseHTTPRequestHandler):
		pass
		
class ChainHandler(ABC):	
	@abstractmethod
	def handle(self, obj : httpServer.BaseHTTPRequestHandler) -> bool:
		return False
		
class PathParamHandler(ABC):
	@abstractmethod
	def handle(self, obj : httpServer.BaseHTTPRequestHandler, param_map : dict):
		pass
		
class ChainPathParamHandler(ABC):	
	@abstractmethod
	def handle(self, obj : httpServer.BaseHTTPRequestHandler, param_map : dict) -> bool:
		return False		

HTTP_METHOD = {
	"GET" : "get",
	"POST" : "post",
	"HEAD" : "head"
}

#key is url, value is NamedTuple called TupleHandler
registered_handlers = {}
TupleHandler = collections.namedtuple('TupleHandler', ['handler_class', 'http_methods'])
place_holder_re = re.compile(r'(?:{\s*(\w+)\s*}|:\s*(\w+))', re.IGNORECASE)
	
def register_handler(url, cls_obj, http_methods):
	registered_handlers[url] = TupleHandler(handler_class=cls_obj, http_methods=http_methods)
	
def register_chain_handler(url, cls_obj_array, http_methods):
	registered_handlers[url] = TupleHandler(handler_class=cls_obj_array, http_methods=http_methods)

#key is url, value is NamedTuple called TupleHandlerRE
registered_handlers_re = {}
TupleHandlerRE = collections.namedtuple('TupleHandlerRE', ['handler_class', 'http_methods', 're'])
	
def register_handler_regex(url, cls_obj, http_methods):
	registered_handlers_re[url] = TupleHandlerRE(handler_class=cls_obj, http_methods=http_methods, re=re.compile(url, re.IGNORECASE))

def register_chain_handler_regex(url, cls_obj_array, http_methods):
	registered_handlers_re[url] = TupleHandlerRE(handler_class=cls_obj_array, http_methods=http_methods, re=re.compile(url, re.IGNORECASE))
	
#key is url, value is NamedTuple called TupleHandlerPathParam	
registered_handlers_path_param = {}
TupleHandlerPathParam = collections.namedtuple('TupleHandlerPathParam', ['handler_class', 'http_methods', 'path_token'])

def register_handler_path_param(url, cls_obj, http_methods):
	registered_handlers_path_param[url] = TupleHandlerPathParam(handler_class=cls_obj, http_methods=http_methods, path_token=url.split("/"))

def register_chain_handler_path_param(url, cls_obj_array, http_methods):
	registered_handlers_path_param[url] = TupleHandlerPathParam(handler_class=cls_obj_array, http_methods=http_methods, path_token=url.split("/"))
	
def process(self : httpServer.BaseHTTPRequestHandler, method):
	self.server_version = self.config['Site']['Name']
	self.sys_version = ''
	
	logging.info(self.path)
	urlpath = self.path.split('?')[0]
		
	if urlpath == "/":
		self.send_response(httpClient.OK)	
		self.send_header('Content-type','text/plain')
		self.end_headers()
		self.wfile.write(bytearray('I am alive!','utf-8'))	
		return
		
	#iterate registered_and/or chain handlers to see if key match self.path
	item = registered_handlers.get(urlpath,None)
	if item is not None:
		logging.info("registered handler found "+self.path)
		if method in item.http_methods:
			if not isinstance(item.handler_class, list):
				item.handler_class.handle(self)
			else:
				for obj in item.handler_class:
					if not obj.handle(self):
						break				
		else:
			default_not_found(self)			
		return
	
	#iterate registered_and/or chain regex handlers to see if key regex match self.path
	for k in registered_handlers_re.keys():
		item = registered_handlers_re[k]
		match = item.re.match(urlpath)
		if match:
			logging.info("registered regex handler found "+k)
			if method in item.http_methods:
				if not isinstance(item.handler_class, list):
					item.handler_class.handle(self)
				else:
					for obj in item.handler_class:
						if not obj.handle(self):
							break				
			else:
				default_not_found(self)			
			return
			
	#iterate registered_and/or chain path param handlers to see if key match self.path
	for k in registered_handlers_path_param.keys():
		item = registered_handlers_path_param[k]
		actual_token = urlpath.split("/")
		if len(item.path_token) == len(actual_token):
			param_map = {}
			found = True
			for i in range(len(item.path_token)):
				match = place_holder_re.match(item.path_token[i])
				if match:
					if match.group(1) is not None:
						param_map[match.group(1)] = actual_token[i]
					if match.group(2) is not None:
						param_map[match.group(2)] = actual_token[i]
				elif item.path_token[i] != actual_token[i]:
					found = False
					break

			if found and len(param_map) > 0:
				logging.info("registered path param handler found "+k)
				if method in item.http_methods:
					if not isinstance(item.handler_class, list):
						item.handler_class.handle(self, param_map)
					else:
						for obj in item.handler_class:
							if not obj.handle(self, param_map):
								break
				return				
			
	default_not_found(self)
	
def default_not_found(self : httpServer.BaseHTTPRequestHandler):
	self.send_response(httpClient.NOT_FOUND)	
	self.send_header('Content-type','text/plain')
	self.end_headers()
	self.wfile.write(bytearray(httpClient.responses[httpClient.NOT_FOUND],'utf-8'))