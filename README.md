# An Exploration of DNS Denial of Service

*CSE 5472: Information Security Projects, The Ohio State University*

*Term Project, Autumn 2023*

*Group: Thomas Li, Prasanth Umapathy, Benjamin Wenger*

*Topic: DNS Security*

In this project, we examine the level of threat posed by various forms of denial of service (DoS) and distributed denial of service (DDoS) attacks directed towards or propogated through Domain Name System (DNS) infrastructure, as well as the effectiveness and practicality of countermeasures that we attempted to deploy against them. 

This repository contains the code artifacts, documentation, and instructions needed for running our experiments, with files organized into three categories:

- **Defense**

    - The code and configuration information needed for self-hosting an authoritative DNS server, which we made internet-accessible through the registration of a domain name and a static IP address in order to fully reflect the behavior of regular real-world nameservers. The external setup steps do not involve any of our own code artifacts, but instructions are included in this README to allow their replication. We used three different DNS server implementations in order to maximize our flexibility in implementing countermeasures and also examine differences in behavior and natural defensive capabilities:

        - A manual implementation consisting of a Python program that listens on port 53 and responds to DNS packets
        - [dnsmasq](https://thekelleys.org.uk/dnsmasq/doc.html), a simple, lightweight DNS server software designed for small networks
        - [BIND](https://www.isc.org/bind/), the most commonly used DNS server software in real-world systems

    - A one-line script to self-host a web server for which our DNS server resolves the domain name into the corresponding IP address. When btoh servers are running, any internet user can access our dummy website by looking up the domain name, representing arguably the most simple and common use case for DNS. This is only included for illustrative purposes and to help verify that our DNS server works.

    - The countermeasures we implemented to prevent our attacks from disrupting the functionality of our servers. Each of these are described in detail later in this README.

- **Attack**

    - Programs to execute the attacks that we implemented, which each have the goal of disabling proper usage of our DNS server. Each of these are described in detail later in this README.

- **Evaluation**

    - Programs to quantify the functionality of our server setup and the effects of our attacks and countermeasures on it by simulating "normal" server traffic coming from spoofed users attempting to access the site through its domain name, with measurements taken for the speed and success status of each user's request. Sample results are shown later in this README alongside the attacks and countermeasures that produced them.

    - Programs to process and visualize the raw measurements

We tried to make the code artifacts as modular and interchangeable as possible to make this work extensible. All that is necessary for the attack and evaluation programs to run is for the DNS server and web server to be running and to be accessible through the chosen domain name using public internet-based DNS resolution. Granted, the registered domain name and static IP needed for consistent internet accessibility both involve small monthly fees, though we considered that to be worth it for the improved convenience and realisticness.

In the next section, we will briefly discuss of the background and general real-world relevance of DNS denial-of-service threats, after which we will move on to the detailed instructions for properly configuring and running our setup with full internet accessibility and for executing the programs present in this repository. The bulk of this README will discuss the attacks and corresponding countermeasures that we implemented, with analysis of their measured effectiveness and their real-world applicability. The closing sections will discuss our overall takeaways and insights from this work, the extent of its usefulness in the real world, and potential improvements and expansions.


## Table of Contents
1. [Background](#background)
    1. [Domain Name System (DNS)](#domain-name-system-dns)
    2. [DNS and Denial of Service](#dns-and-denial-of-service)
2. [Usage Instructions](#usage-instructions)
    1. [External Setup](#external-setup)
        1. [Domain Name Registration](#domain-name-registration)
        2. [Static IP](#static-ip)
    2. [Running the Servers](#running-the-servers)
    3. [Running the Attacks](#running-the-attacks)
    4. [Running the Evaluation](#running-the-evaluation)
3. [Attacks and Countermeasures](#attacks-and-countermeasures)
4. [Conclusions](#conclusions)
5. [References](#references)


## Background

### Domain Name System (DNS)

Three decades into the Information Age, the Internet is so widely available, works so seamlessly, and is so embedded into daily life that it's easy for most people to take it for granted. British science fiction writer Arthur C. Clarke stated in 1962 that "any sufficiently advanced technology is indistinguishable from magic", widely quoted words that now often feel prescient for many real-world technologies, and which may come to mind whenever one does try to think about how the Internet came to be so ubiquitous. In this case, the technology behind the magic consists of a vast network of physical and digital infrastructure in which each connected entity implements a set of standardized protocols that allow it to exchange information with the others in a consistently comprehensible manner. 

Much of the heavy lifting is handled by the [Internet Protocol (IP)](https://en.wikipedia.org/wiki/Internet_Protocol), which handles the process of routing data packets across interconnected networks to allow end-to-end communication between any two devices with valid **IP addresses**. IP addresses are numeric and fixed-length, and can be subdivided such that the prefix identifies the network while the suffix identifies the specific device, making it fairly easy to do routing with them. When it comes to allowing human users to specify what they want to contact, though, these numbers can be difficult to memorize, especially as shorter IPv4 addresses get used up and are superseded by longer IPv6 addresses, and as Internet resources may often change servers or be hosted across multiple servers.

To get to the point where one can visit a website or send an email using a relatively short, easy-to-remember URL or email address, another protocol was needed: the [Domain Name System (DNS)](https://en.wikipedia.org/wiki/Domain_Name_System), which allows the recording and communication of mappings from these almost-arbitrary identification strings (called **domain names**) to the IP addresses of the resources they refer to. Introduced nearly 40 years ago in 1983, DNS's distributed server structure has allowed it to scale up with the Internet as a whole and become essentially its sole widely-used solution for human-readable naming.

This function is crucial to making the Internet usable for the average person, but it can be easily overlooked given how simple it may seem, with the delivery of the actual contents of any given resource typically being of bigger concern for most. The combination of high importance and low attention has made DNS a ripe target for attackers, who can exploit [various vulnerabilities](https://web.mit.edu/6.033/www/papers/dnssec.pdf) that have emerged over the years to disrupt access to websites or otherwise victimize their prospective visitors without the site operator or network operator being able to easily detect or realize the problem.

### DNS and Denial of Service

The most common DNS-based attacks have typically revolved around issues with data integrity and authentication in the protocol, with attackers often trying to spoof responses to DNS queries in order to trick the querying resolver into associating the attacker's chosen IP address with the requested domain. In most cases, this record gets cached, and subsequent users attempting to visit the targeted domain will be directed to the attackers site, a technique known as cache poisoning. This was widespread in the 2000s, but countermeasures have been widely implemented to make it more difficult to pass a spoofed DNS packet off as a real one, and enhanced versions of the protocol like DNS Security Extensions (DNSSEC) and DNS over HTTPS can fully prevent certain classes of these attacks though they have had lower adoption due to technical hurdles.

Denial of Service attacks take a much different approach. Instead of trying to do any sort of clever sleight-of-hand, they go full brute-force and try to overwhelm the server infrastructure until it becomes unusable. It's harder to execute when attackers have few resources, but also harder to counteract when they have many. Extensions to the protocol can do relatively little to help with limitations in hardware capacity, and if anything could make things marginally worse since they increase packet size and processing overhead.

Articles published as recently as [this year](https://www.csoonline.com/article/646765/sophisticated-http-and-dns-ddos-attacks-on-the-rise.html) highlight denial of service, particularly distributed denial of service (DDoS) as a growing problem in general, with the latest wave of attackers starting to use cloud computing in their botnets to greatly expand their offensive capabilities. DDoS targeted directly towards web (HTTP/S) servers is perhaps the type most commonly thought of, but, according to CloudFlare's latest [DDoS threat report](https://blog.cloudflare.com/ddos-threat-report-2023-q3/), DNS is the most common attack vector among the remainder, with DNS Floods making up around 47% of recorded network-layer (i.e., excluding application-layer HTTP-based attacks) DDoS attacks in Q3 of 2023.

Discussions of DNS DDoS attacks typically divide them into two main categories:

- [DNS Floods](https://www.cloudflare.com/learning/ddos/dns-flood-ddos-attack/), a type of symmetrical attack (meaning the attack volume is equal to the attacker's initial output capacity) in which the attacker simply overwhelms a DNS server with a very large volume of traffic.
- [DNS Amplifications](https://www.cloudflare.com/learning/ddos/dns-amplification-ddos-attack/), an asymmetrical attack in which the attacker uses a DNS server to propagate the attack by sending it small request packets designed to trigger large responses which then get directed to the target through spoofed IPs in the request header. Even if the target doesn't directly process the responses, the traffic can still clog the surrounding network, cutting off access to it anyway.

DNS amplifications may seem more clever and efficient, but once again it turns out that the cleverness makes the attack easier to mitigate in a capacity-independent manner. The reliance on spoofed IPs and the fact that the response traffic is being directed towards an entity that didn't request it raise visible red flags that network operators can use to categorically filter out the attacker's packets, and in the end only 2.5% of network-layer DDoS attacks were attributed to DNS amplification in Q3 2023. With DNS floods, though, the target is the one dealing with initial requests, which can be made to look almost indistinguishable from legitimate traffic. If the attacker can send enough, the defender is essentially helpless.

One may note that DNS floods sound about as basic and generic as you can get with denial of service, with the "just send a ton of stuff to the server" approach being exactly what most people probably think of when hearing the word "DDoS". Any distinctive attributes are a factor of the structure and dynamics of the targeted infrastructure, which we should discuss now to get a full picture of what we're dealing with.

With the way DNS is structured, there's generally [four different types](https://www.cloudflare.com/learning/dns/dns-server-types/) of DNS server that each play very distinct roles:

- The **resolvers** are the user's first point of contact whenever they need to look up a domain name. They take their requests and handle the process of querying other DNS servers to find and return the answers, which they may also cache afterwards
- The **root nameservers** are, in turn, the resolver's first point of contact. DNS is organized hierarchically to provide a consistent way of searching through its otherwise decentralized structure, and the root servers sit at the top of the hierarchy, from which they can direct the resolvers to any other section of it.
- The **top-level domain (TLD) nameservers** represent the first subdivision of the hierarchy, with each one maintaining information about the domain names that share its domain extension (e.g. .com, .org, .net). The root servers refer the resolvers to the TLD servers, which in turn refer the resolvers to the next level down.
- Lastly, the **authoritative nameservers** are the ones which can provide the actual mapping from the requested domain name to the corresponding IP address. The same information may be floating around elsewhere in caches, but the authoritative servers are the official source of truth, hence the name. To be accessible to the Internet, a domain name needs served by at least one of these (particularly one that's registered with the corresponding TLD server), with most having multiple for better resiliency.

From the attacker's perspective, taking down a resolver could cut off a user's ability to use the web, but anyone with at least small amount of tech-savviness can simply select a different one in their network settings. Resolvers mostly all perform the same function, and there's well-known publicly available options like Cloudflare's 1.1.1.1 and Google's 8.8.8.8 that are nearly impossible to take down because of how powerful and resilient the underlying infrastructure is. Root servers and TLD servers are similarly daunting targets, as they too involve large numbers of redundant instances maintained by various well-funded and well-prepared organizations, and the scope of the service they provide is much wider than what most are interested in targeting anyway.

This leaves the authoritative servers as the preferred target. These tend to be run by smaller organizations, and in some cases may be hosted on-premise by the same people who own the domain name and corresponding website. Unlike with the other server types, each instance or handful of instances has unique functionality in being the only ones to provide definitive records for certain domains, and taking them down will make the corresponding resources inaccessible for any user who doesn't either have access to a cached record (which generally expires after a short while) or somehow know the IP address. Even when there's redundancy, it can only do so much if all of the servers for the given domain are similarly weak.

As for what would make flooding the authoritative DNS server different from targeting the corresponding web server, beyond the prospect of the DNS server being an easier target due to simply having less attention paid to it, a few things come to mind:

- Since the DNS server typically gets contacted by the resolver rather than receiving queries directly from clients, defense based on IP address filtering is less practical since attackers can simply route their traffic through 1.1.1.1, 8.8.8.8, or other well-known legitimate resolvers, a tactic known as DNS laundering
- On the flip side, the fact that resolvers cache responses is something that defenders can take advantage of to reduce traffic loads. The IP addresses of a site's servers are typically much less subject to change than the actual site contents are, so the DNS server can let cached records stay valid for longer without worrying about data getting stale
- The list of valid records that a DNS server provides is typically very finite and enumerable, so intermediate firewalls could potentially be configured to drop packets that ask for anything else, counteracting attackers who try to get around caching by generating random invalid request. Of course, the firewall could also get overwhelmed, and if it takes more than a trivial amount of computation to distinguish between valid and invalid requests then it could be no better than simply having the server try to answer the request

Ultimately, with these attacks having been largely reduced to a game of brute force, either side having enough of a resource advantage will allow them to always come out on top regardless how much their adversary tries to exploit the properties of the protocol. But with that said, the threshold for "enough" can be made more elusive if one plays their cards well. In this project, we try to quantify just how much of a difference it can make, if any, to try having your defenses work smarter when they can't work any harder.


## Usage Instructions

### External Setup

#### Domain Name Registration

#### Static IP

### Running the Servers

### Running the Attacks

### Running the Evaluation


## Attacks and Countermeasures


## Conclusions


## References

- Wikipedia: [Domain Name System](https://en.wikipedia.org/wiki/Domain_Name_System)
- Wikipedia: [Internet Protocol](https://en.wikipedia.org/wiki/Internet_Protocol)
- Research paper: [Security vulnerabilities in DNS and DNSSEC](https://web.mit.edu/6.033/www/papers/dnssec.pdf)
- CSO: [Sophisticated HTTP and DNS DDoS attacks on the rise](https://www.csoonline.com/article/646765/sophisticated-http-and-dns-ddos-attacks-on-the-rise.html)
- Cloudflare: [DDoS threat report for 2023 Q2](https://blog.cloudflare.com/ddos-threat-report-2023-q2/)
- Cloudflare: [DDoS threat report for 2023 Q3](https://blog.cloudflare.com/ddos-threat-report-2023-q3/)
- Cloudflare: [What are the different types of DNS server?](https://www.cloudflare.com/learning/dns/dns-server-types/)
- Cloudflare: [What is a DNS Flood?](https://www.cloudflare.com/learning/ddos/dns-flood-ddos-attack/)
- Cloudflare: [What is a DNS amplification attack?](https://www.cloudflare.com/learning/ddos/dns-amplification-ddos-attack/)
- Bright: [DNS Flood DDoS Attack: How it Works and How to Protect Yourself](https://brightsec.com/blog/dns-flood-attack/)
- Bright: [DNS Amplification Attack: How they Work, Detection and Mitigation](https://brightsec.com/blog/dns-amplification-attack/)
- Imperva: [DNS Flood](https://www.imperva.com/learn/ddos/dns-flood/)
- Imperva: [DNS Flood of 1.5 Billion Requests a Minute, Fueled by DDoS Protection Services](https://www.imperva.com/blog/massive-dns-ddos-flood/)
- [Domain.com](domain.com)
- [PureVPN](purevpn.com)
- [dnsmasq](https://thekelleys.org.uk/dnsmasq/doc.html)
- [BIND](https://www.isc.org/bind/)
- [Trickest's list of trusted public DNS resolvers](https://github.com/trickest/resolvers/blob/main/resolvers-trusted.txt)]
