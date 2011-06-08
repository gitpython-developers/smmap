####################
Sliding MMap (smmap)
####################
A straight forward implementation of a slidinging memory map.
The idea is that every access to a file goes through a memory map manager, which will on demand map a region of a file and provide a string-like object for reading. 

When reading from it, you will have to check whether you are still within your window boundary, and possibly obtain a new window as required.

The great benefit of this system is that you can use it to map files of any size even on 32 bit systems. Additionally it will be able to close unused windows right away to return system resources. If there are multiple clients for the same file and location, the same window will be reused as well.

As there is a global management facility, you are also able to forcibly free all open handles which is handy on windows, which would otherwise prevent the deletion of the involved files.

For convenience, a stream class is provided which hides the usage of the memory manager behind a simple stream interface.

************
LIMITATIONS
************
* The access is readonly by design.
* In python below 2.6, memory maps will be created in compatability mode which works, but creates inefficient memory maps as they always start at offset 0.

************
REQUIREMENTS
************
* runs Python 2.4 or higher, but needs Python 2.6 or higher to run properly as it needs the offset parameter of the mmap.mmap function.

*******
Install
*******
TODO

******
Source
******
The source is available at git://github.com/Byron/smmap.git and can be cloned using::
    
    git clone git://github.com/Byron/smmap.git

************
MAILING LIST
************
http://groups.google.com/group/git-python

*************
ISSUE TRACKER
*************
https://github.com/Byron/smmap/issues

*******
LICENSE
*******
New BSD License
