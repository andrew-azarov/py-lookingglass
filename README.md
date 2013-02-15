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

Setup:
------
To run out of the box just clone the repo and edit the configuration:
```python
hosts = [
("password",'ip',port_number,"fancy_name")
]
```
Where fancy_name is the name in the select box (display), other options are self-described.

QUAGGA users:
-------------
Change the integer if applicable (www-dev is 2784)

```python
quagga_ping_traceroute_daemon = 2784
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
