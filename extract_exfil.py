from scapy import *
import argparse

def main():
    parser.add_argument('-f',help='pcap file',required=True)  ## archer data file path
    argz = parser.parse_args()
    file = argz.f.strip()
    key = "BeyWfkPjXCERVUCXUIhEypFFYesgqPfKjLfEhZEqKTnolrrcekCJdGQtdVgnbXcBqkPcGyOEIrmpgbhqJjfMIClzdwNmmhhrHPJXIqCtdyXlmrlEyWmsIPvGHrlGmBkkdLKjRhNxueKCzRWaMiTUYTHHwsfvaNBShLUwmgXLQulWNBjiVOAwsTWjDCCBhrGQHJNCgUKBIneOjZsKZMHRPQecKRFLVksEvRDFnOmJihvTwIRuZgiZuLUiBwCxVjrbvbaNnKqdWuUPJFtfAlADmelZQYQoRaNaKZCeYWtmnzdgJdRlvS"

    data = get_data(file)
    data = key ^ data
    print(data)

def getdata(file):
    capture = rdpcap(file)
    ping_data = ""

    for packet in capture:
       if packet[ICMP].type == 0: # Echo request
           ping_data += packet.load

    return ping_data


if __name__ == "__main__":
    main()
