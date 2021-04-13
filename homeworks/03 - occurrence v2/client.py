#!/usr/bin/env python3

import argparse
import csv
import io
import socket
import sys
import os


def format_user_response(content):
    '''
    Decode the CSV, sort the occurrences and filter the top 10 words that appeared the most.

    Args:
        content (str): A CSV str content.

    Returns:
        str: A string that will be sent to the client.
    '''

    top10 = filter_top10_occurrences(decode_word_occurrences_from_csv(content))

    response = f'WORD\t\tOCCURRENCES{os.linesep}'
    for item in top10:
        response += f'{item[0]}\t\t{item[1]}{os.linesep}'

    return response

def filter_top10_occurrences(count):
    '''
    Filter the top 10 word occurrence.

    Args:
        count (dict): Contains the word as a key and it's occurence as a value.

    Returns:
        list (tuples): Each element is a word and it's ocurrences, 
        first by the most occurrence and, if needed a lexicographical order (in case two words tie).
    '''

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
    '''
    Aggregate word with the same count on the same "structure", so they don't "compete" with each other.

    Args:
        count (dict): Contains the word as a key and it's occurence as a value.

    Returns:
        dict: Contains the words as values and their ocurrences as keys.
    '''

    count_by_occurrences = {}
    for word, occurrences in count.items():
        count_by_occurrences[occurrences] = count_by_occurrences.get(occurrences, []) + [word]

    return count_by_occurrences

def decode_word_occurrences_from_csv(content):
    '''
    Decodes a received CSV to a dict.

    Args:
        count (csv): A received CSV.

    Returns:
        dict: Contains the words as keys and their ocurrences as values.
    '''

    count = {}
    for row in csv.reader(io.StringIO(content)):
        word, occurrences = row[0], int(row[1])
        count[word] = occurrences

    return count


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
                sent_message = sent_message.rstrip(os.linesep)

                if not sent_message:
                    continue

                ss.sendall(sent_message.encode())

                content = ''
                while True:
                    received_message = ss.recv(self.payload_size)
                    if not received_message:
                        break

                    content += str(received_message, encoding = 'utf-8')

                    if len(received_message) < self.payload_size:
                        break

                print(format_user_response(content), file = output_file)


        print(f'closing connection with {address}:{port}...')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'reads messages from STDIN, sends them to remote server and writes the reply on STDOUT')

    parser.add_argument('--host', '-H', type = str, default = 'localhost', help = 'remote server\'s address (default localhost)')
    parser.add_argument('--port', '-p', type = int, default = 8080, help = 'remote server\'s port (default 8080)')

    args = parser.parse_args()

    Client().connect_on_server(args.host, args.port)