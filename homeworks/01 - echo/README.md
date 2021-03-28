# echo

This homework introduces the usage of Socket API on Python, in order to abstract a socket and allow communication over network infrastructure.

To illustrate a basic distributed system, it implements a client/server architecture where the server echoes the incoming messages to their clients.

## Usage

Start the server (the passive pair) by running the command below:

```bash
$ ./server.py --host 0.0.0.0 --port 8080
```

In a new terminal session, connect the client (active pair) to the server by issuing the command below:

```bash
$ ./client.py --host localhost --port 8080
> hello world
< hello world
> PING
< PING
> CTRL+d (to exit)
```