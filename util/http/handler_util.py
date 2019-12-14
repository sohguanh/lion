import http.server as httpServer
import http.client as httpClient
import json
import logging

import config
import util.http as httpUtil
import util.template as templateUtil
import util.ratelimiter as rateLimiter
import util.i18n as i18nUtil


def startup_init(config, dbPool):
    '''
    ENTRY POINT: perform any pre-loading/caching of objects or anything else before server startup in here (if any)
    '''
    logging.info('startup init ...')

    # take note below is an example on how to use dbPool
    if dbPool is not None:
        conn = dbPool.get_connection()
        cursor = conn.cursor()
        query = ("SELECT CURRENT_DATE()")
        cursor.execute(query)
        for curr_date in cursor:
            logging.info(curr_date)
        cursor.close()
        conn.close()


def shutdown_cleanup(config, dbPool):
    '''
    ENTRY POINT: perform any cleaning up of objects or anything else before server shutdown in here (if any)
    '''
    logging.info('shutdown cleanup ...')


class MyHandler(httpUtil.Handler):
    def __init__(self, name, config=None):
        self.name = name

    def handle(self, obj: httpServer.BaseHTTPRequestHandler):
        obj.send_response(httpClient.OK)
        obj.send_header('Content-type', 'text/plain')
        obj.end_headers()
        obj.wfile.write(bytearray(self.name, 'utf-8'))
        url_param_map = httpUtil.get_url_param_map(obj)
        obj.wfile.write(bytearray(str(url_param_map) if url_param_map is not None else str('{}'), 'utf-8'))


class MyChainHandler(httpUtil.ChainHandler):
    def __init__(self, chain_name, retTF, config=None):
        self.chain_name = chain_name
        self.ret = retTF
        self.config = config

    def handle(self, obj: httpServer.BaseHTTPRequestHandler) -> bool:
        obj.send_response(httpClient.OK)
        obj.send_header('Content-type', 'text/html; charset=utf-8')
        obj.end_headers()
        obj.wfile.write(bytearray(self.chain_name, 'utf-8'))
        tpl = templateUtil.get_template("helloworld")
        if tpl is not None:
            rb_en_US = i18nUtil.ResourceBundle.get_bundle(self.config, "messages", i18nUtil.Locale("en", "US"))
            rb_zh_CN = i18nUtil.ResourceBundle.get_bundle(self.config, "messages", i18nUtil.Locale("zh", "CN"))
            rb_zh_TW = i18nUtil.ResourceBundle.get_bundle(self.config, "messages", i18nUtil.Locale("zh", "TW"))
            param = {
                'Title': 'Lion',
                'Greeting1': rb_en_US['how.are.you'],
                'Greeting2': rb_zh_CN['how.are.you'],
                'Greeting3': rb_zh_TW['how.are.you'],
                'SpecialDate1': rb_en_US['special.date'].format('03', 12, 1974),
                'SpecialDate2': rb_zh_CN['special.date'].format(1974, 12, '03'),
                'SpecialDate3': rb_zh_TW['special.date'].format(1974, 12, '03')
            }
            obj.wfile.write(bytearray(tpl.safe_substitute(param), 'utf-8'))
        return self.ret


class MyPathParamHandler(httpUtil.Handler):
    def __init__(self, name, config=None):
        self.name = name

    def handle(self, obj: httpServer.BaseHTTPRequestHandler, param_map: dict):
        obj.send_response(httpClient.OK)
        obj.send_header('Content-type', 'text/plain')
        obj.end_headers()
        obj.wfile.write(bytearray(self.name, 'utf-8'))
        obj.wfile.write(bytearray(json.dumps(param_map, indent=4), 'utf-8'))


class MyChainPathParamHandler(httpUtil.Handler):
    def __init__(self, chain_name, retTF, config=None):
        self.chain_name = chain_name
        self.ret = retTF

    def handle(self, obj: httpServer.BaseHTTPRequestHandler, param_map: dict) -> bool:
        obj.send_response(httpClient.OK)
        obj.send_header('Content-type', 'text/plain')
        obj.end_headers()
        obj.wfile.write(bytearray(self.chain_name, 'utf-8'))
        obj.wfile.write(bytearray(json.dumps(param_map, indent=4), 'utf-8'))
        return self.ret


class MyTokenBucketHandler(httpUtil.ChainHandler):
    def __init__(self, maximum_amt=30, refill_duration_sec=30, refill_amt=5):
        self.token_bucket = rateLimiter.TokenBucket(maximum_amt, refill_duration_sec, refill_amt)
        self.token_bucket.start_timer()

    def stop_timer(self):
        if self.token_bucket is not None:
            self.token_bucket.stop_timer()

    def handle(self, obj: httpServer.BaseHTTPRequestHandler) -> bool:
        allowed = self.token_bucket.is_allowed()
        if not allowed:
            httpUtil.default_not_found(obj)
        return allowed


class MySlidingWindowHandler(httpUtil.ChainHandler):
    def __init__(self, request_per_min=30):
        self.sliding_window = rateLimiter.SlidingWindow(request_per_min)

    def handle(self, obj: httpServer.BaseHTTPRequestHandler) -> bool:
        allowed = self.sliding_window.is_allowed()
        if not allowed:
            httpUtil.default_not_found(obj)
        return allowed


def register_handlers(config, dbPool):
    '''
    ENTRY POINT: register all handlers in here
    '''
    logging.info('register all handlers ...')

    # take note below are just examples on how to register handlers to the url
    # for your own usage please CHANGE THEM to your own handler
    # must implement "interface" in httpUtil.Handler
    httpUtil.register_handler("/hello1", MyHandler('My Handler!', config), [httpUtil.HTTP_METHOD["GET"], httpUtil.HTTP_METHOD["POST"]])

    # take note below are just examples on how to register chain handlers to the url
    # usually for chain of handlers, the last handler is the one that write out to client
    # for your own usage please CHANGE THEM to your own handler
    # must implement "interface" in httpUtil.ChainHandler
    httpUtil.register_chain_handler("/hello2", [MyChainHandler("My Chain Handler 1", True, config), MyChainHandler("My Chain Handler 2", True, config)], [httpUtil.HTTP_METHOD["GET"], httpUtil.HTTP_METHOD["POST"]])

    # take note below are just examples on how to register regex handlers to the url
    # for your own usage please CHANGE THEM to your own handler
    # must implement "interface" in httpUtil.Handler
    httpUtil.register_handler_regex("^/hello3/.*/123+", MyHandler('My Regex Handler!', config), [httpUtil.HTTP_METHOD["GET"], httpUtil.HTTP_METHOD["POST"]])

    # take note below are just examples on how to register chain regex handlers to the url
    # usually for chain of handlers, the last handler is the one that write out to client
    # for your own usage please CHANGE THEM to your own handler
    # must implement "interface" in httpUtil.ChainHandler
    httpUtil.register_chain_handler_regex("^/hello4/.*/456$", [MyChainHandler("My Regex Chain Handler 1", True, config), MyChainHandler("My Regex Chain Handler 2", True, config)], [httpUtil.HTTP_METHOD["GET"], httpUtil.HTTP_METHOD["POST"]])

    # take note below are just examples on how to register path param handlers to the url. accepted placeholder are {} and :
    # for your own usage please CHANGE THEM to your own handler
    # must implement "interface" in httpUtil.PathParamHandler
    httpUtil.register_handler_path_param("/hello5/{hi}/:bye", MyPathParamHandler('My Path Param Handler!', config), [httpUtil.HTTP_METHOD["GET"], httpUtil.HTTP_METHOD["POST"]])

    # take note below are just examples on how to register path param chain handlers to the url. accepted placeholder are {} and :
    # usually for chain of handlers, the last handler is the one that write out to client
    # for your own usage please CHANGE THEM to your own handler
    # must implement "interface" in httpUtil.ChainPathParamHandler
    httpUtil.register_chain_handler_path_param("/hello6/{hi}/:bye", [MyChainPathParamHandler("My Path Param Chain Handler 1", True, config), MyChainPathParamHandler("My Path Param Chain Handler 2", True, config)], [httpUtil.HTTP_METHOD["GET"], httpUtil.HTTP_METHOD["POST"]])

    data = httpUtil.get_handler_rules(config, dbPool)
    if data is not None:
        for item in data["handlers"]:
            if item["Mode"] in ['handler', 'handler_regex', 'handler_path_param']:
                klass = item["Handler"][0]
                obj = httpUtil.import_class_from_string(klass["Klass"])()
                for attr in klass["Attributes"]:
                    for key, value in attr.items():
                        setattr(obj, key, value)
                if item["Mode"] == 'handler':
                    httpUtil.register_handler(item["Url"], obj, item["Methods"])
                elif item["Mode"] == 'handler_regex':
                    httpUtil.register_handler_regex(item["Url"], obj, item["Methods"])
                elif item["Mode"] == 'handler_path_param':
                    httpUtil.register_handler_path_param(item["Url"], obj, item["Methods"])
            elif item["Mode"] in ['chain_handler', 'chain_handler_regex', 'chain_handler_path_param']:
                objArr = []
                for klass in item["Handler"]:
                    obj = httpUtil.import_class_from_string(klass["Klass"])()
                    for attr in klass["Attributes"]:
                        for key, value in attr.items():
                            setattr(obj, key, value)
                    objArr.append(obj)
                if item["Mode"] == 'chain_handler':
                    httpUtil.register_chain_handler(item["Url"], objArr, item["Methods"])
                elif item["Mode"] == 'chain_handler_regex':
                    httpUtil.register_chain_handler_regex(item["Url"], objArr, item["Methods"])
                elif item["Mode"] == 'chain_handler_path_param':
                    httpUtil.register_chain_handler_path_param(item["Url"], objArr, item["Methods"])

    # take note below are just examples on how to add rewrite url. source_url parameter accepted placeholder are {} and : and target_url parameter substituition syntax is $1 $ 2 etc
    data = httpUtil.get_rewrite_rules(config, dbPool)
    if data is not None:
        for item in data["rules"]:
            if item["Mode"] == httpUtil.REWRITE_MODE["D"]:
                httpUtil.add_rewrite_url(item["SourceUrl"], item["TargetUrl"])
            elif item["Mode"] == httpUtil.REWRITE_MODE["R"]:
                httpUtil.add_rewrite_url_regex(item["SourceUrl"], item["TargetUrl"])
            elif item["Mode"] == httpUtil.REWRITE_MODE["P"]:
                httpUtil.add_rewrite_url_path_param(item["SourceUrl"], item["TargetUrl"])
    else:
        httpUtil.add_rewrite_url("/test/me/1", "/hello1")
        httpUtil.add_rewrite_url("/test/me/2", "/hello2")
        httpUtil.add_rewrite_url_regex("^/test/me/[3]$", "/hello3/aaa/123")
        httpUtil.add_rewrite_url_regex("^/test/me/[4]$", "/hello4/bbb/456")
        httpUtil.add_rewrite_url_path_param("/test/me/5/{hi}/:bye", "/hello5/$1/$2")
        httpUtil.add_rewrite_url_path_param("/test/me/6/{hi}/:bye", "/hello6/$1/$2")

    # take note below are just examples on how to use endpoint rate limiter using token bucket algorithm
    httpUtil.register_chain_handler("/hello7", [MyTokenBucketHandler(2, 5, 1), MyChainHandler("My Chain Handler 7", True, config)], [httpUtil.HTTP_METHOD["GET"], httpUtil.HTTP_METHOD["POST"]])

    # take note below are just examples on how to use endpoint rate limiter using sliding window algorithm
    httpUtil.register_chain_handler("/hello8", [MySlidingWindowHandler(2), MyChainHandler("My Chain Handler 8", True, config)], [httpUtil.HTTP_METHOD["GET"], httpUtil.HTTP_METHOD["POST"]])
