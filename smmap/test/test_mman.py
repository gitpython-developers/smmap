from lib import TestBase, FileCreator

from smmap.mman import *
from smmap.mman import MemoryCursor
from smmap.util import PAGESIZE

from smmap.exc import RegionCollectionError

import sys
from copy import copy

class TestMMan(TestBase):
	
	def test_cursor(self):
		man = MappedMemoryManager()
		c = MemoryCursor(man)
		assert not c.is_valid()
		assert not c.is_associated()
		
		# copy module
		
		# assign method
		
		
		
	def test_memory_manager(self):
		man = MappedMemoryManager()
		assert man.num_file_handles() == 0
		assert man.num_open_files() == 0
		assert man.window_size() > 0
		assert man.mapped_memory_size() == 0
		assert man.max_mapped_memory_size() > 0
		assert man.page_size() == PAGESIZE
		
		# collection doesn't raise in 'any' mode
		man._collect_one_lru_region(0)
		# doesn't raise if we are within the limit
		man._collect_one_lru_region(10)
		# raises outside of limit
		self.failUnlessRaises(RegionCollectionError, man._collect_one_lru_region, sys.maxint)
