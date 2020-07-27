#!/usr/bin/python
#-*-coding utf-8-*-

#import stander lib
import sys
import socket
import threading
import time
import binascii
import logging

HOST = ''
PORT = 1234
DATA_SIZE=4096

client_list = []

def print_time():
    print(time.strftime("%Y:%m:%d %H:%M:%S", time.localtime()))

def send_other_client(my, data):
    for client in client_list:
        if not client is my:
            client.sendall(data)

def client_thread(conn,addr):
    logging.info('TCP Connected with ' + addr[0] + ':' + str(addr[1]))
    msg_no = 0
    while True:
        try:
            data = conn.recv(DATA_SIZE)
            if len(data) == 0:
            #if data =='':
                break
            msg_no += 1
            logging.info('TCP No(%d):', msg_no)
            logging.info('receive from: %s:%d', addr[0], addr[1])
            logging.info('receive(size): %d', len(data))
            logging.info('receive(data): %s', data)
            reply = data
            if PORT == 6123:
                send_other_client(conn, reply)
                if data.startswith("aplink"):
                    conn.sendall("OK")
            else:
                conn.sendall(reply)
        except socket.error as msg:
            logging.error(msg[1])
            break
    conn.close()
    client_list.remove(conn)
    logging.info('client ' + addr[0] + ':' + str(addr[1]) + ' exit')

class TCPsocket():
    def __init__( self ):
        self.tcpServerSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
        self.tcpServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.tcpServerSocket.bind( (HOST, PORT) )
        except socket.error as msg:
            logging.error('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])

    def listen( self ):
        self.tcpServerSocket.listen(10)
        logging.info('Start TCP server')
        while True:
            # print 'TCP wait for connect'
            conn,addr = self.tcpServerSocket.accept()
            client_list.append(conn)
            #thread.start_new_thread(client_thread, (conn,addr))
            x = threading.Thread(target=client_thread, args=(conn,addr))
            x.setDaemon(True)
            x.start()
            #x.join()
        self.close()

    def close( self ):
        self.tcpServerSocket.close()

    def __del__( self ):
        self.close()

class UDPsocket():
    '''
    usage:
        p = UDPsocket.UDPsocket()
        p.listen()
    '''
    def __init__( self ):
        self.udpServerSocket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.udpServerSocket.bind( (HOST, PORT) )
        self.buffer_size = DATA_SIZE
        self.msg_no = 0

    def receive( self ):
        raw_data, addr = self.udpServerSocket.recvfrom( int(self.buffer_size) )
        self.msg_no += 1
        logging.info('UDP No(%d):', self.msg_no)
        logging.info('receive from: %s:%d', addr[0], addr[1])
        logging.info('receive(size): %d', len(raw_data))
        logging.info('receive(data): %s ', raw_data)
        logging.info('receive(hex data): %s',  binascii.b2a_hex(raw_data))
        reply = raw_data
        return ( reply, addr )

    def send( self, result, addr ):
        self.udpServerSocket.sendto( result, addr )

    def listen( self ):
        logging.info('Start UDP server')
        while True:
            # print 'UDP wait for connect'
            socket_data = self.receive()
            self.send( socket_data[0], socket_data[1] )
        self.close()

    def close( self ):
        self.udpServerSocket.close()

    def __del__( self ):
        self.close()

if __name__ == '__main__':
    LOG_FORMAT="%(asctime)s - %(levelname)s - %(message)s"
    if sys.argv[1] == 'tcp':
        logging.basicConfig(filename='tcp.log', level=logging.INFO, format=LOG_FORMAT)
        p = TCPsocket()
    elif sys.argv[1] == 'udp':
        logging.basicConfig(filename='udp.log', level=logging.INFO, format=LOG_FORMAT)
        p = UDPsocket()
    elif sys.argv[1] == 'aplink':
        logging.basicConfig(filename='aplink.log', level=logging.INFO, format=LOG_FORMAT)
        PORT = 6123
        p = TCPsocket()
    else:
        print ("Usage: %s <tcp|udp|aplink>" % sys.argv[0])
        exit(-1)
    p.listen()
