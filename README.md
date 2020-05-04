# 590JFinal
These files extract data specific to the MySQL database setup in **sql_creation.sql**

## payload.py
The implant that is injected into the target machine as pyconfig.py. It does the following:

1. Uses the wordlist **requirements.txt** (https://github.com/danielmiessler/SecLists/blob/master/Passwords/Leaked-Databases/rockyou-75.txt) to crack the MySQL password.
2. Opens a socket that listens for a connection from the attack machine and executes the commands received, as described below.

## command.py
The command & control script which is run from the attack machine after payload.py is run (persistently) from the target.

It takes the following commands that are then sent to the target machine:
- Path to a file containing an obfuscated sql query, the results of which are received in an ICMP ping. 
    - the file is obscured in that the query is the first and last character of every line e.g. **sql.txt** which contains the query *select * from patients where name = 'Our Guy';*
- 'E' to exit socket connection
- 'D' to delete trace of payload from target machine

## extract_exfil.py
The extraction script which takes a .pcap Wireshark file (as argument **-f**) containing the ICMP ping, and decrypts the data.
