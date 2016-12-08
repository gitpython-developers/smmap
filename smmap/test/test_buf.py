from __future__ import print_function

from .lib import TestBase, FileCreator

from smmap.mman import (
    SlidingWindowMapManager,
    StaticWindowMapManager
)
from smmap.buf import SlidingWindowMapBuffer

from random import randint
from time import time
import sys
import os


man_optimal = SlidingWindowMapManager()
man_worst_case = SlidingWindowMapManager(
    window_size=TestBase.k_window_test_size // 100,
    max_memory_size=TestBase.k_window_test_size // 3,
    max_open_handles=15)
static_man = StaticWindowMapManager()


class TestBuf(TestBase):

    def test_basics(self):
        # invalid paths fail upon construction
        with FileCreator(self.k_window_test_size, "buffer_test") as fc:
            with man_optimal:
                with man_optimal.make_cursor(fc.path) as c:
                    self.assertRaises(ValueError, SlidingWindowMapBuffer, type(c)())   # invalid cursor
                    self.assertRaises(ValueError, SlidingWindowMapBuffer, c, fc.size)  # offset too large

                    offset = 100
                    with SlidingWindowMapBuffer(c, offset) as buf:
                        assert buf.cursor()
                        assert buf.cursor().is_valid()
                        self.assertEqual(len(buf), fc.size - offset)

                    with SlidingWindowMapBuffer(c, fc.size - offset) as buf:
                        assert buf.cursor()
                        assert buf.cursor().is_valid()
                        self.assertEqual(len(buf), offset)

                    with SlidingWindowMapBuffer(c) as buf:
                        assert buf.cursor()
                        assert buf.cursor().is_valid()
                        self.assertEqual(len(buf), fc.size)

                        # simple access
                        with open(fc.path, 'rb') as fp:
                            data = fp.read()
                        self.assertEqual(data[offset], buf[0])
                        self.assertEqual(data[offset:offset * 2], buf[0:offset])

                        # negative indices, partial slices
                        self.assertEqual(buf[-1], buf[len(buf) - 1])
                        self.assertEqual(buf[-10:], buf[len(buf) - 10:len(buf)])
                    # end access makes its cursor invalid
                    assert not buf.cursor()
                    assert not c.is_valid()
                    assert c.is_associated()         # but it remains associated

                self.assertEqual(man_optimal.num_file_handles(), 1)

    def test_performance(self):
        # PERFORMANCE
        # blast away with random access and a full mapping - we don't want to
        # exaggerate the manager's overhead, but measure the buffer overhead
        # We do it once with an optimal setting, and with a worse manager which
        # will produce small mappings only !
        with FileCreator(self.k_window_test_size, "buffer_test") as fc:
            with open(fc.path, 'rb') as fp:
                data = fp.read()

            max_num_accesses = 100
            fd = os.open(fc.path, os.O_RDONLY)
            try:
                for item in (fc.path, fd):
                    for manager, man_id in ((man_optimal, 'optimal'),
                                            (man_worst_case, 'worst case'),
                                            (static_man, 'static optimal')):
                        with manager:
                            for access_mode in range(2):    # single, multi
                                with SlidingWindowMapBuffer(manager.make_cursor(item)) as buf:
                                    self.assertEqual(manager.num_file_handles(), 1)
                                    num_accesses_left = max_num_accesses
                                    num_bytes = 0
                                    fsize = fc.size

                                    st = time()
                                    while num_accesses_left:
                                        num_accesses_left -= 1
                                        if access_mode:  # multi
                                            ofs_start = randint(0, fsize)
                                            ofs_end = randint(ofs_start, fsize)
                                            d = buf[ofs_start:ofs_end]
                                            self.assertEqual(len(d), ofs_end - ofs_start)
                                            self.assertEqual(d, data[ofs_start:ofs_end])
                                            num_bytes += len(d)
                                            del d
                                        else:
                                            pos = randint(0, fsize)
                                            self.assertEqual(buf[pos], data[pos])
                                            num_bytes += 1
                                        # END handle mode
                                    # END handle num accesses
                                assert manager.num_file_handles()
                                assert manager.collect()
                                self.assertEqual(manager.num_file_handles(), 0)
                                elapsed = max(time() - st, 0.001)  # prevent zero division errors on windows
                                mb = float(1000 * 1000)
                                mode_str = (access_mode and "slice") or "single byte"
                                print("%s: Made %i random %s accesses to buffer created from %s "
                                      "reading a total of %f mb in %f s (%f mb/s)"
                                      % (man_id, max_num_accesses, mode_str, type(item),
                                         num_bytes / mb, elapsed, (num_bytes / mb) / elapsed),
                                      file=sys.stderr)
            finally:
                os.close(fd)
