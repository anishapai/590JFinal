from scapy import *
import base64

capture = rdpcap('data.pcap')
ping_data = ""

for packet in capture:
   if packet[ICMP].type == 0: # Echo request
       ping_data += packet.load

print(ping_data)
