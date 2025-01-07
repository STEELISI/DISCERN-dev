#!/usr/bin/env bash
set -euo pipefail

# description: set some reasonable defaults for using our XDC

###
# script should run as root
#
if [ $EUID -ne 0 ]; then
    echo "Must be run as root"
    exit 1
fi

export DEBIAN_FRONTEND=noninteractive
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export LANGUAGE=en_US.UTF-8

# get the ubuntu distribution name via lsb_release or /etc/os-release
if [ $(command -v lsb_release) ]; then
  UBUNTU_CODENAME=$(lsb_release --codename --short)
else
  source /etc/os-release
fi

echo "[.] modify /etc/apt/sources.list to use us.archive.ubuntu.com"
cat << EOF > /etc/apt/sources.list
deb http://us.archive.ubuntu.com/ubuntu/ ${UBUNTU_CODENAME} main restricted universe
deb http://us.archive.ubuntu.com/ubuntu/ ${UBUNTU_CODENAME}-updates main restricted universe
deb http://us.archive.ubuntu.com/ubuntu/ ${UBUNTU_CODENAME}-backports main restricted universe multiverse

deb http://security.ubuntu.com/ubuntu/ ${UBUNTU_CODENAME}-security main restricted
deb http://security.ubuntu.com/ubuntu/ ${UBUNTU_CODENAME}-security universe
deb http://security.ubuntu.com/ubuntu/ ${UBUNTU_CODENAME}-security multiverse
EOF

echo "[.] uninstall ansible 2.5 and python 2.7"
# `apt-get remove` returns a non-zero error code if a package is not
# installed, which shouldn't result in an exit of this script.
apt-get remove --assume-yes --purge ansible || true
apt-get autoremove --assume-yes --purge

# fix "invoke-rc.d: policy-rc.d denied execution of start."
# since we don't have systemd or some run system
printf '#!/bin/sh\nexit 0' > /usr/sbin/policy-rc.d

echo "LC_ALL=en_US.UTF-8" | sudo tee -a /etc/environment > /dev/null
echo "en_US.UTF-8 UTF-8" | sudo tee -a /etc/locale.gen > /dev/null
echo "LANG=en_US.UTF-8" | sudo tee /etc/locale.conf > /dev/null

echo "[.] update and install some useful packages"
apt update
apt install --assume-yes \
    dialog \
    locales

locale-gen en_US.UTF-8

apt install --assume-yes \
    dnsutils \
    git \
    git-lfs \
    less \
    lsb-release \
    net-tools \
    parallel \
    python3.11 \
    python3-pip \
    python3-netaddr \
    renameutils \
    rsync \
    screen \
    traceroute \
    vim

echo "[.] check if we can run `ping`?"
# ping on lighthouse is broken, so we need to reinstall
# return code of 126 -> bash: /usr/bin/ping: Operation not permitted
if [ $(ping >/dev/null 2>&1)$? -eq 126 ]; then
    echo "[.] can't run ping, reinstalling iputils-ping"
    apt-get reinstall iputils-ping
else
    echo "[.] ping is OK"
fi

echo "[.] set python and python3 to /usr/bin/python3.11"
update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

echo "[.] upgrade pip from 9.0 to 21.x"
pip3 install --upgrade pip

echo "[.] install ansible 4"
pip install ansible

echo "[.] install influxdb client"
pip install influxdb-client
