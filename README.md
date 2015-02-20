#Simple Python Router
- Tested with Python 2.7.6

Written with an OOP approach, though I think it makes the
program unnecessarily complicated, I've continued it because
that's how I started. 

## To Run:
./route.py [23456]

## Full Usage:
```bash
usage: route.py [-h] [-v] [--version] [--size N] [--buffer M] [PORT]

Route messages between clients. Tested with Python 2.7.6

positional arguments:
  PORT              The port number for the server (default: 23456)

optional arguments:
  -h, --help        show this help message and exit
  -v, --verbose     verbose output (default: False)
  --version         show program's version number and exit
  --size N          The maximum number N of clients to accept (2 < N < 1024).
                    Note: one client is reserved. (default: 255)
  --buffer M, -b M  The maximum size M of messages to accept (2048 < M <
                    10240) (default: 2048)
```

