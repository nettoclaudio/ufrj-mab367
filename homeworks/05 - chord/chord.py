#!/usr/bin/env python3

import argparse
import hashlib
import math
import os
import time
import sys

import rpyc
from rpyc.utils.server import ThreadedServer


N = 16
BASE_PORT = 8000

class Node(rpyc.Service):
    def __init__(self, id, address):
        self.id = id
        self.address = address

        self.data = {}

        self.finger_table = []

        max_peers = int(math.log(N, 2))
        for i in range(max_peers):
            peer_address = ('localhost', BASE_PORT + ((self.id + (2 ** i)) % N))
            self.finger_table.append(peer_address)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        s = f'Node #{self.id}:\n'

        s += 'Finger table:\n'
        s += '\tNode shift | Node address\n'
        for index, address in enumerate(self.finger_table):
            s += f'\t{index + 1}  | {address[0]}:{address[1]}\n'
        s += '\n'
        return s

    def exposed_lookup(self, key):
        if type(key) != str:
            raise Exception('key must be string')

        print(f'> Node #{self.id}: Calculating which node is holding the "{key}" key...')

        digest = hashlib.sha1(key.encode('ascii')).hexdigest()
        node_id = int(digest, 16) % N

        print(f'Node #{self.id}: SHA1({key}) = {digest} = {int(digest, 16)} % {N} = {node_id} which is the target node ID')

        if node_id == self.id:
            return self.address

        nearest_node_address = ()
        for index, address in enumerate(self.finger_table):
            n = (self.id + (2 ** index)) % N

            if n == node_id:
                return address

            if n > node_id:
                break

            nearest_node_address = address

        with rpyc.connect(nearest_node_address[0], nearest_node_address[1]) as conn:
            return conn.root.lookup(key)

    def exposed_set(self, key, value):
        address, port = self.exposed_lookup(key)

        if self.am_i_this_node(address, port):
            self.data[key] = value
            return

        with rpyc.connect(address, port) as conn:
            conn.root.set(key, value)

    def exposed_get(self, key):
        address, port = self.exposed_lookup(key)

        if self.am_i_this_node(address, port):
            return self.data.get(key)

        with rpyc.connect(address, port) as conn:
            return conn.root.get(key)

    def am_i_this_node(self, address, port):
        return self.address[0] == address and self.address[1] == port

def create_node(identifier):
    return Node(identifier, ('localhost', BASE_PORT + identifier))

def start_node(node):
    print(f'Starting node #{node.id} at {node.address[0]}:{node.address[1]}...')

    server  = ThreadedServer(node, port = node.address[1])
    server.start()

    print(f'Finishing node #{node.id}...')

def start_network():
    print(f'Starting the Chord network with {N} nodes...')

    jobs = []
    nodes = []

    for i in range(N):
        node = create_node(i)
        nodes.append(node)

        job = os.fork()
        if job > 0:
            jobs.append(job)
            continue

        return start_node(node)

    for line in sys.stdin:
        line = line.rstrip('\n')

        if line == 'list':
            print('Listing nodes')

            for node in nodes:
                print(node)

        if line == 'quit':
            break

    print(f'Waiting children terminate themselves...')

    for job in jobs:
        os.waitpid(job, 0)

def main():
    parser = argparse.ArgumentParser(description = 'Start a P2P network to read and store data')

    parser.add_argument('--base-port', type = int, default = 8000, help = 'base port to bind the Chord nodes on (default 8000)')
    parser.add_argument('--size', '-N', type = int, default = 16, help = 'nodes size (default 16)')

    args = parser.parse_args()

    global N
    N = args.size

    global BASE_PORT
    BASE_PORT = args.base_port

    start_network()

if __name__ == '__main__':
    main()
