# Chord K/V

This script allows to create a P2P network which implements a minimal set of
features from Chord. It creates a network of peer which allows to fetch and
store key-values from any node in the ring.

## Running

```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ ./chord.py --base-port 8000 --size 16
```

```bash
$ source venv/bin/activate
$ ./client.py --host localhost --port 8000 set foo bar
Data stored at localhost:8003

$ ./client.py --host localhost --port 8000 get foo
Answer from node at localhost:8003:
> foo = bar
```
