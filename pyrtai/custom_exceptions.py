## @package custom_exceptions
# Custom exceptions for the library

## Base class for exceptions in this module
class RtaiError(Exception):
	pass

## Exception raised for errors involving connections
class RtaiConfigError(RtaiError):

	## @var expr
	# Input expression in which the error occurred
	
	## @var msg
	# Explanation of the error
	
	## Saves expr and msg of the error
	def __init__(self, expr, msg):
		self.expr = expr
		self.msg = msg
		
	## Returns string representation of the error
	def __str__(self):
		return repr("%s [Original error: %s]" % (self.msg, self.expr))

## Exception raised for errors involving connections
class RtaiXmlRpcError(RtaiError):
	
	## @var expr
	# Input expression in which the error occurred
	
	## @var msg
	# Explanation of the error
	
	## Saves expr and msg of the error
	def __init__(self, expr, msg):
		self.expr = expr
		self.msg = msg
	
	## Returns string representation of the error
	def __str__(self):
		return repr("%s [Original error: %s]" % (self.msg, self.expr))