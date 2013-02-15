#!/usr/bin/env python
# coding=utf8
"""
Copyright (c) 2012 Azar-A Kft.
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import telnetlib,os,socket,cgi
from wsgiref.simple_server import make_server

# Thanks tzot @ stackoverflow.com

def is_ipv4(address):
    try:
        addr= socket.inet_pton(socket.AF_INET, address)
    except AttributeError: # no inet_pton here, sorry
        try:
            addr= socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error: # not a valid address
        return False
    return True

def is_ipv6(address):
    try:
        addr= socket.inet_pton(socket.AF_INET6, address)
    except socket.error: # not a valid address
        return False
    return True

# end Thanks tzot @ stackoverflow.com


commands = ['sh ip bgp summary',
'sh ip bgp neighbor %ARG% advertised',
'ping %ARG%',
'traceroute %ARG%']

# You own quagga ping and traceroute daemon for telnet connection

quagga_ping_traceroute_daemon = 2784

hosts = [
("password",'ip',port_number,"fancy_name")
]

def issuecommand(host,port,password,command,arg):
    quagga = (port == 2605)
    if (quagga and command.startswith(("ping","traceroute"))): port = quagga_ping_traceroute_daemon # replace the port for quagga users
    tn = telnetlib.Telnet(host, port)
    if password and not (quagga and ("ping" in command or "traceroute" in command)): # password for real router telnet connections only
        tn.read_until("Password: ")
        tn.write(password+"\n")
    if "%ARG%" in command: # if argument in command
        if is_ipv4(arg) or is_ipv6(arg): # to disable ipv6 write return False in is_ipv6 function beginning
            command = command.replace("%ARG%",arg)
        else:
            try:
                socket.setdefaulttimeout(5)
                arg = socket.gethostbyname(arg)
                command = command.replace("%ARG%",arg)
            except:
                return "Invalid Argument"
    tn.write(str(command)+"\n") # sanitize arguments!?
    if not (quagga and ("ping" in command or "traceroute" in command)): # ping traceroute passover daemon to close connection by itself.
        try:
            tn.write("exit\n")
        except:
            pass
    return str(os.linesep.join([line for line in str(tn.read_all()).splitlines() if command not in line and "exit" not in line])).strip()

def template(*args):
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

def callback(env,respond):
    header = [('Server', 'py-LookingGlass'),('Content-Type', 'text/html')]
    data = ['Looking Glass','<h1>Not Found</h1>']
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
                output = issuecommand(hosts[int(post.getfirst('host'))][1],
                    hosts[int(post.getfirst('host'))][2],
                    hosts[int(post.getfirst('host'))][0],
                    commands[int(post.getfirst('command'))],
                    post.getfirst('args'))
        data = ['Looking Glass',"""
        <section>
        <header>Looking Glass</header><br>
        <form method="POST">
            <label>Router:&nbsp;</label><select name="host">"""+str("".join(["".join(['<option value="',str(k),'">',v[3],'</option>']) for k,v in enumerate(hosts)]))+"""</select>&nbsp;&nbsp;&nbsp;
            <label>Type:&nbsp;</label><select name="command">"""+str("".join(["".join(['<option value="',str(k),'">',v,'</option>']) for k,v in enumerate(commands)]))+"""</select>&nbsp;&nbsp;&nbsp;
            <label>Argument:&nbsp;</label><input type="text" name="args"/><br>
            <label>Output:&nbsp;</label><br><textarea style="width:100%;height:400px">"""+output+"""</textarea><br>
            <button type="submit" name="submit" value="Go">Go</button>
        </form>
        </section>"""]       
    response = template(*data)
    header.append(('Content-Length', str(len(response))))
    respond(status,header)
    return [response]

if __name__ == '__main__':
    httpd = make_server('localhost', 8000, callback)
    httpd.serve_forever()
