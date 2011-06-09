"""Module with a simple buffer implementation using the memory manager"""
from mman import MemoryCursor

import sys

__all__ = ["MappedMemoryBuffer"]

class MappedMemoryBuffer(object):
	"""A buffer like object which allows direct byte-wise object and slicing into 
	memory of a mapped file. The mapping is controlled by an underlying memory manager.
	
	A buffer, once initialized, stays put on providing access to eactly one path.
	A custom interface allows you to change paths mid way, and to optimize 
	the resource usage.
	
	Please note that this type is only fully usable if you configure it with the 
	MappedMemoryManager to use.
	
	The buffer is relative, that is if you map an offset, index 0 will map to the 
	first byte at your given offset."""
	__slots__ = '_c'		# our cursor
	
	#{ Configuration
	# A subclass must provide an instance of a (usually global) MappedMemoryManager
	manager = None
	#}END configuration
	
	def __init__(self, path = None, offset = 0, size = sys.maxint, flags = 0):
		"""Initalize the instance to operate on the given path if given.
		:param path: if not None, the path to the file you want to access
			If None, you have call begin_access before using the buffer 
		:param offset: absolute offset in bytes
		:param size: the total size of the mapping. Defaults to the maximum possible size
		:param flags: Additional flags to be passed to os.open
		:raise ValueError: if the buffer could not achieve a valid state"""
		self._c = MemoryCursor(self.manager)
		assert self.manager is not None, "Require the cls.manager variable to be set in subclass"
		if path and not self.begin_access(path, offset, size, flags):
			raise ValueError("Failed to allocate the buffer - probably the given offset is out of bounds")
		# END handle offset

	def __del__(self):
		self.end_access()
		
	def __getitem__(self, i):
		c = self._c
		if not c.includes_ofs(i):
			c.use_region(i, 1)
		# END handle region usage
		assert c.is_valid()		# TODO: remove for performance
		return c.buffer()[i]
	
	def __getslice__(self, i, j):
		c = self._c
		# fast path, slice fully included - safes a concatenate operation and 
		# should be the default
		if c.ofs_begin() >= i and j < c.ofs_end():
			return c.buffer()[i:j]
		raise NotImplementedError()
	#{ Interface
	
	def begin_access(self, path = None, offset = 0, size = sys.maxint, flags = 0):
		"""Call this before the first use of this instance. The method was already
		called by the constructor in case sufficient information was provided.
		
		For more information no the parameters, see the __init__ method
		:param path: if path is empty or None the existing path will be used if possible. 
		:return: True if the buffer can be used"""
		if path and (not self._c.is_associated() or self._c.path() != path):
			self._c = self.manager.make_cursor(path)
		#END get associated cursor
		
		# reuse existing cursors if possible
		if self._c.is_associated():
			return self._c.use_region(offset, size, flags).is_valid()
		return False
		
	def end_access(self):
		"""Call this method once you are done using the instance. It is automatically 
		called on destruction, and should be called just in time to allow system
		resources to be freed.
		
		Once you called end_access, you must call begin access before reusing this instance!"""
		self._c.unuse_region()
		
	def cursor(self):
		""":return: the currently set cursor which provides access to the data"""
		return self._c
		
	#}END interface


