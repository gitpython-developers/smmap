###########
Motivation
###########
When reading from many possibly large files in a fashion similar to random access, it is usually the fastest and most efficient to use memory maps.

Although memory maps have many advantages, they represent a very limited system resource as every map uses one file descriptor, whose amount is limited per process. On 32 bit systems, the amount of memory you can have mapped at a time is naturally limited to theoretical 4GB of memory, which may not be enough for some applications.

########
Overview
########

Smmap wraps an interface around mmap and tracks the mapped files as well as the amount of clients who use it. If the system runs out of resources, or if a memory limit is reached, it will automatically unload unused maps to allow continued operation.

To allow processing large files even on 32 bit systems, it allows only portions of the file to be mapped. Once the user reads beyond the mapped region, smmap will automatically map the next required region, unloading unused regions using a LRU algorithm.

The interface also works around the missing offset parameter in python implementations up to python 2.5.

Although the library can be used most efficiently with its native interface, a Buffer implementation is provided to hide these details behind a simple string-like interface.

For performance critical 64 bit applications, a simplified version of memory mapping is provided which always maps the whole file, but still provides the benefit of unloading unused mappings on demand.

#############
Prerequisites
#############
* Python 2.7 or 3.4+
* OSX, Windows or Linux

The package was tested on all of the previously mentioned configurations.

###########
Limitations
###########
* The memory access is read-only by design.

################
Installing smmap
################
Its easiest to install smmap using the *pip*  program::
    
    $ pip install smmap
    
As the command will install smmap in your respective python distribution, you will most likely need root permissions to authorize the required changes.

If you have downloaded the source archive, the package can be installed by running the ``setup.py`` script::
    
    $ python setup.py install

It is advised to have a look at the :ref:`Usage Guide <tutorial-label>` for a brief introduction on the different database implementations.

##################
Homepage and Links
##################
The project is home on github at `https://github.com/gitpython-developers/smmap <https://github.com/gitpython-developers/smmap>`_.

The latest source can be cloned from github as well:

 * git://github.com/gitpython-developers/smmap.git
 
 
For support, please use the git-python mailing list:

 * http://groups.google.com/group/git-python
 

Issues can be filed on github:

 * https://github.com/gitpython-developers/smmap/issues
 
###################
License Information
###################
*smmap* is licensed under the New BSD License.

.. _pip: http://www.pip-installer.org/en/latest/
