"""Module containnig a memory memory manager which provides a sliding window on a number of memory mapped files"""
from util import (
					MemoryWindow,
					MappedRegion,
					MappedRegionList,
				)

from weakref import proxy

__all__ = ["MappedMemoryManager"]
#{ Utilities

#}END utilities

class MemoryCursor(object):
	"""Pointer into the mapped region of the memory manager, keeping the current window 
	alive until it is destroyed.
	
	Cursors should not be created manually, but are instead returned by the MappedMemoryManager"""
	__slots__ = ( 
					'_manager',	# the manger keeping all file regions
					'_rlist',	# a regions list with regions for our file
					'_region',	# our current region or None
					'_ofs',		# relative offset from the actually mapped area to our start area
					'_size'		# maximum size we should provide
				)
	
	def __init__(self, manager = None, regions = None):
		self._manager = manager
		self._rlist = regions
		self._region = None
		self._ofs = 0
		self._size = 0
		
	def __del__(self):
		self._destroy()
		
	def _destroy(self):
		"""Destruction code to decrement counters"""
		self.unuse_region()
		
		if self._rlist is not None:
			# Actual client count, which doesn't include the reference kept by the manager, nor ours
			# as we are about to be deleted
			num_clients = self._rlist.client_count() - 2
			if num_clients == 0 and len(self._rlist) == 0:
				# Free all resources associated with the mapped file
				self._manager._files.pop(self._rlist.path())
			#END remove regions list from manager
		#END handle regions
		
	def _copy_from(self, rhs):
		"""Copy all data from rhs into this instance, handles usage count"""
		self._manager = rhs._manager
		self._rlist = rhs._rlist
		self._region = rhs._region
		self._ofs = rhs._ofs
		self._size = rhs._size
		
		if self._region is not None:
			self._region.increment_usage_count(1)
		# END handle regions
		
	def __copy__(self):
		"""copy module interface"""
		cpy = type(self)()
		cpy._copy_from(self)
		return cpy
		
	#{ Interface
	def assign(self, rhs):
		"""Assign rhs to this instance. This is required in order to get a real copy.
		Alternativly, you can copy an existing instance using the copy module"""
		self._destroy()
		self._copy_from(rhs)
		
	def use_region(self, offset, size):
		"""Assure we point to a window which allows access to the given offset into the file
		:param offset: absolute offset in bytes into the file
		:param size: amount of bytes to map
		:return: this instance - it should be queried for whether it points to a valid memory region.
			This is not the case if the mapping failed becaues we reached the end of the file
		:note: The size actually mapped may be smaller than the given size. If that is the case,
			either the file has reached its end, or the map was created between two existing regions"""
			
	def unuse_region(self):
		"""Unuse the ucrrent region. Does nothing if we have no current region
		:note: the cursor unuses the region automatically upon destruction. It is recommended
			to unuse the region once you are done reading from it in persistent cursors as it 
			helps to free up resource more quickly"""
		self._region = None
	
	def is_valid(self):
		""":return: True if we have a valid and usable region"""
		return self._region is not None
		
	def is_associated(self):
		""":return: True if we are associated with a specific file already"""
		return self._rlist is not None
		
	def ofs_begin(self):
		""":return: offset to the first byte pointed to by our cursor"""
		return self._region.ofs_begin() + self._ofs
		
	def size(self):
		""":return: amount of bytes we point to"""
		return self._size
		
	def region_ref(self):
		""":return: weak proxy to our mapped region.
		:raise AssertionError: if we have no current region. This is only useful for debugging"""
		if self._region is None:
			raise AssertionError("region not set")
		return proxy(self._region)
		
	def includes_ofs(self, ofs):
		""":return: True if the given absolute offset is contained in the cursors 
			current region
		:note: always False if the cursor does not point to a valid region"""
		if self._region is None:
			return False
		return (self.ofs_begin() <= ofs) and (ofs < self.ofs_end())
		
	def file_size(self):
		""":return: size of the underlying file"""
		return self._rlist.file_size()
		
	def path(self):
		""":return: path of the underlying mapped file"""
		return self._rlist.path()
	
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
	
