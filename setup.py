from distutils.core import setup
setup(name='py-lookingglass',
      version='0.56',
      py_modules=['lg'],
      url='https://github.com/andrew-azarov/py-lookingglass',
      author='Andrew Azarov',
      author_email='andrew@azar-a.net',
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

Setup:
------

To run out of the box just clone the repo or install using ``pip install py-lookingglass`` or ``easy_install py-lookingglass``, then:

``# python -m lg -h``

Or you can use it as WSGI callback

``lg.lookingglass(name="Looking Glass", cmds=['command','list'], hosts=[('password','ip',port,'name'), qptd=quaggaport])``

Any additional hacks can be applied before init of class

Check ``help(lg.lookingglass)`` for more info

QUAGGA users:
-------------

Change the integer if applicable (www-dev is 2784)

``# python -m lg -q 2784``

to the port number of
quirk.

Small quirk using inetd and a shell script (you can also listen only on
localhost if running py-lookingglass and quagga on the same system)

inetd.conf

``www-dev stream tcp nowait root /path_to_script/pt.sh pt.sh``

pt.sh::

 #!/bin/sh
 read in
 
 cmd=`echo "${in}" | awk '{print $1}'`
 arg=`echo "${in}" | awk '{print $2}' | tr -cd "[:print:]"`
 if [ "${cmd}" = "ping" ]
 then
   if [ `echo ${arg}| grep -c :` -gt 0 ]
   then
     ping6 -l 4 -c 4 ${arg}
 	else
 		ping -l 4 -c 4 ${arg}
 	fi
 elif [ "${cmd}" = "traceroute" ]
 then
 	if [ `echo ${arg}| grep -c :` -gt 0 ]
 	then
 		traceroute -w 2 ${arg}
 	else
 	  traceroute -w 2 ${arg}
 	fi
 fi
 exit 0

**Firewall as required**"""
      )
