"""Module containnig a memory memory manager which provides a sliding window on a number of memory mapped files"""

__all__ = ["MappedMemoryManager", "MemoryCursor"]

from util import (
					MemoryWindow,
					MappedRegion,
					MappedRegionList,
				)


class MemoryCursor(object):
	"""Pointer into the mapped region of the memory manager, keeping the current window 
	alive until it is destroyed"""
	__slots__ = ( 
					'_manager',	# the manger keeping all file regions
					'_regions',	# a regions list with regions for our file
					'_region',	# WEAK REF to our current region
					'_ofs',		# relative offset from the actually mapped area to our start area
					'_size'		# maximum size we should provide
				)
	
	def __init__(self, manager = None, regions = None):
		self._manager = manager
		self._regions = regions
		self._region = region
		self._ofs = 0
		self._size = 0
		
	def __del__(self):
		self._destroy()
		
	def _destroy(self):
		"""Destruction code to decrement counters"""
		
	def _copy_from(self, rhs):
		"""Copy all data from rhs into this instance, handles usage count"""
		
	#{ Interface
	
	
	#} END interface
	
	
	
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
	
