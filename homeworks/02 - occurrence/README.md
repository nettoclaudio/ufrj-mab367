# Word Occurrences

## Usage

1. Start the data service

```bash
$ ./data.py --data-dir ./testdata --port 8002
```

2. Start the processing service

```bash
$ ./processing.py --data-port 8002 --port 8001
```

3. Start the interface service

```bash
$ ./interface.py --processing-port 8001 --port 8000
```

4. Ask for a file over the interface service.

```bash
$ echo "lorem.txt" | ./client.py --port 8000
WORD            OCCURRENCES
et              13
sit             13
quis            11
Maecenas                10
nec             10
a               9
ac              9
Cras            8
amet            8
at              8
```