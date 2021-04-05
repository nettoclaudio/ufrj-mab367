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


def format_user_response(content):
    top10 = filter_top10_occurrences(decode_word_occurrences_from_csv(content))

    response = f'WORD\t\tOCCURRENCES{os.linesep}'
    for item in top10:
        response += f'{item[0]}\t\t{item[1]}{os.linesep}'

    return response

def filter_top10_occurrences(count):
    count_by_occurrences = aggregate_words_by_occurrence(count)

    desc_occurrences = list(count_by_occurrences.keys())
    desc_occurrences.sort(reverse = True)

    result = []
    for occurrence in desc_occurrences:
        words = count_by_occurrences[occurrence]
        words.sort()

        for word in words:
            if len(result) == 10:
                return result

            item = (word, occurrence)
            result.append(item)

    return result

def aggregate_words_by_occurrence(count):
    count_by_occurrences = {}
    for word, occurrences in count.items():
        count_by_occurrences[occurrences] = count_by_occurrences.get(occurrences, []) + [word]

    return count_by_occurrences

def decode_word_occurrences_from_csv(content):
    count = {}
    for row in csv.reader(io.StringIO(content)):
        word, occurrences = row[0], int(row[1])
        count[word] = occurrences

    return count

class Interface(server.Server):

    def __init__(self, processing_address = 'localhost', processing_port = 8080, threads = 2, payload_size = 1024):
        super().__init__(threads = threads, payload_size = payload_size)

        self.processing_address = processing_address
        self.processing_port = processing_port

    def handle_connection(self, worker_id, peer_conn, peer_address):
        data = peer_conn.recv(self.payload_size)
        if not data:
            print(f'worker #{worker_id}: {peer_address[0]}:{peer_address[1]} sent no data, closing connection', file = sys.stderr)
            return

        filename = str(data, encoding = 'utf-8').rstrip(os.linesep)
        print(f'worker #{worker_id}: {peer_address[0]}:{peer_address[1]} has requested the {filename} file', file = sys.stderr)

        content = self.get_word_occurrences(worker_id, filename)

        response = ''

        if Data.is_error(content):
            response = content
        else:
            response = format_user_response(content)

        peer_conn.send(response.encode())

    def get_word_occurrences(self, worker_id, filename):
        content = ''

        with socket.socket() as processing_conn:
            print(f'worker #{worker_id}: connecting to processing service at {self.processing_address}:{self.processing_port}', file = sys.stderr)
            processing_conn.connect((self.processing_address, self.processing_port))

            processing_conn.sendall(filename.encode())
            print(f'worker #{worker_id}: requesting the content of {filename} on data service', file = sys.stderr)

            while True:
                raw = processing_conn.recv(self.payload_size)
                if not raw:
                    break

                content += str(raw, encoding = 'utf-8')

        return content


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'starts the interface server')

    parser.add_argument('--host', '-H', type = str, default = 'localhost', help = 'local address (default localhost)')
    parser.add_argument('--port', '-p', type = int, default = 8080, help = 'local port (default 8080)')
    parser.add_argument('--threads', '-t', type = int, default = 2, help = 'max number of simultaneous clients (default 2)')
    parser.add_argument('--processing-address', type = str, default = 'localhost', help = 'processing server\'s address (default localhost)')
    parser.add_argument('--processing-port', type = int, default = 8080, help = 'processing server\'s port (default 8080)')

    args = parser.parse_args()

    server = Interface(processing_address = args.processing_address, processing_port = args.processing_port, threads = args.threads)

    for ss in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(ss, lambda received_signal, frame: server.stop())

    server.start(host = args.host, port = args.port)