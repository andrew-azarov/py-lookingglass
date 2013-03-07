py-lookingglass
===============

Python looking glass implementation with wsgi

Requires:
---------
Python 2.6+

Standard python modules:
* telnetlib
* os
* socket
* cgi
* wsgi_ref
* random
* traceback
* argparse

Setup:
------
To run out of the box just clone the repo or install using `pip install py-lookingglass` or `easy_install py_lookingglass`, then:
```console
# python -m lg -h
```
Or you can use it as WSGI callback
```python
lg.lookingglass(name="Looking Glass", cmds=['command','list'], hosts=[('password','ip',port,'name'), qptd=quaggaport])
```
Any additional hacks can be applied before init of class

Check `help(lg.lookingglass)` for more info

QUAGGA users:
-------------
Change the integer if applicable (www-dev is 2784)

```console
# python -m lg -q 2784
```
to the port number of quirk.

Small quirk using inetd and a shell script (you can also listen only on localhost if running py-lookingglass and quagga on the same system)

inetd.conf
```sh
www-dev stream tcp nowait root /path_to_script/pt.sh pt.sh
```

pt.sh
```sh
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
```

__Firewall as required__
