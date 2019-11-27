#!/usr/bin/python

import urllib.request as req
import urllib.error as urlError
import threading as threading
import http.server as httpServer
import signal
import logging
import os

import util.http as httpUtil
import config
import util.db as dbUtil
import util.template as templateUtil


def ping(config):
    try:
        _ = req.urlopen("".join(["http://", config['Site']['Url'], ":", str(config['Site']['Port'])]), timeout=config['Site']['CheckAliveTimeoutSec']).read()
        logging.info('server started up ...')
    except urlError.URLError as e:
        logging.error('error contact server: '+str(e.reason))


def signal_handler(sig, frame):
    logging.info("received an interrupt signal, server shutting down ...")
    t = threading.Thread(target=httpUtil.shutdown_cleanup, args=(config, dbPool))
    t.start()
    t.join(config['Site']['GracefulShutdownSec'])
    raise Exception


if __name__ == "__main__":
    try:
        signal.signal(signal.SIGINT, signal_handler)
        config = config.Config().get_instance()
        # dbPool = dbUtil.Db(config).get_instance(config) #uncomment this line once MySQL is up
        dbPool = None  # comment/remove this line once MySQL is up
        threads = [threading.Thread(target=httpUtil.startup_init, args=(config, dbPool)), threading.Thread(target=httpUtil.register_handlers, args=(config, dbPool))]
        if config['TemplateConfig']['Enable']:
            threads.append(threading.Thread(target=templateUtil.register_template, args=(config, dbPool)))
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        reqHandler = httpUtil.RequestHandler
        reqHandler.initialize(reqHandler, config)
        server = httpServer.ThreadingHTTPServer((config['Site']['Url'], config["Site"]["Port"]), reqHandler)
        logging.info("server starting up ...")
        threading.Thread(target=ping, args=(config, )).start()
        server.serve_forever()
    except Exception as e:
        logging.error(str(e))
    finally:
        server.socket.close()
    os.kill(os.getpid(), signal.SIGTERM)
