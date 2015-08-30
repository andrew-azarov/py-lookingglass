from distutils.core import setup
setup(name='py-lookingglass',
      version='0.59',
      py_modules=['lg'],
      url='https://github.com/andrew-azarov/py-lookingglass',
      author='Andrew Azarov',
      author_email='andrew@serverastra.com',
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Intended Audience :: Telecommunications Industry',
                   'Intended Audience :: System Administrators',
                   'Intended Audience :: Information Technology',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: POSIX',
                   'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
                   'Topic :: System :: Networking',
                   'Topic :: System :: Systems Administration'],
      description='Python looking glass implementation with wsgi',
      long_description="""py-lookingglass
===============

Python looking glass implementation with wsgi

Requires:
---------

Python 2.6+

Standard python modules:

- telnetlib
- os
- socket
- cgi
- wsgi\_ref
- traceback
- random
- argparse
- paramiko

Setup:
------

To run out of the box just clone the repo or install using ``pip install py-lookingglass`` or ``easy_install py-lookingglass``, then:

``# python -m lg -h``

Or you can use it as WSGI callback

``lg.lookingglass(name="Looking Glass", cmds=['command','list'], hosts=[('password','ip',port,'name'), qptd=quaggaport])``

Any additional hacks can be applied before init of class

Check ``help(lg.lookingglass)`` for more info
"""
      )
