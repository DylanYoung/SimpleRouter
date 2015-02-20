```bash
usage: route.py [-h] [-v] [--version] [--size {3,15,63,255,511,1023}] [PORT]

Route messages between clients. Tested with Python 2.7.6

positional arguments:
  PORT                  The port number for the server (default: 23456)

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         verbose output (default: False)
  --version             show program's version number and exit
  --size {3,15,63,255,511,1023}
                        The maximum number of clients to accept (default: 255)
```