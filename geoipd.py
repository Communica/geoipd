#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
#    Communicas Geo-ip loookup daemon
#
#
#
# @author: technocake
# @changelog:
#    when    who            what
#    210812    technocake    made alpha version, capable of lookups.
#
##########################################################################################
import iplookup, sys, socket, random, time, threading, math, copy, os, pdb, cPickle, re, json
from prompt import *

try:
    import SocketServer
except:
    import socketserver as SocketServer


# Loading db to memory
iplookup.parseIpDB()

#CONFIGZ
#http://docs.python.org/library/socketserver.html

DEBUG = False
HOST, PORT = 'localhost', 80

#
#
#    Communica geo-ip lookup
#
#

HTTP_HEADERS = """HTTP/1.1 200
Cache-Control: no-cache;
Content-Type: application/json; charset=utf-8;

"""


class NerdHandler(SocketServer.StreamRequestHandler):
    """
    This class is invoked when dealing with a request.

    Each client connecting will get a separate thread running handling them. (this class)
    It is here the communication happens between the server and client.

    """
    def handle(self):
        ip = self.client_address[0]
        print

        data = self.ReadSomething()
        self.SaySomething(HTTP_HEADERS)
        try:
            ipv4 = re.search(r'ip=([^\ |&]+)[&\ ]', data).group(1)
            querytype = 'CTR_ONLY' if 'type=CTR_ONLY' in data else 'NORMAL'
            response = server.lookup(ipv4, type=querytype)

            print "request from %s, lookup: %s --> %s" % (ip, ipv4, response)
            self.SaySomething(json.dumps(response))
        except:
            print "error..."
            self.SaySomething("{}")

    def SaySomething(self, something):
        """
        Method for writing to the socket. Python 3 compability issue handling :)
        Str is no longar  string or something
        """
        self.wfile.write(str(something).encode('UTF-8') + '\n')

    def ReadSomething(self):
        """
        Method to read from the socket.  The comp...  well, it decodes utf-8.
        """
        return self.rfile.readline(2048).decode('UTF-8').strip()


class ThreadedNetChallonged(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True  # SO_REUSEADDR so we can reboot the server immidiently

    def lookup(self, ip, type='NORMAL'):
        """
            Threadsafe lookup method
        """
        if DEBUG:
            pdb.set_trace()
        try:
            with self.lookupLock:
                if type == 'NORMAL':
                    return iplookup.lookup(ip)
                else:
                    return iplookup.lookup_ctr(ip)
        except Exception as e:
            print ("Failed to lookup... %s \n %s " % (ip, e))

    #To make the operations on add / get users / challenges atomic.
    lookupLock = threading.RLock()


# Below are the control and running of the server.
# It is an interactive prompt that controls it.

if __name__ == "__main__":
    server = ThreadedNetChallonged((HOST, PORT), NerdHandler)

    def shutUp():
        print ("Shuting down.. eh, up")
        server.shutdown()
        exit()

    print ("The Daemon is alive")
    serveraddr, serverport = server.server_address
    try:
        serverThread = threading.Thread(target=server.serve_forever)
        serverThread.setDaemon(True)
        serverThread.start()
        while 1:
            cmd = prompt("Communica->Geoipd>> ")
            if "quit" in cmd:
                shutUp()

            if "help" in cmd:
                args = cmd.split(" ")

                #Lists all cmds
                if len(args) == 1:
                    for k in ["help", "quit", "lookup"]:
                        print (k)
                    print ("Usage help [<command>]  \n if no command given, it lists all commands")
                    continue

                if "lookup" in args[1]:
                    print("""
                        Usage: lookup <ipv4>

                            Looks up a ipv4 address to its country
                        """
                        )

            elif "lookup" in cmd:
                ip = cmd.split(' ')[1]
                print server.lookup(ip)

    except KeyboardInterrupt:
        print ("Shuting down, erh up... ")
    finally:
        server.shutdown()
