#!/usr/bin/env bash

# Generate encrypted password:
# python3 -c 'import crypt,getpass; print(crypt.crypt(getpass.getpass(), crypt.mksalt(crypt.METHOD_SHA512)))'

#sed -i "s/#Port 22/Port $1/" /etc/ssh/sshd_config
rm -rf /etc/ssh/*key*
DEBIAN_FRONTEND=noninteractive dpkg-reconfigure openssh-server
echo "root:$1" | chpasswd --encrypted
/usr/sbin/sshd -D
