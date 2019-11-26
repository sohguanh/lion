import threading

class TokenBucket:
	def __init__(self, maximum_amt=30, refill_duration_sec=30, refill_amt=5):
		'''
		maximum_amt parameter to indicate how many request the url endpoint can handle before rejecting. 
		refill_duration_sec parameter to indicate elapsed how many seconds before refilling. 
		refill_amt to indicate how many to refill. any value that exceed maximum_amt will still be capped to maximum_amt.
		'''
		self.maximum_amt = maximum_amt
		self.current_amt = maximum_amt
		self.refill_duration_sec = refill_duration_sec
		self.refill_amt = refill_amt
		self.lock = threading.Lock()
		
	def __del__(self):
		self.stop_timer()
		
	def start_timer(self):
		self.timer = threading.Timer(self.refill_duration_sec,self.refill).start()
		
	def stop_timer(self):
		if self.timer is not None:
			self.timer.cancel()
	
	def refill(self):
		self.lock.acquire()
		if self.current_amt < self.maximum_amt:
			new_amt = self.current_amt + self.refill_amt
			if new_amt > self.maximum_amt:
				self.current_amt = self.maximum_amt
			else:
				self.current_amt = new_amt				
		self.lock.release()
		self.timer = threading.Timer(self.refill_duration_sec,self.refill).start()
		
	def is_allowed(self) -> bool:
		allowed = True
		self.lock.acquire()
		if self.current_amt > 0:
			self.current_amt = self.current_amt - 1
			allowed = True
		else:
			allowed = False			
		self.lock.release()
		return allowed