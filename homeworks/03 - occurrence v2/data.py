#!/usr/bin/env python3

import argparse
import os
import pathlib
import signal
import sys

import server


def read_file(path):
    with open(path, 'r') as fh:
        return fh.read()


class Data(server.Server):
    '''
    Connects to the remote server, sends the messages from STDIN to there
    and writes the replies on STDOUT.

    Args:
        address (str): remote server address.
        port (int): remote server port.
    '''

    ERROR_FILE_NOT_FOUND        = 'error: file not found'
    ERROR_INTERNAL_SERVER_ERROR = 'error: internal server error'

    def __init__(self, data_dir, payload_size = 1024):
        super().__init__(payload_size = payload_size)
        self.data_dir = data_dir

    def request_handler(self, peer_conn, peer_address, data = ''):
        message = ''

        try:
            filename = data.rstrip(os.linesep)
            print(f'  > {peer_address[0]}:{peer_address[1]} has requested the {filename} file', file = sys.stderr)

            message = read_file(pathlib.Path(self.data_dir, filename))

        except FileNotFoundError as e:
            message = Data.ERROR_FILE_NOT_FOUND

        except Exception as e:
            message = Data.ERROR_INTERNAL_SERVER_ERROR
            print(f'an exception occurred while reading file {filename}: Exception = {e}', file = sys.stderr)

        finally:
            peer_conn.send(f'{message}{os.linesep}'.encode())
            peer_conn.close()

    @staticmethod
    def is_error(message):
        return Data.ERROR_INTERNAL_SERVER_ERROR in message or Data.ERROR_FILE_NOT_FOUND in message


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'starts the data server')

    parser.add_argument('--host', '-H', type = str, default = 'localhost', help = 'local address (default localhost)')
    parser.add_argument('--port', '-p', type = int, default = 8080, help = 'local port (default 8080)')
    parser.add_argument('--data-dir', type = str, default = './files', help = 'path at filesystem which the files are stored (default ./files)')

    args = parser.parse_args()

    server = Data(data_dir = args.data_dir)

    for ss in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(ss, lambda received_signal, frame: server.stop())

    server.start(host = args.host, port = args.port)