#########
Changelog
#########

2.1.0
======

- **BREAKING API:** retrofit ``git.util.mman`` as context-manager,
  to release memory-mapped regions held.

  The *mmap-manager(s)* are re-entrant, but not thread-safe **context-manager(s)**,
  to be used within a ``with ...:`` block, ensuring any left-overs cursors are cleaned up.
  If not entered, :meth:`StaticWindowMapManager.make_cursor()` and/or
  :meth:`WindowCursor.use_region()` will scream.

  Get them from ``smmap.managed_mmaps()``.

- FIX ``memoryview`` leak in Windows; now all *gitdb* TCs now pass without explicit release!

- Simplify :class:`SlidingWindowMapBuffer` as create/close context-manager
  (no ``begin_access()``, or ``end_access()``).


v0.9.0
========
- Fixed issue with resources never being freed as mmaps were never closed.
- Client counting is now done manually, instead of relying on pyton's reference count


v0.8.5
========
- Fixed Python 3.0-3.3 regression, which also causes smmap to become about 3 times slower depending on the code path. It's related to this bug (http://bugs.python.org/issue15958), which was fixed in python 3.4


v0.8.4
========
- Fixed Python 3 performance regression


v0.8.3
========
- Cleaned up code and assured it works sufficiently well with python 3


v0.8.1
========
- A single bugfix


v0.8.0
========

- Initial Release
