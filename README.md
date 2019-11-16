# lion
Python mini-web framework (Python 3.X and above)

**How to use lion framework**

*Step 1*
Ensure config/config.json are setup correctly for your environment.

*Step 2*
Start to add your application specific code in util/http/handler_util.py. Refer to the extensive comments in the file to learn how to add your own handler for the url.

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
Use a browser and navigate to your configured url in Step 1 config.json e.g http://localhost:8000
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

**Contact**

Any bug/suggestion/feedback can mail to sohguanh@gmail.com

:lion: :lion: :lion:
