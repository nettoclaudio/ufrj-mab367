#!/usr/bin/env python3

import argparse
import pathlib
import server
import signal
import sys


class Data(server.Server):

    def __init__(self, threads = 2, payload_size = 1024, data_dir = '/tmp/files'):
        super().__init__(threads = threads, payload_size = payload_size)
        self.data_dir = data_dir

    def read_file(self, filename):
        path = pathlib.Path(self.data_dir, filename)

        if not path.is_file():
            raise FileNotFoundError(f'{filename} not found')

        with open(path, 'r') as f:
            return f.read()

    def handle_connection(self, worker_id, peer_conn, peer_address):
        while True:
            data = peer_conn.recv(self.payload_size)
            if not data:
                return

            filename = str(data, encoding='utf-8').rstrip('\r\n')

            try:
                content = self.read_file(filename)
                peer_conn.sendall(f'BEGIN_FOUND\n{content}\nEND_FOUND\n'.encode())

            except FileNotFoundError as e:
                peer_conn.sendall(f'BEGIN_FILE_NOT_FOUND\n{e}\nEND_FILE_NOT_FOUND'.encode())

            except Exception as e:
                print(f'worker #{worker_id}: an exception occurred while reading file {filename}: Exception = {e}', file = sys.stderr)
                return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'starts the data server')

    parser.add_argument('--host', '-H', type = str, default = 'localhost', help = 'local address (default localhost)')
    parser.add_argument('--port', '-p', type = int, default = 8080, help = 'local port (default 8080)')
    parser.add_argument('--threads', '-t', type = int, default = 2, help = 'max number of simultaneous clients (default 2)')
    parser.add_argument('--data-dir', type = str, default = '/tmp/files', help = 'path in filesystem which the files are stored (default /tmp/files)')

    args = parser.parse_args()

    server = Data(data_dir = args.data_dir)

    for ss in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(ss, lambda received_signal, frame: server.stop())

    server.start(host = args.host, port = args.port)