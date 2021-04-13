#!/usr/bin/env python3

import argparse
import csv
import io
import os
import pathlib
import server
import signal
import socket
import sys

from data import Data


def count_word_occurrences(content):
    count = dict()
    for word in content.split():
        count[word] = count.get(word, 0) + 1

    return count

def encode_word_occurrences_to_csv(count):
    r = io.StringIO()

    writer = csv.writer(r)
    for word in count:
        writer.writerow([word, count[word]])

    return r.getvalue()


class Processing(server.Server):
    '''
    Reimplements the Server Class.
    '''

    def __init__(self, data_address = 'localhost', data_port = 8080, payload_size = 1024):
        super().__init__(payload_size = payload_size)

        self.data_address = data_address
        self.data_port = data_port

    def request_handler(self, peer_conn, peer_address, data = ''):
        filename = data.rstrip(os.linesep)
        print(f'  > {peer_address[0]}:{peer_address[1]} has requested the {filename} file', file = sys.stderr)

        content = self.get_file_content(filename)

        response = ''

        if Data.is_error(content):
            response = content
        else:
            response = encode_word_occurrences_to_csv(count_word_occurrences(content))

        peer_conn.send(response.encode())

    def get_file_content(self, filename):
        '''
        Connects with Data Server and sends the received file name.

        Args:
            filename (str): The requested file name.

        Returns:
            str: The content of the file name requested to the Data Server.
        '''

        content = ''

        with socket.socket() as data_conn:
            print(f'connecting to data service at {self.data_address}:{self.data_port}', file = sys.stderr)
            data_conn.connect((self.data_address, self.data_port))

            data_conn.sendall(filename.encode())
            print(f'requesting the content of {filename} on data service', file = sys.stderr)

            while True:
                raw = data_conn.recv(self.payload_size)
                if not raw:
                    break

                content += str(raw, encoding = 'utf-8')

        return content


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'starts the processing server')

    parser.add_argument('--host', '-H', type = str, default = 'localhost', help = 'local address (default localhost)')
    parser.add_argument('--port', '-p', type = int, default = 8080, help = 'local port (default 8080)')
    parser.add_argument('--data-address', type = str, default = 'localhost', help = 'data server\'s address (default localhost)')
    parser.add_argument('--data-port', type = int, default = 8080, help = 'data server\'s port (default 8080)')

    args = parser.parse_args()

    server = Processing(data_address = args.data_address, data_port = args.data_port)

    for ss in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(ss, lambda received_signal, frame: server.stop())

    server.start(host = args.host, port = args.port)