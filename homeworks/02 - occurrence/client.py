#!/usr/bin/env python3

import argparse
import socket
import sys


class Client:
    '''
    Client is the active side of client/server architeture model. It connects
    to the remote server, sends the message from standard input and writes
    the received reply on the standard output.

    Args:
        payload_size (int): Max size of an incoming message. Defaults to 1024.
    '''

    def __init__(self, payload_size = 1024):
        self.payload_size = payload_size

    def connect_on_server(self, address, port, input_file = sys.stdin, output_file = sys.stdout):
        '''
        Connects to the remote server, sends the messages from STDIN to there
        and writes the replies on STDOUT.

        Args:
            address (str): remote server address.
            port (int): remote server port.
        '''

        with socket.socket() as ss:
            print(f'connecting to remote server at {address}:{port}...')

            try:
                ss.connect((address, port))
            except Exception as e:
                print(f'an exception occurred while connecting on remote server: Exception = {e}', file = sys.stderr)
                return


            for sent_message in input_file:
                ss.sendall(sent_message.encode())

                received_message = ss.recv(self.payload_size)
                print(str(received_message, encoding = 'utf-8'), end = '', file = output_file)

        print(f'closing connection with {address}:{port}...')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'reads messages from STDIN, sends them to remote server and writes the reply on STDOUT')

    parser.add_argument('--host', '-H', type = str, default = 'localhost', help = 'remote server\'s address (default localhost)')
    parser.add_argument('--port', '-p', type = int, default = 8080, help = 'remote server\'s port (default 8080)')

    args = parser.parse_args()

    Client().connect_on_server(args.host, args.port)