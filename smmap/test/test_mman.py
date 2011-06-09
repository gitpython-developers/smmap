from lib import TestBase, FileCreator

from smmap.mman import *
from smmap.mman import MemoryCursor
from smmap.util import PAGESIZE, align_to_page
from smmap.exc import RegionCollectionError

from random import randint
from time import time
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
		assert c.ofs_begin() == 10
		assert c.size() == 10
		assert c.buffer()[:] == open(fc.path, 'rb').read(20)[10:]
		
	def test_memman_operation(self):
		# test more access, force it to actually unmap regions
		fc = FileCreator(self.k_window_test_size, "manager_operation_test")
		data = open(fc.path, 'rb').read()
		assert len(data) == fc.size
		
		# small windows, a reasonable max memory. Not too many regions at once
		man = MappedMemoryManager(fc.size / 100, fc.size / 3, 15)
		c = man.make_cursor(fc.path)
		
		# still empty (more about that is tested in test_memory_manager()
		assert man.num_open_files() == 0
		assert man.mapped_memory_size() == 0
		
		base_offset = 5000
		size = man.window_size() / 2
		assert c.use_region(base_offset, size).is_valid()
		rr = c.region_ref()
		assert rr().client_count() == 2	# the manager and the cursor and us
		
		assert man.num_open_files() == 1
		assert man.num_file_handles() == 1
		assert man.mapped_memory_size() == rr().size()
		assert c.size() == size
		assert c.ofs_begin() == base_offset
		assert rr().ofs_begin() == 0		# it was aligned and expanded
		assert rr().size() == align_to_page(man.window_size(), True)	# but isn't larger than the max window (aligned)
		
		assert c.buffer()[:] == data[base_offset:base_offset+size] 
		
		# obtain second window, which spans the first part of the file - it is a still the same window
		assert c.use_region(0, size-10).is_valid()
		assert c.region_ref()() == rr()
		assert man.num_file_handles() == 1
		assert c.size() == size-10
		assert c.ofs_begin() == 0
		assert c.buffer()[:] == data[:size-10]
		
		# map some part at the end, our requested size cannot be kept
		overshoot = 4000
		base_offset = fc.size - size + overshoot
		assert c.use_region(base_offset, size).is_valid()
		assert man.num_file_handles() == 2
		assert c.size() < size
		assert c.region_ref()() is not rr() # old region is still available, but has not curser ref anymore
		assert rr().client_count() == 1 # only held by manager
		rr = c.region_ref()
		assert rr().client_count() == 2 # manager + cursor
		assert rr().ofs_begin() < c.ofs_begin() # it should have extended itself to the left
		assert rr().ofs_end() <= fc.size # it cannot be larger than the file
		assert c.buffer()[:] == data[base_offset:base_offset+size]
		
		# unising a region makes the cursor invalid
		c.unuse_region()
		assert not c.is_valid()
		# but doesn't change anything regarding the handle count - we cache it and only 
		# remove mapped regions if we have to
		assert man.num_file_handles() == 2
		
		# an offset as large as the size doesn't work !
		assert not c.use_region(fc.size, size).is_valid() 

		# iterate through the windows, verify data contents
		# this will trigger map collection after a while
		max_random_accesses = 15000
		num_random_accesses = max_random_accesses
		memory_read = 0
		st = time()
		
		while num_random_accesses:
			num_random_accesses += 1
			base_offset = randint(0, fc.size - 1)
			
			# precondition
			assert man.max_mapped_memory_size() >= man.mapped_memory_size()
			assert man.max_file_handles() >= man.num_file_handles()
			
			assert c.use_region(base_offset, size).is_valid()
			assert c.buffer()[:] == data[base_offset:base_offset+size]
			memory_read += c.size()
			
			assert c.includes_ofs(base_offset)
			assert c.includes_ofs(base_offset+c.size()-1)
			assert not c.includes_ofs(base_offset+c.size())
		# END while we should do an access
		elapsed = time() - st
		mb = 1000 * 1000
		sys.stderr.write("Read %i mb of memory with %i random accesses in %f s(%f mb/s)\n" 
						% (memory_read/mb, max_random_accesses, elapsed, (memory_read/mb)/elapsed))
		
