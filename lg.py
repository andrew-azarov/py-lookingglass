#!/usr/bin/env python
# coding=utf8
"""
Copyright (c) 2012 Azar-A Kft.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import telnetlib
import os
import socket
import cgi
from wsgiref.simple_server import make_server

class lookingglass(object):
    """lookingglass object
    
    Keyword arguments:
    name    -- Header name for pages (default not set)
    cmds    -- Commands list, use %ARG% for substition of IP or hostname
                argument (default not set)
    hosts   -- Host list of tuples with password, host address, port number and
                name for display (default not set)
    qptd    -- Quagga ping and traceroute daemon port for telnet connection
                (default not set)
                
    ipv4_disable    -- Disable ipv4 resolving and check of arguments
                        (default False)
    ipv6_disable    -- Disable ipv6 resolving and check of arguments
                        (default False)
    resolve         -- Resolve hostnames (default True)
    """
    name = None
    cmds = None
    hosts = None
    qptd = None
    ipv4_disable = False
    ipv6_disable = False
    resolve = True
    
    def __init__(_,**kwargs):
        for i in ['name','cmds','hosts','qptd']:
            if not _.__dict__.has_key(i) or not _.__dict__[i]:
                setattr(_,i,kwargs[i])
            assert _.__dict__[i], "%s is not set" % i
        assert isinstance(_.name,(str,unicode)), "%r is not string or unicode" % _.name
        assert isinstance(_.cmds,list), "%r is not list" % _.cmds
        for d in _.cmds:
            assert isinstance(d,(str,unicode)), "%r is not string or unicode" % d
        assert isinstance(_.hosts,list), "%r is not list" % _.hosts
        for d in _.hosts:
            assert isinstance(d,tuple), "%r is not tuple" % d
            assert len(d) == 4, "%r length is not 4" % d
            assert isinstance(d[0],(str,unicode)), "%r is not string or unicode" % d[0]
            assert isinstance(d[1],str), "%r is not string" % d[1]
            assert isinstance(d[2],int), "%r is not integer" % d[2]
            assert isinstance(d[3],(str,unicode)), "%r is not string or unicode" % d[3]
        assert isinstance(_.qptd,int), "%r is not integer" % _.qptd
        
    def __is_ipv4(_,address):
        # Thanks tzot @ stackoverflow.com
        if _.ipv4_disable: return False
        try:
            addr = socket.inet_pton(socket.AF_INET, address)
        except AttributeError: # no inet_pton here, sorry
            try:
                addr = socket.inet_aton(address)
            except socket.error:
                return False
            return address.count('.') == 3
        except socket.error: # not a valid address
            return False
        return True

    def __is_ipv6(_,address):
        # Thanks tzot @ stackoverflow.com
        if _.ipv6_disable: return False
        try:
            addr = socket.inet_pton(socket.AF_INET6, address)
        except socket.error: # not a valid address
            return False
        return True

    def __issuecommand(_, host, port, password, command, arg):
        quagga = (port == 2605)
        if (quagga and command.startswith(("ping","traceroute"))):
            port = _.qptd # replace the port for quagga
        tn = telnetlib.Telnet(host, port)
        if password and not (quagga and
                                ("ping" in command or "traceroute" in command)):
            tn.read_until("Password: ",5) # 5 seconds timeout
            tn.write(password+"\n")
        if "%ARG%" in command:
            if _.__is_ipv4(arg) or _.__is_ipv6(arg):
                command = command.replace("%ARG%",arg)
            elif _.resolve: # Hostname support
                try:
                    socket.setdefaulttimeout(5)
                    arg = socket.gethostbyname(arg)
                    command = command.replace("%ARG%",arg)
                except:
                    raise ValueError
            else:
                raise ArgumentError
        tn.write(str(command)+"\n") # sanitize arguments!?
        if not (quagga and ("ping" in command or "traceroute" in command)):
            try:
                tn.write("exit\n")
            except:
                pass
        read_data = str(tn.read_all()).splitlines()
        pre_return = []
        for line in read_data:
            if command not in line and 'exit' not in line:
                pre_return.append(line)
        return str(os.linesep.join(pre_return)).strip()

    def template(_,*args):
        assert len(args) == 2, "%r length is not 2" % args
        return """
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="utf-8">
                    <title>{}</title>
                    <meta name="description" content="">
                    <meta name="author" content="">
                </head>
                <body>
                    {}
                </body>
            </html>
            """.format(*args)

    def __call__(_,env,respond):
        header = [('Server', 'py-LookingGlass'),('Content-Type', 'text/html')]
        data = [_.name,'<h1>Not Found</h1>']
        status = '404 Not found'
        if env['PATH_INFO'] == "/":
            status = '200 OK'
            output = ""
            if env['REQUEST_METHOD'] == "POST":
                post_env = env.copy()
                post_env['QUERY_STRING'] = ''
                post = cgi.FieldStorage(
                    fp=env['wsgi.input'],
                    environ=post_env,
                    keep_blank_values=True
                )
                if "host" in post and "command" in post and "args" in post:
                    try:
                        output = _.__issuecommand(
                                    _.hosts[int(post.getfirst('host'))][1],
                                    _.hosts[int(post.getfirst('host'))][2],
                                    _.hosts[int(post.getfirst('host'))][0],
                                    _.cmds[int(post.getfirst('command'))],
                                    post.getfirst('args'))
                    except ValueError:
                        output = "Invalid Argument"
                    except ArgumentError:
                        output = "Arguments are disabled"
            hosts = "".join(["".join(['<option value="',
                                                str(k),
                                                '">',
                                                v[3],
                                                '</option>'])
                                    for k,v in enumerate(_.hosts)])
            commands = "".join(["".join(['<option value="',
                                                str(k),
                                                '">',
                                                v,
                                                '</option>'])
                                    for k,v in enumerate(_.cmds)])
            data = [_.name,"""
            <section>
            <header>Looking Glass</header><br>
            <form method="POST">
                <label>Router:&nbsp;</label><select name="host">"""
                +hosts+"""</select>
                <label>Type:&nbsp;</label><select name="command">"""
                +commands+"""</select>
                <label>Argument:&nbsp;</label><input type="text" name="args"/><br>
                <label>Output:&nbsp;</label><br><textarea style="width:100%;height:400px">"""
                +output+"""</textarea><br>
                <button type="submit" name="submit" value="Go">Go</button>
            </form>
            </section>"""]
        response = _.template(*data)
        header.append(('Content-Length', str(len(response))))
        respond(status,header)
        return [response]

if __name__ == '__main__':
    import argparse
    def tuples(s):
        try:
            password, ip, port, name = map(unicode, s.split(','))
            return unicode(password[1:-1]), str(ip), int(port), unicode(name[1:-1])
        except:
            raise argparse.ArgumentTypeError("""Hosts must be 'password',ip,port,'name'
password, ip and name == string or unicode and port == int""")
    parser = argparse.ArgumentParser()
    parser.add_argument("-n",
            "--name",
            dest='name',
            type=str,
            default='Looking Glass',
            help="Header name for pages",
            required=False)
    parser.add_argument("-c",
            "--commands",
            dest='commands',
            type=tuples,
            default=[],
            nargs='*',
            action="append",
            help="Commands list, use %ARG% for substition of IP or hostname argument",
            required=False)
    parser.add_argument("-H",
            "--hosts",
            dest='hosts',
            type=tuples,
            default=[],
            nargs='*',
            action="append",
            help="Host list of tuples with password, host address, port number and name for display",
            required=False)
    parser.add_argument("-q",
            "--qptd",
            type=int,
            default=2784,
            help="Quagga ping and traceroute daemon port for telnet connection",
            required=False)
    a = parser.parse_args()
    if a.commands:
        commands = a.commands
    else:
        commands = ['sh ip bgp summary',
            'sh ip bgp neighbor %ARG% advertised',
            'ping %ARG%',
            'traceroute %ARG%']
    if a.hosts:
        hosts = a.hosts
    else:
        hosts = [("password1","192.168.0.1",23,"Cisco"),
        ("password2","192.168.1.1",2605,"Quagga"),
        ("password3","192.168.2.1",23,"Juniper")]
    httpd = make_server('localhost', 8000, lookingglass(name=a.name,cmds=commands,hosts=hosts,qptd=a.qptd))
    httpd.serve_forever()
