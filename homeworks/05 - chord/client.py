#!/usr/bin/env python3

import argparse
import sys

import rpyc


def lookup(address, port, key):
    with rpyc.connect(address, port) as conn:
        return conn.root.lookup(key)

def set(address, port, key, value):
    address, port = lookup(address, port, key)

    with rpyc.connect(address, port) as conn:
        print(f'Data stored at {address}:{port}', file = sys.stderr)
        conn.root.set(key, value)

def get(address, port, key):
    address, port = lookup(address, port, key)

    with rpyc.connect(address, port) as conn:
        value = conn.root.get(key)
        print(f'Answer from node at {address}:{port}:', file = sys.stderr)
        print(f'> {key} = {value}')

def main():
    parser = argparse.ArgumentParser(description = 'Read and store data over a P2P network')

    parser.add_argument('--host', '-H', type = str, default = 'localhost', help = 'remote server\'s address (default localhost)')
    parser.add_argument('--port', '-p', type = int, default = 8000, help = 'remote server\'s port (default 8000)')

    subparsers = parser.add_subparsers(dest='action')

    get_command = subparsers.add_parser('get', help = 'read data')
    get_command.add_argument('key', type = str, nargs = 1, help = 'the key')

    set_command = subparsers.add_parser('set', help = 'store data')
    set_command.add_argument('key', type = str, nargs = 1, help = 'the key')
    set_command.add_argument('value', type = str, nargs = 1, help = 'the value')

    args = vars(parser.parse_args())

    address = args.get('host')
    port = args.get('port')

    command = args.get('action')

    key = args.get('key').pop()

    if command == "get":
        return get(address, port, key)

    if command == "set":
        return set(address, port, key, args.get('value').pop())

if __name__ == '__main__':
  main()
