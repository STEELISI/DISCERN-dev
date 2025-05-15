# Packet Sniffer (Malware)

- Runs byob on the attacker node
- Starts the byob client on victim1 and victim2 (they connect to attacker)
- Attacker runs the packet sniffer malware attack on victim 1 (packets heard on victim 1 are stored locally on victim 1)
- Attacker runs the packet sniffer malware attack on victim 2 (packets heard on victim 2 are stored locally on victim 2)
- Attacker pauses
- Attacker downloads sniffed packets from victim 1
- Attacker downloads sniffed packets from victim 2
- Attacker kills packet sniffer malware attack on victim 1
- Attacker kills packet sniffer malware attack on victim 2
- Attacker kills byob software on victim 1 via byob
- Attacker kills byob software on victim 2 via byob
- Attacker stop byob server

