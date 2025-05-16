# Ransomware Scenario (Malware)

### Note: the encryption seems to happen on the attackers machine

- Runs byob on the attacker node
- Starts the byob client on compromised
The following files are encrypted / decrypted in this order:
    - encrypt_file "$HOME/testing.txt"
    - encrypt_file "/boot"
    - encrypt_file "/root"
    - encrypt_file "/home"
    - decrypt_file "/home/blankcanvas/.ssh"
    - decrypt_file "/home/blankcanvas/.bashrc"
    - decrypt_file "/home/blankcanvas/.profile"
- Attacker pauses
- Attacker kills byob software on compromised via byob
- Attacker stop byob server

