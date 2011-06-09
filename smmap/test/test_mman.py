from lib import TestBase, FileCreator

from smmap.mman import *
from smmap.mman import MemoryCursor
from smmap.util import PAGESIZE

from smmap.exc import RegionCollectionError

import sys
from copy import copy

class TestMMan(TestBase):
	
	def test_cursor(self):
		fc = FileCreator(self.k_window_test_size, "cursor_test")
		
		man = MappedMemoryManager()
		ci = MemoryCursor(man)	# invalid cursor
		assert not ci.is_valid()
		assert not ci.is_associated()
		assert ci.size() == 0		# this is cached, so we can query it in invalid state
		
		cv = man.make_cursor(fc.path)
		assert not cv.is_valid()	# no region mapped yet
		assert cv.is_associated()# but it know where to map it from
		assert cv.file_size() == fc.size
		assert cv.path() == fc.path
		
		# copy module
		cio = copy(cv)
		assert not cio.is_valid() and cio.is_associated()
		
		# assign method
		assert not ci.is_associated()
		ci.assign(cv)
		assert not ci.is_valid() and ci.is_associated()
		
		# unuse non-existing region is fine
		cv.unuse_region()
		cv.unuse_region()
		
		# destruction is fine (even multiple times)
		cv._destroy()
		MemoryCursor(man)._destroy()
		
	def test_memory_manager(self):
		man = MappedMemoryManager()
		assert man.num_file_handles() == 0
		assert man.num_open_files() == 0
		assert man.window_size() > 0
		assert man.mapped_memory_size() == 0
		assert man.max_mapped_memory_size() > 0
		assert man.page_size() == PAGESIZE
		
		# collection doesn't raise in 'any' mode
		man._collect_lru_region(0)
		# doesn't raise if we are within the limit
		man._collect_lru_region(10)
		# raises outside of limit
		self.failUnlessRaises(RegionCollectionError, man._collect_lru_region, sys.maxint)
		
		
		# use a region, verify most basic functionality
		fc = FileCreator(self.k_window_test_size, "manager_test")
		c = man.make_cursor(fc.path)
		assert c.use_region(10, 10).is_valid()
