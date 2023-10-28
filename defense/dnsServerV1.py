# This program manually implements DNS server functionality for our site by
# listening on port 53 and responding to DNS queries with responses listing
# our site's IP address

import socket
import dnslib

# Config
dns_server_ip = ''
dns_server_port = 53
min_packet_size = 512
zone = dnslib.textwrap.dedent('''
    $TTL 0
    $ORIGIN dummy-site-for-dns-ddos-testing.com

    www IN  A   45.74.34.221
''')

# Listen on port for UDP packets, parse contents and send responses
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((dns_server_ip, dns_server_port))
while True:
    packet, address = server_socket.recvfrom(min_packet_size)
    d = dnslib.DNSRecord.parse(packet)
    reply = d.replyZone(zone)
    server_socket.sendto(reply.pack(), address)