# 590JFinal
These files extract data specific to the MySQL database setup in **sql_creation.sql**

## payload.py
Implant that is injected into the target machine as pyconfig.py.

1. Uses **requirements.txt** (https://github.com/danielmiessler/SecLists/blob/master/Passwords/Leaked-Databases/rockyou-75.txt) as wordlist to crack the MySQL password.
2. Opens a socket that listens for a connection from attack machine. Executes commands as described below.

## command.py
Command & control script which is run from the attack machine after payload.py is run. 

- Path to a file containing an obfuscated sql query (first and last character of every line) to receive results of query in ICMP ping. e.g. **sql.txt** which contains the query *select * from patients where name = 'Our Guy';*
- 'E' to exit socket connection
- 'D' to delete trace of payload from target machine

## extract_exfil.py
Extraction script which takes the .pcap Wireshark file (argument **-f**) containing the ICMP ping and decrypts the data.
