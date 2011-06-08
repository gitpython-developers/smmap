from lib import TestBase, FileCreator

from copy import copy
from smmap.mman import *
from smmap.mman import MemoryCursor

class TestMMan(TestBase):
	
	def test_cursor(self):
		man = MappedMemoryManager()
		c = MemoryCursor(man)
		assert not c.is_valid()
		assert not c.is_associated()
		
		# copy module
		
		# assign method
		
		
		
	def test_memory_manager(self):
		pass
