## MergeTB Testbed Instrumentation
This guide sets up the sensors responsible for data collection on the MergeTB testbed.

### Source Code
The source code is found at: https://gitlab.com/mergetb/tech/instrumentation <br>
The `.deb` files can be fetched from: https://gitlab.com/groups/mergetb/tech/-/packages

Our nodes (which are Debian based), pull the latest 2 `.deb` image files named `DataSorcerers.deb` and `FusionCore.deb`. Then we need to set up the environment.
### Installation of DataSorcerers.deb on node

```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt update
sudo apt upgrade -y
```

We install the `DataSorcerers.deb` using the following command:

```bash
sudo dpkg -i DataSorcerers.deb
```

If encounter the following error:

```bash
Selecting previously unselected package datasorcerers.
(Reading database ... 60313 files and directories currently installed.)
Preparing to unpack DataSorcerers.deb ...
Hit:1 http://security.debian.org/debian-security bullseye-security InRelease
Hit:2 http://deb.debian.org/debian bullseye InRelease       
Hit:3 http://deb.debian.org/debian bullseye-updates InRelease
Hit:4 https://download.docker.com/linux/debian bullseye InRelease
Reading package lists... Done         
Building dependency tree... Done
Reading state information... Done
All packages are up to date.
Unpacking datasorcerers (1.0) ...
dpkg: dependency problems prevent configuration of datasorcerers:
 datasorcerers depends on strace; however:
  Package strace is not installed.
 datasorcerers depends on bpftrace; however:
  Package bpftrace is not installed.

dpkg: error processing package datasorcerers (--install):
 dependency problems - leaving unconfigured
Errors were encountered while processing:
 datasorcerers
```

Then, try the following commands:

```bash
sudo apt --fix-broken install
sudo dpkg -i DataSorcerers.deb
```

This should install `DataSorcerers.deb`, create the symbolic links, and install the system services.

### Installation of FusionCore.deb on node

We then install the `FusionCore.deb`

```bash
sudo dpkg -i FusionCore.deb
```

If you encounter the following error:

```bash
Selecting previously unselected package fusioncore.
(Reading database ... 45450 files and directories currently installed.)
Preparing to unpack FusionCore.deb ...
Hit:1 http://security.debian.org/debian-security bullseye-security InRelease
Hit:2 http://deb.debian.org/debian bullseye InRelease
Hit:3 http://deb.debian.org/debian bullseye-updates InRelease
Reading package lists... Done
Unpacking fusioncore (1.0) ...
dpkg: dependency problems prevent configuration of fusioncore:
 fusioncore depends on docker-ce; however:
  Package docker-ce is not installed.
 fusioncore depends on docker-ce-cli; however:
  Package docker-ce-cli is not installed.
 fusioncore depends on containerd.io; however:
  Package containerd.io is not installed.
 fusioncore depends on docker-buildx-plugin; however:
  Package docker-buildx-plugin is not installed.
 fusioncore depends on docker-compose-plugin; however:
  Package docker-compose-plugin is not installed.

dpkg: error processing package fusioncore (--install):
 dependency problems - leaving unconfigured
Errors were encountered while processing:
 fusioncore
```

We need to install Docker for the FusionCore. We can install docker with:

```bash
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian `lsb_release -cs` test"
sudo apt update
sudo apt install docker-ce
```

This should install `FusionCore.deb` and create the necessary systen elements.

### Pulling Docker images
The docker images are to be pulled to the system via the container registry on GitLab. They can be done through the following commands:

```bash
sudo docker pull registry.gitlab.com/mergetb/tech/instrumentation/psql:latest
sudo docker pull registry.gitlab.com/mergetb/tech/instrumentation/influx:latest
```

The output might look something like this:

```bash
latest: Pulling from mergetb/tech/instrumentation/psql
b0a0cf830b12: Already exists 
dda3d8fbd5ed: Pull complete 
283a477db7bb: Pull complete 
91d2729fa4d5: Pull complete 
9739ced65621: Pull complete 
ae3bb1b347a4: Pull complete 
f8406d9c00ea: Pull complete 
c199bff16b05: Pull complete 
e0d55fdb4d15: Pull complete 
c1cb13b19080: Pull complete 
873532e5f8c7: Pull complete 
050d9f8c3b1c: Pull complete 
710e142705f8: Pull complete 
cb628c265f09: Pull complete 
6051daefefaf: Pull complete 
825582430ab7: Pull complete 
409e62461d94: Pull complete 
c8644a76e024: Pull complete 
Digest: sha256:e2a3154857cb670b26b20955ca76a3cdc85c6ca5f7235832e5475c9b123c1245
Status: Downloaded newer image for registry.gitlab.com/mergetb/tech/instrumentation/psql:latest
registry.gitlab.com/mergetb/tech/instrumentation/psql:latest

.
.
.

latest: Pulling from mergetb/tech/instrumentation/influx
b0a0cf830b12: Pull complete 
a0233282981d: Pull complete 
02e83ee0e313: Pull complete 
bbba555ac45c: Pull complete 
19c0354213f2: Pull complete 
6c251dc7077b: Pull complete 
f5f2bb35f883: Pull complete 
3820c759c3b6: Pull complete 
9156434ddff3: Pull complete 
04e86d74ecaf: Pull complete 
Digest: sha256:5e66c8bb46853e1525c96b54df4fbd36ef67c3b29e9cefae1d0e526becb144cd
Status: Downloaded newer image for registry.gitlab.com/mergetb/tech/instrumentation/influx:latest
registry.gitlab.com/mergetb/tech/instrumentation/influx:latest
```

### Point Data Collection to FusionCore service
Since the FusionCore service is running on `botmaster` in this case, we direct the configuration to the botmaster in our case. We change the line #6 at `/etc/discern/SorcererConfig.yaml` to:

```
gprc_ip: botmaster.infra
```

### Restart the FusionCore service
Restart the FusionCore to initiate the `influx` and `psql` services by using the following command:

```bash
sudo systemctl restart FusionCore
```

In order to check if the services have been up, it can be done by checking the status through the command: `sudo docker ps`. The output is as follows:

```bash
CONTAINER ID   IMAGE                                                   COMMAND                  CREATED         STATUS                  PORTS                                       NAMES
ce75a6a8f7df   influxdb                                                "/entrypoint.sh infl…"   5 seconds ago   Up Less than a second   0.0.0.0:8086->8086/tcp, :::8086->8086/tcp   influx
d563a1ac0a9f   registry.gitlab.com/mergetb/tech/instrumentation/psql   "docker-entrypoint.s…"   20 hours ago    Up 20 hours             0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   gifted_kalam
```

### Check the logs
The log can be checked at the location of node where the FusionCore service is established (`botmaster` in our case). The log can be viewed at `/var/log/discern.log`. To keep the updated log running, the following command can be used:

```bash
tail -f discern.log
```