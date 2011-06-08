from lib import TestBase, FileCreator

from smmap.mman import *
from smmap.mman import Region
from smmap.mman import Window

import sys
import mmap

class TestMMan(TestBase):
	
	_window_test_size = 1000 * 1000 * 8 + 5195
	
	def test_window(self):
		wl = Window(0, 1)	 	# left
		wc = Window(1, 1)		# center
		wc2 = Window(10, 5)		# another center
		wr = Window(8000, 50)	# right
		
		assert wl.ofs_end() == 1
		assert wc.ofs_end() == 2
		assert wr.ofs_end() == 8050
		
		# extension does nothing if already in place
		maxsize = 100
		wc.extend_left_to(wl, maxsize)
		assert wc.ofs == 1 and wc.size == 1
		wl.extend_right_to(wc, maxsize)
		wl.extend_right_to(wc, maxsize)
		assert wl.ofs == 0 and wl.size == 1
		
		# an actual left extension
		pofs_end = wc2.ofs_end()
		wc2.extend_left_to(wc, maxsize)
		assert wc2.ofs == wc.ofs_end() and pofs_end == wc2.ofs_end() 
		
		
		# respects maxsize
		wc.extend_right_to(wr, maxsize)
		assert wc.ofs == 1 and wc.size == maxsize
		wc.extend_right_to(wr, maxsize)
		assert wc.ofs == 1 and wc.size == maxsize
		
		# without maxsize
		wc.extend_right_to(wr, sys.maxint)
		assert wc.ofs_end() == wr.ofs and wc.ofs == 1
		
		# extend left
		wr.extend_left_to(wc2, maxsize)
		wr.extend_left_to(wc2, maxsize)
		assert wr.size == maxsize
		
		wr.extend_left_to(wc2, sys.maxint)
		assert wr.ofs == wc2.ofs_end()
		
		wc.align()
		assert wc.ofs == 0 and wc.size == mmap.PAGESIZE*2
		
	
	def test_region(self):
		fc = FileCreator(self._window_test_size, "window_test")
		rfull = Region(fc.path, 0, fc.size)
		
		
		
		Window.from_region # todo
		pass
		
	def test_basics(self):
		pass
