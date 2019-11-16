import http.server as httpServer
import http.client as httpClient
import json
import logging

import config
import util.http as httpUtil

def StartupInit(config) :
	'''
	ENTRY POINT: perform any pre-loading/caching of objects or anything else before server startup in here (if any)
	'''
	logging.info('startup init ...')

def ShutdownCleanup(config):
	'''
	ENTRY POINT: perform any cleaning up of objects or anything else before server shutdown in here (if any)
	'''
	logging.info('shutdown cleanup ...')

class MyHandler(httpUtil.Handler):
	def __init__(self,name,config=None):
		self.name = name
		
	def handle(self, obj : httpServer.BaseHTTPRequestHandler):
		obj.send_response(httpClient.OK)	
		obj.send_header('Content-type','text/plain')
		obj.end_headers()
		obj.wfile.write(bytearray(self.name,'utf-8'))
		
class MyChainHandler(httpUtil.ChainHandler):
	def __init__(self,chain_name,retTF,config=None):
		self.chain_name = chain_name
		self.ret = retTF
		
	def handle(self, obj : httpServer.BaseHTTPRequestHandler) -> bool:		
		obj.send_response(httpClient.OK)
		obj.send_header('Content-type','text/plain')
		obj.end_headers()
		obj.wfile.write(bytearray(self.chain_name,'utf-8'))		
		return self.ret
		
class MyPathParamHandler(httpUtil.Handler):
	def __init__(self,name,config=None):
		self.name = name
		
	def handle(self, obj : httpServer.BaseHTTPRequestHandler, param_map : dict):
		obj.send_response(httpClient.OK)	
		obj.send_header('Content-type','text/plain')
		obj.end_headers()
		obj.wfile.write(bytearray(self.name,'utf-8'))
		obj.wfile.write(bytearray(json.dumps(param_map, indent = 4),'utf-8'))

class MyChainPathParamHandler(httpUtil.Handler):
	def __init__(self,chain_name,retTF,config=None):
		self.chain_name = chain_name
		self.ret = retTF
		
	def handle(self, obj : httpServer.BaseHTTPRequestHandler, param_map : dict) -> bool:		
		obj.send_response(httpClient.OK)
		obj.send_header('Content-type','text/plain')
		obj.end_headers()
		obj.wfile.write(bytearray(self.chain_name,'utf-8'))
		obj.wfile.write(bytearray(json.dumps(param_map, indent = 4),'utf-8'))
		return self.ret		
		
def RegisterHandler(config):
	'''
	ENTRY POINT: register all handlers in here
	'''
	logging.info('register all handlers ...')
	
	#take note below are just examples on how to register handlers to the url
	#for your own usage please CHANGE THEM to your own handler
	#must implement "interface" in httpUtil.Handler
	httpUtil.register_handler("/hello1", MyHandler('My Handler!',config), [httpUtil.HTTP_METHOD["GET"], httpUtil.HTTP_METHOD["POST"]])
		
	#take note below are just examples on how to register chain handlers to the url
	#usually for chain of handlers, the last handler is the one that write out to client
	#for your own usage please CHANGE THEM to your own handler
	#must implement "interface" in httpUtil.ChainHandler
	httpUtil.register_chain_handler("/hello2", [MyChainHandler("My Chain Handler 1",True,config),MyChainHandler("My Chain Handler 2",True,config)], [httpUtil.HTTP_METHOD["GET"], httpUtil.HTTP_METHOD["POST"]])
		
	#take note below are just examples on how to register regex handlers to the url
	#for your own usage please CHANGE THEM to your own handler
	#must implement "interface" in httpUtil.Handler
	httpUtil.register_handler_regex("^/hello3/.*/123+", MyHandler('My Regex Handler!',config), [httpUtil.HTTP_METHOD["GET"], httpUtil.HTTP_METHOD["POST"]])
	
	#take note below are just examples on how to register chain regex handlers to the url
	#usually for chain of handlers, the last handler is the one that write out to client
	#for your own usage please CHANGE THEM to your own handler
	#must implement "interface" in httpUtil.ChainHandler
	httpUtil.register_chain_handler_regex("^/hello4/.*/456$", [MyChainHandler("My Regex Chain Handler 1",True,config),MyChainHandler("My Regex Chain Handler 2",True,config)], [httpUtil.HTTP_METHOD["GET"], httpUtil.HTTP_METHOD["POST"]])
	
	#take note below are just examples on how to register path param handlers to the url. accepted placeholder are {} and :
	#for your own usage please CHANGE THEM to your own handler
	#must implement "interface" in httpUtil.PathParamHandler
	httpUtil.register_handler_path_param("/hello5/{hi}/:bye", MyPathParamHandler('My Path Param Handler!',config), [httpUtil.HTTP_METHOD["GET"], httpUtil.HTTP_METHOD["POST"]])
	
	#take note below are just examples on how to register path param chain handlers to the url. accepted placeholder are {} and :
	#usually for chain of handlers, the last handler is the one that write out to client
	#for your own usage please CHANGE THEM to your own handler
	#must implement "interface" in httpUtil.ChainPathParamHandler	
	httpUtil.register_chain_handler_path_param("/hello6/{hi}/:bye", [MyChainPathParamHandler("My Path Param Chain Handler 1",True,config),MyChainPathParamHandler("My Path Param Chain Handler 2",True,config)], [httpUtil.HTTP_METHOD["GET"], httpUtil.HTTP_METHOD["POST"]])	
	