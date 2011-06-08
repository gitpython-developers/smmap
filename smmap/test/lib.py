"""Provide base classes for the test system"""
from unittest import TestCase

__all__ = ['TestBase']


class TestBase(TestCase):
	"""Foundation used by all tests"""
	
	#{ Configuration
	
	#} END configuration
	
	#{ Overrides
	@classmethod
	def setUpAll(cls):
		# nothing for now
		pass
		
	#END overrides
	
	#{ Interface
	
	#} END interface
