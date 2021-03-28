#!/usr/bin/env python3

import argparse
import signal
import socket
import sys
import threading


class Server:
    '''
    Server is the passive side of client-server architecture model. It binds
    to one or more local interface and listens for incoming connection on some
    port.

    For learning purporses, all incoming messages are echoed to its related peer.

    Args:
        threads (int): Max number of peers which are able to send and receive messages simultaneosly. Defaults to 2.
        payload_size (int): Max size of an incoming message. Defaults to 1024.
    '''

    def __init__(self, threads = 2, payload_size = 1024):
        self.payload_size = payload_size
        self.threads = threads

        self.lock = threading.Lock()
        self.socket = None
        self.stopped = True

    def start(self, host, port):
        '''
        Starts the server.

        Args:
            host (str): Interfaces address where the server should listen on.
            port (int): Port number where the server should listen on.
        '''

        address = (host, port)
        print(f'starting the server at {address[0]}:{address[1]}...')

        with socket.create_server(address, reuse_port = True) as ss:
            with self.lock:
                self.socket = ss
                self.stopped = False

            threads = []
            for tid in range(self.threads):
                t = threading.Thread(target=self.listen_connections, args=(tid, ss))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

        with self.lock:
            self.socket = None

    def stop(self):
        '''
        Stops the server.
        '''

        print('server has received a signal to stop...')
        with self.lock:
            if self.socket:
                self.socket.close()
                self.stopped = True

    def listen_connections(self, worker_id, socket):
        '''
        Accepts new connections of remote peers.

        Args:
            worker_id (int): Identifier of the worker (thread).
            socket (obj): Inherited socket object.
        '''

        while True:
            try:
                peer_connection, peer_address = socket.accept()
                with peer_connection:
                    self.handle_connection(worker_id, peer_connection, peer_address)

            except Exception as e:
                print(f'worker #{worker_id}: an exception occurred while listening for connections: Exception = {e}', file = sys.stderr)
                return

    def handle_connection(self, worker_id, peer_conn, peer_address):
        '''
        Handles the connection from a remote peer, extracts the payload and
        replies with the same content.

        Args:
            worker_id (int): Identifier of the worker (thread).
            peer_conn (obj): Inherited socket object.
            peer_address (tuple): A tuple with the address and port from the remote peer.
        '''

        peer_id = f'{peer_address[0]}:{peer_address[1]}'
        print(f'worker #{worker_id}: handling connection from peer {peer_id}...')

        messages_count = 0

        while True:
            with self.lock:
                if self.stopped:
                    return

            try:
                messages_count += 1

                data = peer_conn.recv(self.payload_size)
                if not data:
                    print(f'  > worker #{worker_id}: message #{messages_count}: no content received, closing the connection with {peer_id}...')
                    return

                print(f'  > worker #{worker_id}: message #{messages_count}: echoing {data} to {peer_id}')
                peer_conn.sendall(data)

            except Exception as e:
                print(f'worker #{worker_id}: an exception occurred while handling a connection from peer {peer_id}: Exception = {e}', file = sys.stderr)
                return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'starts server which echoes incoming messages from remote clients')

    parser.add_argument('--host', '-H', type = str, default = 'localhost', help = 'local address (default localhost)')
    parser.add_argument('--port', '-p', type = int, default = 8080, help = 'local port (default 8080)')
    parser.add_argument('--threads', '-t', type = int, default = 2, help = 'max number of simultaneous clients (default 2)')

    args = parser.parse_args()

    server = Server(threads = args.threads)

    for ss in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(ss, lambda received_signal, frame: server.stop())

    server.start(host = args.host, port = args.port)