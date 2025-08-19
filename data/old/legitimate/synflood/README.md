# Synflood Scenario (Real Use)

- Client dumps eth1 to ~/results.pcap
- Client curls server/index.html every second
- Script pauses for data collection
- Attacker starts the flooder program
- Script pauses for data collection
- Attacker stops flooder program
- Client stops curling server
- Client stops tcpdump
- Syn cookies are activated on server
- Client dumps eth1 to ~/results.pcap
- Client curls server/index.html every second
- Script pauses for data collection
- Attacker starts the flooder program
- Script pauses for data collection
- Attacker stops flooder program
- Client stops curling server
- Client stops tcpdump
- Script pauses so last data can be dumped

