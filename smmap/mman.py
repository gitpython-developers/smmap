"""Module containnig a memory memory manager which provides a sliding window on a number of memory mapped files"""

__all__ = ["MappedMemoryManager"]

import os
import mmap

from mmap import PAGESIZE

#{ Utilities

def align_to_page(num, round_up):
	"""Align the given integer number to the closest page offset, which usually is 4096 bytes.
	:param round_up: if True, the next higher multiple of page size is used, otherwise
		the lower page_size will be used (i.e. if True, 1 becomes 4096, otherwise it becomes 0)
	:return: num rounded to closest page"""
	res = (num / PAGESIZE) * PAGESIZE;
	if round_up and (res != num):
		res += PAGESIZE;
	#END handle size
	return res;

#}END utilities

class Window(object):
	"""Utility type which is used to snap windows towards each other, and to adjust their size"""
	__slots__ = (
				'ofs',		# offset into the file in bytes
				'size'				# size of the window in bytes
				)

	def __init__(self, offset, size):
		self.ofs = offset
		self.size = size

	def __repr__(self):
		return "Window(%i, %i)" % (self.ofs, self.size) 

	@classmethod
	def from_region(cls, region):
		""":return: new window from a region"""
		return cls(region.ofs_begin(), region.size())

	def ofs_end(self):
		return self.ofs + self.size

	def align(self):
		self.ofs = align_to_page(self.ofs, 0)
		self.size = align_to_page(self.size, 1)

	def extend_left_to(self, window, max_size):
		"""Adjust the offset to start where the given window on our left ends if possible, 
		but don't make yourself larger than max_size.
		The resize will assure that the new window still contains the old window area"""
		rofs = self.ofs - window.ofs_end()
		nsize = rofs + self.size
		rofs -= nsize - min(nsize, max_size)
		self.ofs = self.ofs - rofs
		self.size += rofs

	def extend_right_to(self, window, max_size):
		"""Adjust the size to make our window end where the right window begins, but don't
		get larger than max_size"""
		self.size = min(self.size + (window.ofs - self.ofs_end()), max_size)


class Region(object):
	"""Defines a mapped region of memory, aligned to pagesizes
	:note: deallocates used region automatically on destruction"""
	__slots__ = (
					'_b'	, 	# beginning of mapping
					'_mf',	# mapped memory chunk (as returned by mmap)
					'_nc',	# number of clients using this region
					'_uc'	# total amount of usages
				)
	
	
	def __init__(self, path, ofs, size):
		"""Initialize a region, allocate the memory map
		:param path: path to the file to map
		:param ofs: **aligned** offset into the file to be mapped 
		:param size: if size is larger then the file on disk, the whole file will be
			allocated the the size automatically adjusted
		:raise Exception: if no memory can be allocated"""
		self._b = ofs
		self._nc = 0
		self._uc = 0
		
		fd = os.open(path, os.O_RDONLY|getattr(os, 'O_BINARY', 0))
		try:
			self._mf = mmap.mmap(fd, size, access=mmap.ACCESS_READ, offset=ofs)
		finally:
			os.close(fd)
		#END close file handle
	

class MappedMemoryManager(object):
	"""Maintains a list of ranges of mapped memory regions in one or more files and allows to easily 
	obtain additional regions assuring there is no overlap.
	Once a certain memory limit is reached globally, or if there cannot be more open file handles 
	which result from each mmap call, the least recently used, and currently unused mapped regions
	are unloaded automatically.
	
	:note: currently not thread-safe !
	:note: in the current implementation, we will automatically unload windows if we either cannot
		create more memory maps (as the open file handles limit is hit) or if we have allocated more than 
		a safe amount of memory already, which would possibly cause memory allocations to fail as our address
		space is full."""
		
	__slots__ = tuple()
	
