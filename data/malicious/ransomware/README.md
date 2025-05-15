# Ransomware Scenario (Malware)

### Note: the encryption seems to happen on the attackers machine

- Runs byob on the attacker node
- Starts the byob client on compromised
- encrypts the file ~/testing.txt
- Locates all txt files in the file system with byob shell, find, and grep
- Encrypts the first 20 files in that list
- Locates all c files in the file system with byob shell, find, and grep
- Encrypts the first 20 files in that list
- Locates all files in ~/.config with byob shell, find, and grep
- Encrypts the first 20 files in that list
- Attacker pauses
- Attacker kills byob software on compromised via byob
- Attacker stop byob server

