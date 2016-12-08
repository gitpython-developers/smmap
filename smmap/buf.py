"""Module with a simple buffer implementation using the memory manager"""
import sys
import logging

__all__ = ["SlidingWindowMapBuffer"]


try:
    bytes
except NameError:
    bytes = str  # @ReservedAssignment


log = logging.getLogger(__name__)


class SlidingWindowMapBuffer(object):

    """A buffer like object which allows direct byte-wise object and slicing into
    memory of a mapped file. The mapping is controlled by the provided cursor.

    The buffer is relative, that is if you map an offset, index 0 will map to the
    first byte at the offset you used during initialization or begin_access

    .. Tip::
        Use it as a context-manager inside a ``with SlidingWindowMapBuffer(...):`` block.

    .. Note::
        Although this type effectively hides the fact that there are mapped windows
        underneath, it can unfortunately not be used in any non-pure python method which
        needs a buffer or string
    """
    __slots__ = (
        '_c',           # our cursor
        '_size',        # our supposed size
        '_entered',     # entry/exit accounting
    )

    def __init__(self, cursor=None, offset=0, size=sys.maxsize, flags=0):
        """Initialize the instance to operate on the given cursor.
        :param cursor: The associated cursor to the file you want to access
            If None, you have call begin_access before using the buffer and provide a cursor
        :param offset: absolute offset in bytes
        :param size: the total size of the mapping. Defaults to the maximum possible size
            From that point on, the __len__ of the buffer will be the given size or the file size.
            If the size is larger than the mappable area, you can only access the actually available
            area, although the length of the buffer is reported to be your given size.
            Hence it is in your own interest to provide a proper size !
        :param flags: Additional flags to be passed to os.open
        :raise ValueError: if the buffer could not achieve a valid state"""
        if not cursor:
            raise ValueError("Cursor cannot be null!")
        self._c = cursor
        self._entered = 0

        if cursor.is_associated() and cursor.use_region(offset, size, flags).is_valid():
            # if given size is too large or default, we computer a proper size
            # If its smaller, we assume the combination between offset and size
            # as chosen by the user is correct and use it !
            # If not, the user is in trouble.
            if size > cursor.file_size():
                size = cursor.file_size() - offset
            # END handle size
            self._size = size
        else:
            raise ValueError("Cursor %s not associated or mapping region failed!" % cursor)

    def __enter__(self):
        assert self._entered >= 0, self._entered
        self._entered += 1
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        assert self._entered >= 0, self._entered
        self._entered -= 1
        if self._entered == 0:
            self.close()

    def __del__(self):
        if self._entered != 0:
            log.warning("Missed %s exit(s) on %s!" % (self._entered, self))
            self.close()

    def _check_if_entered(self):
        if self._entered <= 0:
            raise ValueError('Context-manager %s not entered!' % self)

    def __len__(self):
        return self._size

    def __getitem__(self, i):
        self._check_if_entered()

        if isinstance(i, slice):
            return self.__getslice__(i.start or 0, i.stop or self._size)
        c = self._c
        assert c.is_valid()
        if i < 0:
            i = self._size + i
        if not c.includes_ofs(i):
            c.use_region(i, 1)
        # END handle region usage
        return c.buffer()[i - c.ofs_begin()]

    def __getslice__(self, i, j):
        self._check_if_entered()

        c = self._c
        # fast path, slice fully included - safes a concatenate operation and
        # should be the default
        assert c.is_valid()
        if i < 0:
            i = self._size + i
        if j == sys.maxsize:
            j = self._size
        if j < 0:
            j = self._size + j
        if (c.ofs_begin() <= i) and (j < c.ofs_end()):
            b = c.ofs_begin()
            return c.buffer()[i - b:j - b]
        else:
            l = j - i                 # total length
            ofs = i
            # It's fastest to keep tokens and join later, especially in py3, which was 7 times slower
            # in the previous iteration of this code
            pyvers = sys.version_info[:2]
            if (3, 0) <= pyvers <= (3, 3):
                # Memory view cannot be joined below python 3.4 ...
                out = bytes()
                while l:
                    c.use_region(ofs, l)
                    assert c.is_valid()
                    d = c.buffer()[:l]
                    ofs += len(d)
                    l -= len(d)
                    # This is slower than the join ... but what can we do ...
                    out += d
                    del(d)
                # END while there are bytes to read
                return out
            else:
                md = []
                while l:
                    c.use_region(ofs, l)
                    assert c.is_valid()
                    d = c.buffer()[:l]
                    ofs += len(d)
                    l -= len(d)
                    # Make sure we don't keep references, as c.use_region() might attempt to free resources, but
                    # can't unless we use pure bytes
                    if hasattr(d, 'tobytes'):
                        d = d.tobytes()
                    md.append(d)
                # END while there are bytes to read
                return bytes().join(md)
        # END fast or slow path
    #{ Interface

    def close(self):
        """Call this method once you are done using the instance. It is automatically
        called on destruction, and should be called just in time to allow system
        resources to be freed.

        Once you called close, you must call begin access before reusing this instance!"""
        if self._c:
            self._c.unuse_region()
            self._c = None
            self._size = 0

    def cursor(self):
        """:return: the currently set cursor which provides access to the data"""
        return self._c

    #}END interface
