# This program manually implements DNS server functionality for our site by
# listening on port 53 and responding to DNS queries with responses listing
# our site's IP address

import socket
import dnslib

# Config

dns_server_ip = ''
dns_server_port = 5053
min_packet_size = 512

domain = 'dummy-site-for-dns-ddos-testing.com.'
ip = '45.74.34.221'

# Adapted from https://gist.github.com/nsuan/6da86e94c067d6fd8d61
ns_records = [dnslib.NS("ns1." + domain), dnslib.NS("ns2." + domain)]
records = { # If the subdomain and request type match, the corresponding info will be returned
    domain: [dnslib.A(ip)],
    "www." + domain: [dnslib.A(ip)],
    "ns1." + domain: [dnslib.A(ip)],
    "ns2." + domain: [dnslib.A(ip)]
}

ttl = 0 # Control caching here

# Listen on port for UDP packets, parse contents and send responses
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((dns_server_ip, dns_server_port))
total_count = 0
while True:
    packet, address = server_socket.recvfrom(min_packet_size)
    print("Received packet from " + str(address))
    
    d = dnslib.DNSRecord.parse(packet)
    print(d)

    qname = str(d.q.qname)
    qtype = dnslib.QTYPE[d.q.qtype]

    if qname == domain or qname.endswith('.' + domain):
        reply = d.reply()
        # For matching domain, look through list of records for matching type and subdomain
        # I adapted this part from the code sample linked earlier too
        if qname in records:
            for rdata in records[qname]:
                rtype = rdata.__class__.__name__
                if qtype == rtype or qtype == "*":
                    reply.add_answer(dnslib.RR(rname=qname, rtype=dnslib.QTYPE.reverse[rtype], rclass=1, ttl=ttl, rdata=rdata))
        # Add nameserver records too - idk if this is actually needed for anything
        for rdata in ns_records:
            reply.add_auth(dnslib.RR(rname=domain, rtype=dnslib.QTYPE.NS, rclass=1, ttl=ttl, rdata=rdata))
            reply.add_ar(dnslib.RR(rname=rdata.label, rtype=dnslib.QTYPE.A, rclass=1, ttl=ttl, rdata=records[str(rdata.label)][0]))

        print("Sending reply:")
        print(reply)
        
        server_socket.sendto(reply.pack(), address)
        print("Reply sent")
    else:
        print("Domain doesn't match (got '" + qname + "'), no reply sent")
    
    total_count += 1
    print("Total packets processed: " + str(total_count))
