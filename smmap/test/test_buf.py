from lib import TestBase, FileCreator

from smmap.mman import MappedMemoryManager
from smmap.buf import *

from random import randint
from time import time
import sys

class TestBuffer(MappedMemoryBuffer):
	#{ Configuration
	manager = MappedMemoryManager()
	#} END configuration
	

class TestBuf(TestBase):
	
	def test_basics(self):
		self.failUnlessRaises(AssertionError, MappedMemoryBuffer)			# needs subclass
		fc = FileCreator(self.k_window_test_size, "buffer_test")
		
		# invalid paths fail upon construction
		self.failUnlessRaises(OSError, TestBuffer, "somefile")				# invalid file
		self.failUnlessRaises(ValueError, TestBuffer, fc.path, fc.size)		# offset too large
		
		buf = TestBuffer()												# can create uninitailized buffers
		assert not buf.cursor().is_valid() and not buf.cursor().is_associated()
		
		# can call end access any time
		buf.end_access()
		buf.end_access()
		
		# begin access can revive it, if the offset is suitable
		offset = 100
		assert buf.begin_access(fc.path, fc.size) == False
		assert buf.begin_access(fc.path, offset) == True
		
		# empty begin access keeps it valid on the same path, but alters the offset
		assert buf.begin_access() == True
		assert buf.cursor().is_valid()
		
		# simple access
		data = open(fc.path, 'rb').read()
		assert data[offset] == buf[0]
		assert data[offset:offset*2] == buf[0:offset]
		
		# end access makes its cursor invalid
		buf.end_access()
		assert not buf.cursor().is_valid()
		assert buf.cursor().is_associated()			# but it remains associated
		
		# an empty begin access fixes it up again
		assert buf.begin_access() == True and buf.cursor().is_valid()
		del(buf)		# ends access automatically
		
		man = TestBuffer.manager
		assert man.num_file_handles() == 1
		
		# PERFORMANCE
		# blast away with rnadom access and a full mapping - we don't want to 
		# exagerate the manager's overhead, but measure the buffer overhead
		# We do it once with an optimal setting, and with a worse manager which 
		# will produce small mappings only !
		max_num_accesses = 5000
		num_accesses_left = max_num_accesses
		
		for manager in (MappedMemoryManager(window_size=fc.size/100, max_memory_size=fc.size/3, max_open_handles=15), man):
			TestBuffer.manager = manager
			st = time()
			buf = TestBuffer(fc.path)
			assert manager.num_file_handles() == 1
			num_bytes = 0
			fsize = fc.size
			while num_accesses_left:
				num_accesses_left -= 1
				ofs_start = randint(0, fsize)
				ofs_end = randint(ofs_start, fsize)
				d = buf[ofs_start:ofs_end]
				assert len(d) == ofs_end - ofs_start
				assert d == data[ofs_start:ofs_end]
				num_bytes += len(d)
				pos = randint(0, fsize)
				assert buf[pos] == data[pos]
			# END handle num accesses
			buf.end_access()
			assert manager.num_file_handles() == 1
			assert manager.collect() == 1
			assert manager.num_file_handles() == 0
			elapsed  = time() - st
			mb = 1000*1000
			sys.stderr.write("Made %i random slices to buffer reading a total of %f mb in %f s (%f mb/s)\n" % (max_num_accesses, num_bytes/mb, elapsed, (num_bytes/mb)/elapsed)) 
		# END for each manager
