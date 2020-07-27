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
PORT = 6122
DATA_SIZE=4096

client_list = []

def print_time():
    print(time.strftime("%Y:%m:%d %H:%M:%S", time.localtime()))

def send_other_client(my, data):
    for client in client_list:
        if not client is my:
            client.sendall(data)

def handle_cmd(data):
    if data[0] == '\x7E':
        if data[5] == '\x10':
            logging.info('Reg CMD')
            return '\x7E\x00\x08\x00\x00\x11\x01\x68'
        elif data[5] == '\x20':
            logging.info('Heart CMD')
            return '\x7E\x00\x07\x00\x00\x21\x5A'
        elif data[5] == '\x30':
            logging.info('Now CMD')
            return '\x7E\x00\x07\x00\x00\x31\x4A'
        elif data[5] == '\x32':
            logging.info('Thread CMD')
            return '\x7E\x00\x07\x00\x00\x33\x48'
    return ''

def client_thread(conn,addr):
    logging.info('TCP Connected with ' + addr[0] + ':' + str(addr[1]))
    msg_no = 0
    while True:
        try:
            data = conn.recv(DATA_SIZE)
            #if data =='':
            if len(data) == 0:
                break
            msg_no += 1
            logging.info('TCP No(%d):', msg_no)
            logging.info('receive from: %s:%d', addr[0], addr[1])
            logging.info('receive(size): %d', len(data))
            logging.info('receive(data): %s', data)
            logging.info('receive(hex data): %s',  binascii.b2a_hex(data))
            reply = handle_cmd(data)
            if reply:
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
        self.close()

    def close( self ):
        self.tcpServerSocket.close()

    def __del__( self ):
        self.close()


if __name__ == '__main__':
    LOG_FORMAT="%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(filename='yuandian.log', level=logging.INFO, format=LOG_FORMAT)
    p = TCPsocket()
    p.listen()
