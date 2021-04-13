#!/usr/bin/env python3

import argparse
import errno
import select
import signal
import socket
import sys
import threading


class Server:
    '''
    Server is the passive side of client-server architecture model. It binds
    to one or more local interface and listens for incoming connection on some
    port.

    Args:
        payload_size (int): Max size of an incoming message. Defaults to 1024.
    '''

    def __init__(self, payload_size = 1024):
        self.payload_size = payload_size

        self.lock = threading.Lock()
        self.threads = []
        self.stopped = True
        self.socket = None

    def start(self, host, port):
        '''
        Starts the server.

        Args:
            host (str): Interfaces address where the server should listen on.
            port (int): Port number where the server should listen on.
        '''

        address = (host, port)
        print(f'starting the server at {address[0]}:{address[1]}...')

        with self.lock:
            if not self.stopped:
                raise Exception('server is already running')

            self.socket = self.create_server(address)

        self.listen_connections()

        self.socket.close()

        with self.lock:
            self.socket = None

    def stop(self):
        '''
        Stops the server.
        '''

        with self.lock:
            print('server has received a signal to stop...')
            self.stopped = True

            if self.socket:
                self.socket.close()

            print(self.threads)

            for t in self.threads:
                print(t)
                t.join()

            self.threads = []

    def create_server(self, address):
        '''
        Creates a socket to accept connection on server side.

        Args:
            address (tuple): the address and port.
        '''

        ss = socket.create_server(address, reuse_port = True)
        ss.setblocking(False) # set the socket as asynchronous
        return ss

    def listen_connections(self):
        '''
        Accepts new connections from remote peers.

        Args:
            socket (obj): Inherited socket object.
        '''

        while True:
            reading_list = []

            try:
                reading_list, _, _ = select.select([self.socket], [], [])
            except IOError as e:
                if e.errno == errno.EBADF: # server has been stopped
                    break

            except Exception as e:
                print(f'an exception occurred while listening for connections: Exception = {e}', file = sys.stderr)
                break

            for r in reading_list:
                peer_connection, peer_address = self.socket.accept()

                thread = threading.Thread(target = self.handle_connection, args = (peer_connection, peer_address))
                thread.start()

                self.threads.append(thread)

    def handle_connection(self, peer_conn, peer_address):
        '''
        Handles the connection from a remote peer, extracts the payload and
        replies with the same content.

        Args:
            peer_conn (obj): Inherited socket object.
            peer_address (tuple): A tuple with the address and port from the remote peer.
        '''

        peer_id = f'{peer_address[0]}:{peer_address[1]}'
        print(f'handling connection from peer {peer_id}...')

        messages_count = 0

        while True:
            try:
                messages_count += 1

                data = peer_conn.recv(self.payload_size)
                if not data:
                    print(f'  > message #{messages_count}: no content received, closing the connection with {peer_id}...')
                    break

                self.request_handler(peer_conn, peer_address, str(data, encoding='utf-8'))

            except IOError as e:
                if e.errno == errno.EDEADLK: # ignoring the "Resource temporarily unavailable" error if no data is available (since the socket is asynchronous)
                   continue

                if e.errno == errno.EBADF: # if the file descriptor is suddenly closed in the "connection_handler" method, we close abort the loop to end up the thread
                    break

            except Exception as e:
                print(f'an exception occurred while handling a connection from peer {peer_id}: Exception = {e}', file = sys.stderr)
                break

        peer_conn.close()

    def request_handler(self, peer_conn, peer_address, data = ''):
        raise NotImplementedError("please implement this method")
