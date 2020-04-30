from scapy.all import *
import argparse
from itertools import cycle

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f',help='pcap file',required=True)  ## archer data file path
    argz = parser.parse_args()
    file = argz.f.strip()
    key = b"BeyWfkPjXCERVUCXUIhEypFFYesgqPfKjLfEhZEqKTnolrrcekCJdGQtdVgnbXcBqkPcGyOEIrmpgbhqJjfMIClzdwNmmhhrHPJXIqCtdyXlmrlEyWmsIPvGHrlGmBkkdLKjRhNxueKCzRWaMiTUYTHHwsfvaNBShLUwmgXLQulWNBjiVOAwsTWjDCCBhrGQHJNCgUKBIneOjZsKZMHRPQecKRFLVksEvRDFnOmJihvTwIRuZgiZuLUiBwCxVjrbvbaNnKqdWuUPJFtfAlADmelZQYQoRaNaKZCeYWtmnzdgJdRlvS"
    data = getdata(file)
    data = ''.join(chr(x ^ y) for (x,y) in zip(data, cycle(key)))
    print(data)

def getdata(file):
    capture = rdpcap(file)
    ping_data = b""

    for packet in capture:
       if ICMP in packet: # Echo request
           ping_data += packet.load
    ping_data = ping_data[8:]
    return ping_data


if __name__ == "__main__":
    main()
