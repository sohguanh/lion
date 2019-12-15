# lion
Python mini-web framework (Python 3.X and above)

**How to use lion framework**

*Step 1*
Ensure config/config.json are setup correctly for your environment.

*Step 2*
All application specific code are to be added inside util/http/handler_util.py. Refer to the extensive comments in the file to learn how to add your own handler for the url. def register_handlers to register your handler. def startup_init show a small example on how to use dbPool which interface with MySQL.

*Step 3*
If your application specific handlers are very simple, you can configure them inside config/handlers.json. Similarly if your url rewrite rules are very simple, you can configure them inside config/urlrewrite.json

The code snippet to read from config file and register handers are in util/http/handler_util.py from line 172 onwards.

```
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
```

The code snippet to read from config file and register url rewrite rules are in util/http/handler_util.py from line 203 onwards.
```
    data = httpUtil.get_rewrite_rules(config, dbPool)
    if data is not None:
        for item in data["rules"]:
            if item["Mode"] == httpUtil.REWRITE_MODE["D"]:
                httpUtil.add_rewrite_url(item["SourceUrl"], item["TargetUrl"])
            elif item["Mode"] == httpUtil.REWRITE_MODE["R"]:
                httpUtil.add_rewrite_url_regex(item["SourceUrl"], item["TargetUrl"])
            elif item["Mode"] == httpUtil.REWRITE_MODE["P"]:
                httpUtil.add_rewrite_url_path_param(item["SourceUrl"], item["TargetUrl"])
```

*Step 4*
Once you get the hang of how the framework works and want to start coding from the bare minimum please refer to below.
1. Remove or move elsewhere the existing util/http/handler_util.py
2. Rename existing util/http/handler_util_bare.py to util/http/handler_util.py
3. You can now start to code from the bare minimum

*Step 5*
For MySQL interfacing, please take note by default it is turned off at code level. Once you get MySQL up and MySQL Connector dependency package installed, please refer to existing ```lion.py``` The comments are quite clear on how to turn off and on. You just need to comment and uncomment the relevant lines.
- line 37        # dbPool = dbUtil.Db(config).get_instance(config) #uncomment this line once MySQL is up
- line 38        dbPool = None  # comment/remove this line once MySQL is up

**Different methods for registering handlers to url**
```
httpUtil.register_handler
httpUtil.register_chain_handler
httpUtil.register_handler_regex
httpUtil.register_chain_handler_regex
httpUtil.register_handler_path_param
httpUtil.register_chain_handler_path_param
```

**"Interface" Class**
```
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
```

*Step 3*
From Windows Command Prompt or Linux terminal, type <path_to_python3.X> lion.py or <path_to_python3.X> lion.py &

*Step 4*
Use a browser and navigate to your configured url in Step 1 config.json e.g ht&#8203;tp://localhost:8000
You should see a message I am alive! This mean your http server is up and running.
To shutdown, send a SIGINT signal. Ctrl-C for Windows Command Prompt. kill -SIGINT <pid> for Linux.
  
**Sample url based on the example code**

| Description | Url |
| --- | --- |
| root | ht&#8203;tp://localhost:8000 |
| handler | ht&#8203;tp://localhost:8000/hello1 |
| chain_handler | ht&#8203;tp://localhost:8000/hello2 |
| handler_regex | ht&#8203;tp://localhost:8000/hello3/abc/123 |
| chain_handler_regex | ht&#8203;tp://localhost:8000/hello4/abc/456  |
| handler_path_param | ht&#8203;tp://localhost:8000/hello5/123/456 | 
| chain_handler_path_param | ht&#8203;tp://localhost:8000/hello6/123/456 | 

**Sample rewrite url based on the example code**

You can add the url rewrite rules inside util/http/handler_util.py or configure them inside config/urlrewrite.json

| Source Url | Target Url |
| --- | --- |
| ht&#8203;tp://localhost:8000/test/me/1 | ht&#8203;tp://localhost:8000/hello1 |
| ht&#8203;tp://localhost:8000/test/me/2 | ht&#8203;tp://localhost:8000/hello2 |
| ht&#8203;tp://localhost:8000/test/me/3 | ht&#8203;tp://localhost:8000/hello3/abc/123 |
| ht&#8203;tp://localhost:8000/test/me/4 | ht&#8203;tp://localhost:8000/hello4/abc/456  |
| ht&#8203;tp://localhost:8000/test/me/5/123/456 | ht&#8203;tp://localhost:8000/hello5/123/456 | 
| ht&#8203;tp://localhost:8000/test/me/6/123/456 | ht&#8203;tp://localhost:8000/hello6/123/456 |

**Internalization aka i18n**

Implementation is **different** from Python normal approach. It is model after Java Locale, ResourceBundle, .properties file concept instead. Follow below steps to understand how to use. Then change accordingly to your needs.

*Step 1*
Inside config/config.json configure under i18nConfig. The attribute names are self-explanatory.
```
"i18nConfig" : {
	"Enable" : true,
	"Path" : "templates/i18n",
	"FileExt" : ".properties"				
}
```

*Step 2*
Refer to util/http/handler_util.py under MyChainHandler code section to see how to use.
```
import util.i18n as i18nUtil
...
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
```

*Step 3*
Go to ht&#8203;tp://localhost:8000/hello2 and you should be able to see the webpage that render English, Simplified Chinese and Traditional Chinese labels.

**Install below Python MySQL Connector dependency package separately**

*Step 1* 
Go to https://dev.mysql.com/downloads/connector/python/

Select Operating System -> Platform Independent

Choose either mysql-connector-python-8.0.18.tar.gz or mysql-connector-python-8.0.18.zip

*Step 2* 
Unzip mysql-connector-python-8.0.18.zip to a folder e.g C:\Python\mysql-connector-python-8.0.18

*Step 3* 
Open a Command Prompt. 

Add Python to the PATH if it has not been done when you install Python 3.X

e.g ```set PATH=C:\Python\Python38;%PATH%``` followed by ```echo %PATH%```

cd C:\Python\mysql-connector-python-8.0.18 and type ```python setup.py install```

*Step 4*
C:\Python\Python3.X\Lib\site-packages\mysql* folders should appear

**Contact**

Any bug/suggestion/feedback can mail to sohguanh@gmail.com

:lion: :lion: :lion:
