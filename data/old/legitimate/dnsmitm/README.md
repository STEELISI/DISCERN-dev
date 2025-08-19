# DNS Mitm (Real Use)

- Installs dnsutils and traceroute on the client node via apt
- Sets /etc/ettercap/etter.dns with the spoofed IP address on attacker
- Makes attacker use ettercap to arp poison and dns spoof the LAN for the rest of the experiment
- Sets up named config files to implement dnssec on cache
- Sets up named config files to implement non-dnssec case on cache
- Sets named on cache into non-dnssec case
- Makes client dig google.com 3 times
- Sets named on cache into dnssec case
- Makes client dig google.com 3 times
- Kills ettercap on attacker
- Pauses for 15 sec for data collection

