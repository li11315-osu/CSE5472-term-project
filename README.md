# An Exploration of DNS Denial of Service

*CSE 5472: Information Security Projects, The Ohio State University*

*Term Project, Autumn 2023*

*Group: Thomas Li, Prasanth Umapathy, Benjamin Wenger*

*Topic: DNS Security*

In this project, we examine the level of threat posed by denial of service (DoS) and distributed denial of service (DDoS) attacks directed towards Domain Name System (DNS) infrastructure, as well as the effectiveness and practicality of countermeasures that we attempted to deploy against them. 

This repository contains the code artifacts, documentation, and instructions needed for running our experiments, with files organized into three categories:

- **Defense**

    - The code and configuration information needed for self-hosting an authoritative DNS server, which we made internet-accessible through the registration of a domain name and a static IP address in order to fully reflect the behavior of regular real-world nameservers. The external setup steps do not involve any of our own code artifacts, but instructions are included in this README to allow their replication. We used two different DNS server implementations in order to maximize our flexibility in implementing countermeasures and also examine differences in behavior and natural defensive capabilities:

        - A manual implementation consisting of a Python program that listens on port 53 and responds to DNS packets
        - [BIND](https://www.isc.org/bind/), the most commonly used DNS server software in real-world systems

    - A one-line script to self-host a web server for which our DNS server resolves the domain name into the corresponding IP address. When both servers are running, any internet user can access our dummy website by looking up the domain name, representing arguably the most simple and common use case for DNS. This is only included for illustrative purposes and to help verify that our DNS server works.

    - The countermeasures we implemented to prevent our attacks from disrupting the functionality of our servers. Each of these are described in detail later in this README.

- **Attack**

    - Programs to execute the attacks that we implemented, which each have the goal of disabling proper usage of our DNS server. Each of these are described in detail later in this README.

- **Evaluation**

    - Programs to quantify the functionality of our server setup and the effects of our attacks and countermeasures on it by simulating "normal" server traffic coming from spoofed users attempting to resolve the site's domain name, with measurements taken for the speed and success status of each user's request. Collected results from our trials are shown later in this README.

    - The collected results for each trial we performed

    - Programs to process and visualize the raw measurements

We tried to make the code as modular and interchangeable as possible to make this work extensible. All that is necessary for the attack and evaluation programs to work is for the DNS server to be running on any networked host and to be accessible through the chosen domain name using public internet-based DNS resolution. Granted, the registered domain name and static IP needed for consistent internet accessibility both involve small monthly fees, though we considered that to be worth it for the improved convenience and realisticness.

In the next section, we will briefly discuss of the background and general real-world relevance of DNS denial-of-service threats. After that, we will discuss the contents of this repository in detail and will provide instructions for properly configuring and the components or our setup. From there, we list and analyze the methodology and results of each of our experimental trials. The closing sections will discuss our overall takeaways and insights from this work, the extent of its usefulness in the real world, and potential improvements and expansions.


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
        1. [Data Collection](#data-collection)
        2. [Analysis and Visualization](#analysis-and-visualization)
    5. [Running the Countermeasures](#running-the-countermeasures)
        1. [Rate-Limtiing](#rate-limiting)
        2. [Subdomain Filter](#subdomain-filter)
3. [Trials and Measurements](#trials-and-measurements)
    1. [11/06/2023](#11062023)
    4. [11/26/2023](#11262023)
4. [Conclusions](#conclusions)
    1. [Lessons Learned](#lessons-learned)
    2. [Unanswered Questions and Future Work](#unanswered-questions-and-future-work)
5. [References](#references)


## Background

### Domain Name System (DNS)

Three decades into the Information Age, the Internet is so widely available, works so seamlessly, and is so embedded into daily life that it's easy for most people to take it for granted. British science fiction writer Arthur C. Clarke stated in 1962 that "any sufficiently advanced technology is indistinguishable from magic" - widely quoted words that now often feel prescient for many real-world technologies, and which may come to mind whenever one does try to think about how the Internet came to be so ubiquitous. In this case, the technology behind the magic consists of a vast network of physical and digital infrastructure in which each connected entity implements a set of standardized protocols that allow it to exchange information with the others in a consistently comprehensible manner. 

Much of the heavy lifting is handled by the [Internet Protocol (IP)](https://en.wikipedia.org/wiki/Internet_Protocol), which handles the process of routing data packets across interconnected networks to allow end-to-end communication between any two devices with valid **IP addresses**. IP addresses are numeric and fixed-length, and can be subdivided such that the prefix identifies the network while the suffix identifies the specific device, making it fairly easy to do routing with them. When it comes to allowing human users to specify what they want to contact, though, these numbers can be difficult to memorize, especially as shorter IPv4 addresses get used up and are superseded by longer IPv6 addresses, and as Internet resources may often change servers or be hosted across multiple servers.

To get to the point where one can visit a website or send an email using a relatively short, easy-to-remember URL or email address, another protocol was needed: the [Domain Name System (DNS)](https://en.wikipedia.org/wiki/Domain_Name_System), which allows the recording and communication of mappings from these almost-arbitrary identification strings (called **domain names**) to the IP addresses of the resources they refer to. Introduced nearly 40 years ago in 1983, DNS's distributed server structure has allowed it to scale up with the Internet as a whole and become essentially its sole widely-used solution for human-readable naming.

This function is crucial to making the Internet usable for the average person, but it can be easily overlooked given how simple it may seem, with the delivery of the actual contents of any given resource typically being of bigger concern for most. The combination of high importance and low attention has made DNS a ripe target for attackers, who can exploit [various vulnerabilities](https://web.mit.edu/6.033/www/papers/dnssec.pdf) that have emerged over the years to disrupt access to websites or otherwise victimize their prospective visitors without the site operator or network operator being able to easily detect or realize the problem.

### DNS and Denial of Service

The most common DNS-based attacks have typically revolved around issues with data integrity and authentication in the protocol, with attackers often trying to spoof responses to DNS queries in order to trick the querying resolver into associating the attacker's chosen IP address with the requested domain. In most cases, this record gets cached, and subsequent users attempting to visit the targeted domain will be directed to the attackers site, a technique known as cache poisoning. This was widespread in the 2000s, but countermeasures have been widely implemented to make it more difficult to pass a spoofed DNS packet off as a real one, and enhanced versions of the protocol like DNS Security Extensions (DNSSEC) and DNS over HTTPS can fully prevent certain classes of these attacks though they have had lower adoption due to technical hurdles.

Denial of Service attacks take a much different approach. Instead of trying to do any sort of clever sleight-of-hand, they go full brute-force and try to overwhelm the server infrastructure until it becomes unusable. It's harder to execute when attackers have few resources, but also harder to counteract when they have many. Extensions to the protocol can do relatively little to help with limitations in hardware capacity, and if anything could make things marginally worse since they increase packet size and processing overhead.

Articles published as recently as [this year](https://www.csoonline.com/article/646765/sophisticated-http-and-dns-ddos-attacks-on-the-rise.html) highlight denial of service, particularly distributed denial of service (DDoS) as a growing problem in general, with the latest wave of attackers starting to use cloud computing in their botnets to greatly expand their offensive capabilities. DDoS targeted directly towards web (HTTP/S) servers is perhaps the type most commonly thought of, but, according to CloudFlare's latest quarterly [DDoS threat report](https://blog.cloudflare.com/ddos-threat-report-2023-q3/), DNS is the most common attack vector among the remainder, with DNS Floods making up around 47% of recorded network-layer (i.e., excluding application-layer HTTP-based attacks) DDoS attacks in Q3 of 2023.

![](https://blog.cloudflare.com/content/images/2023/10/pasted-image-0--19-.png)

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

![](https://www.cloudflare.com/img/learning/dns/dns-server-types/authoritative-nameserver.png)

From the attacker's perspective, taking down a resolver could cut off a user's ability to use the web, but anyone with at least small amount of tech-savviness can simply select a different one in their network settings. Resolvers mostly all perform the same function, and there's well-known publicly available options like Cloudflare's 1.1.1.1 and Google's 8.8.8.8 that are nearly impossible to take down because of how powerful and resilient the underlying infrastructure is. Root servers and TLD servers are similarly daunting targets, as they too involve large numbers of redundant instances maintained by various well-funded and well-prepared organizations, and the scope of the service they provide is much wider than what most are interested in targeting anyway.

This leaves the authoritative servers as the preferred target. These tend to be run by smaller organizations, and in some cases may be hosted on-premise by the same people who own the domain name and corresponding website. Unlike with the other server types, each instance or handful of instances has unique functionality in being the only ones to provide definitive records for certain domains, and taking them down will make the corresponding resources inaccessible for any user who doesn't either have access to a cached record (which generally expires after a short while) or somehow know the IP address. Even when there's redundancy, it can only do so much if all of the servers for the given domain are similarly weak.

As for what would make flooding the authoritative DNS server different from targeting the corresponding web server, beyond the prospect of the DNS server being an easier target due to simply having less attention paid to it, a few things come to mind:

- Since the DNS server typically gets contacted by the resolver rather than receiving queries directly from clients, defense based on IP address filtering is less practical since attackers can simply route their traffic through 1.1.1.1, 8.8.8.8, or other well-known legitimate resolvers, a tactic known as DNS laundering

- On the flip side, the fact that resolvers cache responses is something that defenders can take advantage of to reduce traffic loads. The IP addresses of a site's servers are typically much less subject to change than the actual site contents are, so the DNS server can let cached records stay valid for longer without worrying about data getting stale

- The list of valid records that a DNS server provides is typically very finite and enumerable, so intermediate firewalls could potentially be configured to drop packets that ask for anything else, counteracting attackers who try to get around caching by generating random invalid request. Of course, the firewall could also get overwhelmed, and if it takes more than a trivial amount of computation to distinguish between valid and invalid requests then it could be no better than simply having the server try to answer the request

And therein lies the inherent problem with trying to counter denial-of-service: any packet that hits the defender's network will cause some level of strain on the defender's resources, be it from answering a legitimate request or trying to block or drop a suspicious one. In the end, these attacks can almost always be reduced to a game of brute force, where either side having enough of a resource advantage will allow them to come out on top regardless how much their adversary tries to exploit the properties of the protocol.

But with that said, the threshold for "enough" can be made more elusive if one plays their cards well. In this project, we try to quantify just how much of a difference it can make, if any, to try having your defenses work smarter when they can't work any harder.


## Usage Instructions

### External Setup

We wanted as much of a realistic setup as possible without running afoul of terms of service or cybercrime laws, so we decided we would self-host the actual server instance but would still make it accessible to public DNS resolvers. As we mentioned previously, doing the latter required us to buy a domain name so that we could register an authoritative DNS server for it, as well as a static IP address so that our server could be accessed in a consistent manner.

#### Domain Name Registration

DNS may be mostly decentralized, but everything that's Internet-accessible is still part of the same global hierarchy. People can't just go around adding nameservers for any arbitrary domain, or else no one would be able to host a site without someone else being able to make the URL redirect somewhere else. Systems are in place to allow people to establish ownership over domain names, with the ownership delegated by accredited companies called *registrars* that one can buy names from.

Buying a domain name is fairly common action - anyone who wants to set up a public website needs to do it - so there's a wide range of registrars out there that all try to make the process quick and painless even for non-technical people. We went with **[Domain.com](domain.com)** for the cheap, no-frills package, registering `dummy-site-for-dns-ddos-testing.com` for one year for around $20. For anyone trying to reuse this work, any name and registrar should work just as well so long as the registrar lets you set custom nameservers.

#### Static IP

Now that we had the right to run the authoritative nameserver for our domain, we next needed to specify where the nameserver is actually located.

Self-hosting means we'd just list our own IP address, but the problem with that is that the IP addresses on our devices are constantly changing. When we connect to a network, we get one assigned to us through Dynamic Host Configuration Protocol (DHCP), and we lose it if we disconnect or switch networks, or it might just expire and refresh after a while.

Since changes to the public DNS registry take time to propogate, we can't just keep changing the listed address on-the-fly, and it's not like we'd want to do that, either, considering how inconvenient it'd be. Instead, we needed a static IP address - one that doesn't change.

We decided that our best option for getting one of those was through a VPN, since it would also allow us to share the IP address by sharing the account. We went with **[PureVPN](purevpn.com)** since they allow port forwarding, which is what allows incoming traffic to actually interact with things running on the IP address. A one-year subscription with the Dedicated IP add-on costs about $100.

Enabling port forwarding on the static IP is fairly easy. PureVPN has a settings panel that lets us just list the ports we want to enable, and all we had to do was type in "53, 80" (53 for DNS, 80 for web). 

From there, if you run PureVPN with the Dedicated IP connection then anything listening on those ports will be accessible at the address. 

![](https://cdn.discordapp.com/attachments/1019067030663598080/1179195162702905394/image.png?ex=6578e613&is=65667113&hm=9f61b56c52182f1645707101d0111b6f6bf5cb98ccd5688113954d26d52d0745&)

One will need to connect to the Dedicated IP when running the DNS server in order for the attacks and evaluation to work. 

As for hooking the address up to the domain registrar: on the Domain.com control panel, the Private Nameservers tab in the DNS & Nameservers subpanel lets us register DNS servers that point to IP addresses that we specify. We listed `ns1.dummy-site-for-dns-ddos-testing.com` and `ns2.dummy-site-for-dns-ddos-testing.com` as both pointing to our static IP. The `ns2` may or may not have been needed, but we included it there just in case, since some registrars require redundant nameservers. 

There's a switch that allows us use the private nameservers as our site's main nameservers, so that resolvers will be directed to them. When we tried flipping it, though, it kept telling us that our nameservers were invalid. We tried again after actually running a DNS server instance on the static IP, but it still gave us the same error. Some time later, we ended up getting it to work after going on the main Nameservers tab, clicking the Add Nameserver button, and listing the `ns1` and `ns2` domains. This is what it looked like in the end:

![](https://cdn.discordapp.com/attachments/1019067030663598080/1173449843746803732/image.png?ex=6563ff54&is=65518a54&hm=b877b435b274b236c5c54632ca6ab757ea81ae99c0add90f077bbcab82f70079&)
![](https://cdn.discordapp.com/attachments/1019067030663598080/1173449946192674896/image.png?ex=6563ff6c&is=65518a6c&hm=d150cd60fd0afc4fea7c7ab157afa4b73fc3beb95226c4481663da596345236e&)

This part only needs to be done once for a given domain name and static IP.

### Running the Servers

The server scripts and configurations are generally intended to work for Linux. We used a Ubuntu VM in our own testing.

The `defense` directory contains everything needed for running both the servers and the countermeasures. We'll get to the latter later.

The web server is the easy one and it's just there for illustrative purposes so we'll get it out of the way first. Just enter `sudo ./runWebServer.sh`, and it'll start listening on port 80. With the way the DNS servers are configured, the returned IP address for the website is the same static IP being used for hosting the DNS server itself, so the combined setup needs both servers to be running on the same host to work. When running the actual attacks and evaluation, the web server doesn't need to be running since none of the automated traffic interacts with ti.

The manual Python implementation of the DNS server is located in `dnsServerV1.py`. Tweaks to the configuration can be done by changing parts of the code. Running the script on its own won't work since port 53 is normally occupied by another process on Linux, so I added a shell script that will free up the port (`free_port_53_linux.sh`), as well as another one that can undo those changes (`restore_port_53_linux.sh`) after you're done running the server. All of these will need to be run with `sudo` since the Python script needs priveliged access for port 53 and since the shell scripts mess with the `/etc/systemd` configuration. 

To summarize the sequence:

1. `sudo ./free_port_53_linux.sh`
2. `sudo python3 dnsServerV1.py`
3. (Do stuff with the server)
4. (Ctrl+C to terminate the server)
5. `sudo ./restore_port_53_linux.sh` (Optional)

For the BIND DNS server, BIND can be installed onto Linux by typing `sudo apt get install bind9` into the terminal. With the software already implementing the server functionality, our own code artifacts just consist of the server configuration (located in the `bindConfig` subdirectory), a script to run a server instance using our config (`runBind.sh`), and a script to stop the running instance (`stopBind.sh` - the server runs in the background, so Ctrl+C won't work). Both of these scripts need to be run with `sudo` as well since they touch `/etc/bind` in order to copy our server's config files into it and later clean them out of it. For some reason, the script to free up port 53 doesn't need to be run for BIND, and it'll just claim the port on its own.

To summarize the sequence:

1. `sudo apt get install bind9` (Once)
2. `sudo ./runBind.sh`
3. (Do stuff with the server)
4. `sudo ./stopBind.sh`

### Running the Attacks

As we mentioned a few sections ago, DNS-based denial of service attacks include symmetrical DNS floods as well as asymmetrical DNS amplification attacks, but the former is much more widely used due to being both easier to implement and harder to counter. As thus, we limit our focus to them for this project.

The `attack` directory contains the two variants we implemented, both as Python scripts:

- `directFlood.py` finds the IP addresses of the site's nameservers (we only had one, but wanted to keep this generalizable) and proceeds to send as many DNS packets to them as possible.

- `launderingFlood.py` sends queries to public DNS resolvers instead of directly contacting the authoritative nameservers, cycling through [a list](#https://github.com/trickest/resolvers/blob/main/resolvers.txt) of 30,000 that we found online and downloaded into the directory. To get around caching, it generates a random subdomain for each set of requests to ensure that each resolver has a cache miss.

Either of these can be run by simply typing `python3 <filename>` into the terminal while the DNS server is running somewhere and is connected to the static IP. The attacks won't terminate on their own, and will need to be stopped by pressing Ctrl+C. The final terminal printout for both will show the number and rate of packets sent, to help add context to other measurements.

We caution that, given the deliberate lack of constraints on the rate at which packets are being sent, both of these scripts will generate a very large volume of network traffic, likely reaching several hundred MB within seconds. **These attacks should only be launched while both the attacking host and the server host are connected to personal networks or hotspots. Don't get yourself blacklisted or arrested for doing this to a public or organizational network.** If you go for the hotspot option, make sure you have an unlimited plan with your cellular provider so that this doesn't take up all your data.

If the server setup is changed, the scripts only need to be changed if a different domain name is being used, or, in the case of the direct flood, if different nameserver subdomains are being used.

### Running the Evaluation

#### Data Collection

The intended effect of denial of service is, of course, to prevent or hamper people from accessing certain services. As such, the key metric we try to gauge is the performance and availability of our DNS server from the perspective of normal users.

The `evaluation` directory contains a Python script called `serverEval.py` that we use for generating our measurement data. It works by sending DNS queries for our domain at controlled intervals and seeing how long it takes to get a response for each one, if the server responds at all.

For simplicity and reliability in detecting responses, each query is done by calling the `dig` utility, as opposed to directly opening a new socket. By default, `dig` will time out after 15 seconds, a setting we left in place since it seemed like a reasonable threshold. Multithreading is used so that a new request can be sent before the previous ones receive responses, for a more realistic simulation of user traffic.

To also simulate the fact that traffic will be coming from a range of sources (something that becomes a significant factor when caching is enabled) we directed the queries to various public resolvers, using [a shorter list](https://github.com/trickest/resolvers/blob/main/resolvers.txt) of 30 well-known, trusted ones to guarantee reliable responses in the absence of the attack taking place.

Factors that can be adjusted in the code include: 

- The domain name 
- The interval between requests
- The list of resolvers being used
- The number of requests to make before terminating
- The command-line arguments being given to `dig`.

Running the script is about as simple as one would expect: `python3 serverEval.py`. To save the results directly to a file instead of printing to the console, the optional `--file=<file path>` argument can be added at the end. The DNS server will need to be running somewhere and will need to be connected to the static IP in order for this to work properly, of course.

After a response is received for the last request, the program will terminate and give a printout of the results in JSON as an array of objects, each with the following properties:

- **"index"** (number) - Just the index of the given request, starting from 0. Redundant but helps with readability
- **"resolver"** (string) - The IP address of the DNS resolver that the request was initial sent to
- **"start_time"** (number) - The time at which the request was sent, relative to the start of the evaluation, given in milliseconds
- **"end_time"** (number) - The time at which the response was received, relative to the start of the evaluation, given in milliseconds
- **"response_time"** (number) - Equal to start_time - end_time, is redundant but helps with readability
- **"success"** (boolean) - True if an actual response was received, false if `dig` timed out

The JSON files in the `results` directory all contain data generated in this format.

Eyeballing the JSON can be somewhat helpful - at the very least, one can tell the difference between a working server and a struggling or disabled one - but overall it's very verbose and can be tough for humans to parse, even with the redundant fields. Fortunately, it doesn't take much to extract macro-level insights and generate nice-looking charts.

#### Analysis and Visualization

After getting the measurement data into a JSON file, entering `python3 dataVisualization.py --file=<file path> --desc=<optional description>` into the terminal from the `evaluation` directory will display a range bar chart showing the start and stop times of each requests, with successful requests shaded green while timeouts are shaded red. This was intended to resemble the network waterfall charts present in Chrome and Firefox's dev tools panels, with the inclusion of start times adding context and making it easier to put the lengths of response times from different trials into perspective. If a description is given, it will be displayed next to the chart title in parentheses.

The request success rate and the average response time for successful requests, arguably the two most informative numbers we have for determining overall service availability, are listed in the corner of the chart. If the text overlaps with the bars or with the chart border, the chart window can be expanded to separate them.

Information about which resolvers were used for which requests wasn't included since there didn't seem to be a good way to show it without cluttering the charts, and we figured that ideally it shouldn't significantly affect the results much anyway.

The charts we use for showing the results of our own trials later in this README were generated using this program. One can reproduce them by running it on the provided data files, or modify the chart appearance or include additional charts by modifying the provided code.

### Running the Countermeasures

Implementations for countermeasures are located back in the `defense` directory, and are currently designed to operated on the same host as the server. We have two, with one intended for each attack.

#### Rate-Limiting

For the Direct Flood, we found that BIND has a built-in feature that lets us limit the number of requests from the same client that the server will process in a given window.

The `named.conf.options` file in the `bindConfig` subdirectory contains a few commented-out lines specifying the rate-limiting configuration. To enable rate-limiting, uncomment them and rerun the BIND server.

![](https://cdn.discordapp.com/attachments/1019067030663598080/1179553460899811378/image.png?ex=657a33c4&is=6567bec4&hm=2bc1e4e5eb7324ccb9b5fe9dc7ed62f15db8c8ff7e2b4594cb055b70e7234aac&)

The limit can be made stricter or looser by adjusting these numbers. To disable rate-limiting, comment the lines out again and rerun the server again.

Given that BIND already has it, we didn't bother reimplementing it in the Python server since people in the real world would just use BIND. Later trials only test the BIND server since there turned out to be no upside to using the Python server.

#### Subdomain Filter

For the Laundering Attack, we figured that we could take advantage of the need for randomly-generated subdomains to implement a packet filter that drops requests to any subdomains that aren't provided by the server.

Our implementation is done using Linux's [netfilter](https://www.netfilter.org/) framework, which lets us use hooks in the kernel to register callbacks that inspect incoming packets and can choose to drop or accept them before they reach the user applications. The code and the makefile are present in the `subdomain_filter` subdirectory where one can modify them.

Back at the top level of the `defense` directory, entering `./runSubdomainFilter.sh` will handle the whole process of compiling the code and inserting it into the kernel, enabling the filter. To disable the filter, enter `./stopSubdomainFilter.sh`, which will remove the code from the kernel and also clean up the compiled artifacts. The server doesn't need to be rerun since the filter runs separately from it.


## Trials and Measurements

### 11/06/2023

We ran our first tests right after writing the attacks, with no countermeasures in place. Everything was done on Thomas's laptop, with the server and VPN running inside a Ubuntu VM while the attack and evaluation scripts were running outside of it (yes, attack and evaluation traffic were coming from the same host here, something we changed for the final trial). The device was connected to this internet through a cellular hotspot.

The baseline measurements for the server implementations, with no attacks running, are shown below. The evaluation script was configured to send a request every 100ms and to cycle through the resolver list 3 times, for a total of 90 requests.

![](https://cdn.discordapp.com/attachments/1019067030663598080/1175613500849147954/image.png?ex=656bde64&is=65596964&hm=681c4745b41806fecd17ef490ac0f1fbd2e2e9869af55d508539c84e74f91fbb&)
![](https://cdn.discordapp.com/attachments/1019067030663598080/1175612271905484880/image.png?ex=656bdd3f&is=6559683f&hm=43c17cde645433ec11062d98d6260b8e1f73f8552440d20cc454a3ea0df46f04&)

We can see that both servers work, with not much of a significant difference between the two. The one failed request on the Python server was probably just a random fluke caused by underlying network conditions since the other two requests on the same resolver went through.

Next, we ran the direct flood on both implementations, waiting about 10 seconds between the start of the attack and the start of the evaluation. In both cases, the attack sent out around 80K packets per second. Its effects can be seen below:

![](https://cdn.discordapp.com/attachments/1019067030663598080/1175612919673782333/image.png?ex=656bddd9&is=655968d9&hm=6e83ddd8bf7f430d157c42c5b2647f4499747db76b7c894aeb23dba3cb513efc&)
![](https://cdn.discordapp.com/attachments/1019067030663598080/1175612507059126353/image.png?ex=656bdd77&is=65596877&hm=2197e6cd3c87a5f80cc566b122fce319399b2ad86b464e97646f26eb0c45e747&)

In both cases, the attacks significantly hamper access to the server without completely cutting it off. The BIND server performs somewhat better, as one would expect from industrial-quality software compared to an amateur Python script, though it's not that big of a difference.

Next we ran the DNS laundering attacks in the same manner. About 45K packets per second were sent out in both cases.

![](https://cdn.discordapp.com/attachments/1019067030663598080/1175614207408996352/image.png?ex=656bdf0c&is=65596a0c&hm=a0d8752b6a7ef11198023464b82d1da054056a93450f4cb0d342236044c2d1c7&)
![](https://cdn.discordapp.com/attachments/1019067030663598080/1175614862915805307/image.png?ex=656bdfa9&is=65596aa9&hm=f5aa2f4b6ae6dea97ff99af414e14412a5acd07fe1c0677604e2be8ed3f21953&)

This was somewhat surprising. Even though the initial traffic volume was much smaller, this attack was able to completely disable both servers. 

The two possible explanations we thought of were that the resolvers could be putting additional overhead on our servers by sending multiple packets for each query (which still doesn't seem like it could have that much of an effect), or that the resolvers were rate-limiting the evaluation traffic since it was coming from the same source as the attack traffic (though 45K requests per second on 30K resolvers means each one was barely being queried more than once a second anyway). We'd have to do more trials to find out.

As a sanity check, we ran one more set of tests with the DNS laundering, in which we started the evaluation first and then started the attacks about a second later.

![](https://cdn.discordapp.com/attachments/1019067030663598080/1175615731283525724/image.png?ex=656be078&is=65596b78&hm=12b2664876e036821415d5ef9bceed1a5f620a69169cdbaa91591e44c48b8d45&)
![](https://cdn.discordapp.com/attachments/1019067030663598080/1175615453171810455/image.png?ex=656be035&is=65596b35&hm=4422c5382546495218a400c0739c6d84c997fcdabe127ba152e38c9553a564a0&)

As we can see in both cases, there's an almost-instant transition from normal operation to complete denial of service.

### 11/26/2023 

Shortly after we managed to implement both countermeasures, we got the group together on a call to collect some more measurements, this time with proper separation of traffic sources.

The attack traffic was running off of Benjamin's laptop, connected to a personal Wi-Fi network, while the defense setup (including the VPN connection) was running on Thomas's laptop inside a VM and the evaluation traffic was running outside of the VM, with the device connected to a cellular hotspot. We would've liked to separate the three components onto three separate devices, but Prashanth's internet connection dropped so we had to make do with two.

The evaluation script was configured to cycle through the resolver list only once this time around, since we would be turning caching on later, for a total of 30 requests. The interval between requests was increased from 100ms to 250ms to offset the shortening.

We focused on testing the BIND server since it was the only one with a rate-limiting implementation and since it was the option that most people in the real world would use. We basically only implemented the Python server in case we needed more control over the server code, and it turned out that we didn't. Still, though, we collected another set of results with it to get another reference point.

![](https://cdn.discordapp.com/attachments/1144353133129125931/1178485080205824020/image.png?ex=657650c2&is=6563dbc2&hm=c7d1fc3f5560069638d1b29207517edb3e9e65e5c2f72eaba06642a57c151f3f&)
![](https://cdn.discordapp.com/attachments/1144353133129125931/1178485614316896306/image.png?ex=65765141&is=6563dc41&hm=f4419ac2d83bc79a132fedfc540714d4d796d5ae79b9299c97110d7b7c4fdebe&)
![](https://cdn.discordapp.com/attachments/1144353133129125931/1178485829308530778/image.png?ex=65765174&is=6563dc74&hm=254f8fda59e8efe0143590406af4a257223b98fdf8cdf90e434cb034037c4da0&)

For the baseline and direct flood, this basically replicated the result of the first trial, but the measurements for the laundering attack already show a clear divergence. The evaluation traffic can actually get through this time, which seems to support the hypothesis that the resolvers were rate-limiting it the last time around, when it was coming from the same place as the attack traffic.

Initial attack volume averaged out to around 100K packets per second for the direct flood and 180K per second for the laundering flood, numbers that remained within a consistent range for each subsequent trial. The fact that Benjamin's laptop would generate far more packets for the laundering flood than the direct flood, the opposite of what had been the case on Thomas's laptop, is interesting, though we're not sure what the cause would be.

Next, we moved on to collecting measurements for the BIND server with no countermeasures. Starting from here, we also began taking screenshots of the network monitor on the server host showing the volume of traffic sent and received, which gives a picture of what's happening to the packets on the server-side. These are listed under the corresponding request timings chart.

![](https://cdn.discordapp.com/attachments/1144353133129125931/1178486983593570334/image.png?ex=65765288&is=6563dd88&hm=22ebd76763cf0d933bcb75b9d87c8b832cf779040f4285441184d5e28533de88&)

![](https://cdn.discordapp.com/attachments/1144353133129125931/1178486360470982726/image.png?ex=657651f3&is=6563dcf3&hm=4e454023e22cb3bd9dce5ec4a95cf626e1f11463bfd1324383412b6fe5934d05&)
![](https://cdn.discordapp.com/attachments/1144353133129125931/1178466153413222480/image.png?ex=65763f21&is=6563ca21&hm=13d092f215c7bb653ef303092e7105f0303d46580634bd3a92eeb6cc97ec7245&)

![](https://cdn.discordapp.com/attachments/1144353133129125931/1178486068828442664/image.png?ex=657651ae&is=6563dcae&hm=d9f2e3fda8eca878488f8293c3cfc1007b3421d877e47d0ab2ef48c23942adb1&)
![](https://cdn.discordapp.com/attachments/1144353133129125931/1178466729312124949/image.png?ex=65763fab&is=6563caab&hm=2d77125929b912e19ed9d48666b7ab69df1f0999c7c329543e91c1aaf0bf47e8&)

Again, there's not much of a significant difference between the two implementations, at least not one big enough to not be attributable to fluctuations in network conditions. In general, the precise numbers can be finicky, and it's better to focus on the wider trends.

On the network monitor, we see the sent traffic approximately tracking with the received traffic, showing the baseline for what it looks like when the server attempts to respond to all of the packets it receives. With all of our attack sessions lasting between around 30 and 35 seconds, it's interesting to note how the traffic from the direct flood stops almost immediately while the traffic from the laundering attack keeps coming in, indicative of quirks in resolver behavior.

Next, we turned rate-limiting on:

![](https://cdn.discordapp.com/attachments/1144353133129125931/1178487408472363078/image.png?ex=657652ed&is=6563dded&hm=c9f873283d7476755a642af09ec3f4fd0dd106e9621dfd5eda4cd65933262ae0&)

![](https://cdn.discordapp.com/attachments/1144353133129125931/1178487743660163082/image.png?ex=6576533d&is=6563de3d&hm=f4f2d63ce132eba53c12a3e3c3109584e6864d14c10d01d9be01a83e242a8abd&)
![](https://cdn.discordapp.com/attachments/1144353133129125931/1178467634304532521/image.png?ex=65764082&is=6563cb82&hm=f19dd56d4a96de6b67608ba8c9504f526685ac0f09f8eadb7d13f485211c6eee&)

![](https://cdn.discordapp.com/attachments/1144353133129125931/1178487968487448636/image.png?ex=65765372&is=6563de72&hm=9772604a093c6c693a2eab4b4f67030e413abcc19ff2aab470a9abdf86caabd1&)
![](https://cdn.discordapp.com/attachments/1144353133129125931/1178468185008255088/image.png?ex=65764106&is=6563cc06&hm=7bc1d3dd04cb094e1d3bb4093d24669ec5180a1a500eac972701eed37a167065&)

Before the tests, we had figured that the rate-limiting would probably mostly neutralize the direct flood since everything in this version was coming from a single host, while the laundering attack would probably become much more crippling since the attack traffic would crowd out any evaluation traffic that uses the same resolvers. Neither such thing happens. Server availability holds up slightly better under the direct flood, but it's not a big difference. The laundering attack also gets slightly better, surprisingly, though it could very well be attributable to network conditions.

The network monitor screenshots are useful here in that they tell us that this isn't a case of us just forgetting to properly enable the countermeasure. With the direct flood, the sent traffic tracks to just over half of the received traffic now. Still, that's odd considering that we configured it to 5 packets per 5 seconds whereas the attack sent around 100,000 packets per second. Perhaps we still did something wrong, or perhaps the limits don't or can't get enforced that strictly beyond a certain point, or perhaps we misunderstood how the whole thing works.

Overall, though, it's somewhat encouraging that there was a slight improvement at all under the attacks and that the legitimate traffic wasn't noticeably impeded. It's not exactly a technical contribution on our part, since this is already a built-in option, but at least we now know how to address one of the problems we created here.

Next, we turned rate-limiting off and turned the subdomain filter on:

![](https://cdn.discordapp.com/attachments/1144353133129125931/1178489131941253201/image.png?ex=65765488&is=6563df88&hm=96ad7182af369b17306bc22ee34a8cc56545cda88995245c0ae3c78a5b029153&)

![](https://cdn.discordapp.com/attachments/1144353133129125931/1178488605124071544/image.png?ex=6576540a&is=6563df0a&hm=a14855553470dfa5a9612b93d3484fd45ced938d8e67c985381d6eac29d52ccd&)
![](https://cdn.discordapp.com/attachments/1144353133129125931/1178477672163196928/image.png?ex=657649dc&is=6563d4dc&hm=a84cc3bfb0b2fa921f92f8e5059793697e55e9057bbc1b1b293ade39f5c72377&)

![](https://cdn.discordapp.com/attachments/1144353133129125931/1178488349573513297/image.png?ex=657653cd&is=6563decd&hm=bc1dc3c2892faa826fbaeff4c11fd05e13394d56edb5b7a5b71f36a6dc43dd25&)
![](https://cdn.discordapp.com/attachments/1144353133129125931/1178478178591846490/image.png?ex=65764a54&is=6563d554&hm=9796039f22a5370146b96c7cdc2a63179c431d7a2024d2b5f91118908b38eb78&)

When writing the countermeasure, we knew that it would only work if the overhead of inspecting and dropping packets was lower than that of just letting the server respond as usual. Otherwise, the whole system would get overwhelmed just as easily. In practice, it got overwhelmed even more easily. Much more easily, in fact. We go from partial denial to near-full denial. These are almost comically bad results.

The network monitor shows that most of the traffic is indeed getting filtered out before the server tries responding to it, but of course the goal of defending against denial of service is not to reduce server load but to ensure continued user access. All we did was create a new bottleneck. The only good news is that it at least didn't also mess up the no-attack case.

In hindsight, we realized another clear flaw: if a resolver sends a packet and doesn't get a response, it doesn't have any way of knowing why or where the packet gets dropped, and it'd probably send another one. That's presumably why DNS timeouts seem so rare during our normal web browsing, even though DNS requests are transported over unreliable UDP packets. That would mean that this "countermeasure" is amplifying the attack it's supposed to be defending against. An affirmative "non-existent domain" response would let the resolver know not to try again, and perhaps we could've modified the code to send one, but we'd just be copying the normal server functionality at that point, and it's unlikely that any code we can write in the span of this project could run faster than software like BIND that's been getting improved and optimized for decades.

We didn't generate the timing charts until after we had run all of the trials, so we didn't realize just how badly the subdomain filter had failed until later. As such, we went forward with another set of measurements in which we turned caching on (TTL of 30 seconds) to deal with an issue we noticed in which resolvers don't just query the specified subdomain but also send requests to the ns1 and ns2 subdomains, which are valid and don't get filtered. We figured that caching would make it so that they would only look those up once.

![](https://cdn.discordapp.com/attachments/1144353133129125931/1178489399672061952/image.png?ex=657654c8&is=6563dfc8&hm=bc44ba526abb371f57b064a1c9db5e70d5013710f03a6aec85ac0e9b60ee8a17&)

![](https://cdn.discordapp.com/attachments/1144353133129125931/1178489700382687383/image.png?ex=6576550f&is=6563e00f&hm=1aba492fb90ecb8d128f63b61da65f532d7ec7501bc57be7c6a637685fad31d6&)
![](https://cdn.discordapp.com/attachments/1144353133129125931/1178480305816998031/image.png?ex=65764c50&is=6563d750&hm=8089d6e6cab0b1848835694dd482c00fc09855e4b0d26dd63d74fc41e1282656&)

![](https://cdn.discordapp.com/attachments/1144353133129125931/1178490197109911624/image.png?ex=65765586&is=6563e086&hm=9a80ab0b886b71943d0fb8d9740d17b3fe1ac8960e9dd0009554e0a706fb35df&)
![](https://cdn.discordapp.com/attachments/1144353133129125931/1178480866092134530/image.png?ex=65764cd5&is=6563d7d5&hm=805ad7b86a5394d29cf49c9311c4c06798e12723407e08f701c3680f3f562663&)

Once again, the laundering attack obliterates the system, and it doesn't even seem like there's much of a different in the amount of traffic going through. That massive surge in received packets near the end, which was probably a fluke, makes the rest of the graph hard to read.

What's surprising is that the direct flood has now gone back to only causing less than half of the legitimate requests to fail, even though there was nothing about the enablement of caching that would make it behave differently. We made sure to wait at least 30 seconds if not more between trials so that all existing cached answers for the evaluation resolvers would expire, and the respond times on the successful requests are too long to look like cache hits. 

This could suggest that the 90% fail rate on the direct flood in the previous trial was a fluke, and that the subdomain filter only really consistently makes things worse when dealing with the laundering attack. That would make sense, since intentionally dropping a packet seems like a more complex and expensive operation than letting one through as normal.

For the last set of trials, we turned the rate-limiting back on to test out defense in depth. Caching remained on.

![](https://cdn.discordapp.com/attachments/1144353133129125931/1178491029318541404/image.png?ex=6576564c&is=6563e14c&hm=ee858c5fb1972034a22bb31302edc48806449de5abe9f873db131e2ea70f852d&)

![](https://cdn.discordapp.com/attachments/1144353133129125931/1178490733150339202/image.png?ex=65765606&is=6563e106&hm=2d095fb1bf41639f3a5a6e1cf90419baeefa48a8d7824258af2278ddd7532c19&)
![](https://cdn.discordapp.com/attachments/1144353133129125931/1178482611052626000/image.png?ex=65764e75&is=6563d975&hm=0a9f3de3e6c91cee5c821c78051a6f12fdffd9cd5d2eacda2ae0559c65d8e144&)

![](https://cdn.discordapp.com/attachments/1144353133129125931/1178490509426171944/image.png?ex=657655d0&is=6563e0d0&hm=14aa6755d2f694c03a38b1e0dce1ce8f826be8a31bd80402bc0b28933f13e8d8&)
![](https://cdn.discordapp.com/attachments/1144353133129125931/1178483186448220200/image.png?ex=65764efe&is=6563d9fe&hm=43da29ff2528afa86e4ebf69f16f91548b7cba62b99146bedae8e1fe09cf5c54&)

We can see that the two defenses can work in conjunction to deflate traffic from both attacks without interfering with legitimate requests in the absence of attacks. But, of course, the caveat is that one of those defenses creates a bottleneck in its attempt to filter attack traffic, making the attack worse from the user's perspective, which is what actually matters. At least we have another data point showing that it's just the laundering attack and not the direct flood that triggers the bottleneck.

## Conclusions

### Lessons Learned

Denial of Service isn't exactly a novel problem, and at this point there's plenty of widely available protection options, either as part of cloud computing platforms like AWS or standalone services like those offered by Cloudflare. If one signs up for them, they typically won't have to worry about them being inadequate. The [largest DDoS attack](https://cloud.google.com/blog/products/identity-security/google-cloud-mitigated-largest-ddos-attack-peaking-above-398-million-rps) in history as of this writing was mitigated by Google Cloud in just two minutes. When face with the question of what our own technical contribution would be, we knew we could never beat the existing solutions in terms of general sophistication, so we wondered if we could go in the other direction and come up with simpler and easier-to-use solutions optimized for the specific case of protecting DNS servers, taking advantage of DNS's relative simplicity as a service.

Indeed, the fact that the any single client is unlikely to query the same authoritative DNS server very frequently (given caching) means that servers can be fairly strict about rate-limiting, but that already seems to be widely known, given how BIND has it as a built-in option.

When going beyond that and trying to implement defenses with our own custom code, we run into the fact that DNS's apparently simplicity is just an abstraction. It's still a protocol built on a stack of other protocols, with countless things going on under the hood that we barely understand. Most of the time, we don't have to worry about it, but it comes to bite us in cases like dealing with DoS, where every bit of overhead matters. The established players know the optimal ways to deal with large volumes of traffic, hence why the built-in rate-limiting did alright, but our "simple solution" takes a naive approach, and it completely falls apart once you put a bit of load on it.

It's not even just a networking thing. When it comes to computing in general, something that runs fast when done once isn't always still going to seem fast if you have to do it over 100,000 times a second on a single host. A better solution would try to look at the big picture instead of just going through one packet at a time. With the amount of effort it would take to implement something like that, one would most likely be better off either buying protection or learning how to deploy one of the open source options.

There's the moral of the story: that DoS protection is an area where you don't reinvent the wheel. By all means, you can try, but you won't get very far unless you really know what you're doing.

### Unanswered Questions and Future Work

It may seem like we hit a dead end, but the rate-limiting still worked somewhat and we still came out with this neat testing setup.

If we were to keep working on this, the first order of business would probably be to run some more trials to determine the amount of variability we can expect in our measurements and get a clearer picture of what's actually going on. 

It'd also be nice to have some way of seeing how much of the request slowdown is coming from the server being overloaded versus how much is coming from network bottlenecks or other environment-dependent noise. This would probably require more sophisticated instrumentation.

For rate-limiting, we only tried one configuration, with 5 packets per 5 seconds, so there's still the question of how the system would perform under different settings, or if there are different or more effective ways of enforcing the limit.

Getting some data on how existing solutions stack up under our measurement system could also be interesting, though it'd probably only be feasible to test the open-source options since sending DoS traffic to third-party services could carry risks.

In that vein, we keep just saying "Denial of Service" or "DoS" instead of "DDoS" because the other D stands for "distributed", and we don't have any distribution. If one could get their hands on the right resources, though, then they could change that for their own trials. All it would take is having each distributed host run its own copy of the attack script. One could also try testing out a distributed version of the server setup by running multiple instances and listing each one on the domain registrar.

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
- [BIND](https://www.isc.org/bind/)
- [Trickest's list of trusted public DNS resolvers](https://github.com/trickest/resolvers/blob/main/resolvers-trusted.txt)
- [Trickest's full list of public DNS resolvers](https://github.com/trickest/resolvers/blob/main/resolvers.txt)
- [netfilter](https://www.netfilter.org/)
- Google: [Google mitigated the largest DDoS attack to date, peaking above 398 million rps](https://cloud.google.com/blog/products/identity-security/google-cloud-mitigated-largest-ddos-attack-peaking-above-398-million-rps)