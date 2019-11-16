#!/usr/bin/python

import urllib.request as req
import urllib.error as urlError
import threading as threading
import http.server as httpServer
import signal
import logging

import util.http as httpUtil
import config

def ping(config):
	try:
		contents = req.urlopen("".join(["http://",config['Site']['Url'],":",str(config['Site']['Port'])]),timeout=config['Site']['CheckAliveTimeoutSec']).read()
		logging.info('server started up ...')
	except urlError.URLError as e:
		logging.error('error contact server: '+str(e.reason))
		
def signal_handler(sig, frame):
	logging.info("received an interrupt signal, server shutting down ...")	
	t = threading.Thread(target=httpUtil.ShutdownCleanup,args=(config,))
	t.start()
	t.join(config['Site']['GracefulShutdownSec'])
	raise Exception
	
if __name__ == "__main__":
	try:
		signal.signal(signal.SIGINT, signal_handler)
		config = config.Config().get_instance()		
		threads = [ threading.Thread(target=httpUtil.StartupInit,args=(config,)), threading.Thread(target=httpUtil.RegisterHandler,args=(config,)) ]
		for t in threads:
			t.start()
		for t in threads:
			t.join()
		reqHandler = httpUtil.RequestHandler
		reqHandler.initialize(reqHandler, config)
		server = httpServer.ThreadingHTTPServer((config['Site']['Url'], config["Site"]["Port"]), reqHandler)
		logging.info("server starting up ...")
		threading.Thread(target=ping,args=(config,)).start()
		server.serve_forever()
	except Exception as e:
		logging.error(str(e))
	finally:
		server.socket.close()