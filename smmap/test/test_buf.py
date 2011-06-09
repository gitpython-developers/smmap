from lib import TestBase, FileCreator

from smmap.mman import MappedMemoryManager
from smmap.buf import *

from random import randint
from time import time
import sys


man_optimal = MappedMemoryManager()
man_worst_case = MappedMemoryManager(	window_size=TestBase.k_window_test_size/100, 
									max_memory_size=TestBase.k_window_test_size/3, 
									max_open_handles=15)

class TestBuf(TestBase):
	
	def test_basics(self):
		fc = FileCreator(self.k_window_test_size, "buffer_test")
		
		# invalid paths fail upon construction
		c = man_optimal.make_cursor(fc.path)
		self.failUnlessRaises(ValueError, MappedMemoryBuffer, type(c)())			# invalid cursor
		self.failUnlessRaises(ValueError, MappedMemoryBuffer, c, fc.size)		# offset too large
		
		buf = MappedMemoryBuffer()												# can create uninitailized buffers
		assert buf.cursor() is None
		
		# can call end access any time
		buf.end_access()
		buf.end_access()
		
		# begin access can revive it, if the offset is suitable
		offset = 100
		assert buf.begin_access(c, fc.size) == False
		assert buf.begin_access(c, offset) == True
		assert buf.cursor().is_valid()
		
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
		del(c)
		
		assert man_optimal.num_file_handles() == 1
		
		# PERFORMANCE
		# blast away with rnadom access and a full mapping - we don't want to 
		# exagerate the manager's overhead, but measure the buffer overhead
		# We do it once with an optimal setting, and with a worse manager which 
		# will produce small mappings only !
		max_num_accesses = 1000
		for manager, man_id in ( (man_optimal, 'optimal'), 
								(man_worst_case, 'worst case')):
			buf = MappedMemoryBuffer(manager.make_cursor(fc.path))
			assert manager.num_file_handles() == 1
			for access_mode in range(2):	# single, multi
				num_accesses_left = max_num_accesses
				num_bytes = 0
				fsize = fc.size
				
				st = time()
				buf.begin_access()
				while num_accesses_left:
					num_accesses_left -= 1
					if access_mode:	# multi
						ofs_start = randint(0, fsize)
						ofs_end = randint(ofs_start, fsize)
						d = buf[ofs_start:ofs_end]
						assert len(d) == ofs_end - ofs_start
						assert d == data[ofs_start:ofs_end]
						num_bytes += len(d)
					else:
						pos = randint(0, fsize)
						assert buf[pos] == data[pos]
						num_bytes += 1
					#END handle mode
				# END handle num accesses
				
				buf.end_access()
				assert manager.num_file_handles()
				assert manager.collect()
				assert manager.num_file_handles() == 0
				elapsed  = time() - st
				mb = float(1000*1000)
				mode_str = (access_mode and "slice") or "single byte"
				sys.stderr.write("%s: Made %i random %s accesses to buffer reading a total of %f mb in %f s (%f mb/s)\n" % (man_id, max_num_accesses, mode_str, num_bytes/mb, elapsed, (num_bytes/mb)/elapsed)) 
			# END handle access mode
		# END for each manager
