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
3. [Trials and Measurements](#trials-and-measurements)
    1. [11/06/2023](#11062023)
4. [Conclusions](#conclusions)
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

TODO: Add PureVPN screenshot

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

TODO: Implement and document countermeasures


## Trials and Measurements

### 11/06/2023

We ran our first tests right after writing the attacks, with no countermeasures in place. Everything was done on Thomas's laptop, with the server and VPN running inside a Ubuntu VM while the attack and evaluation scripts were running outside of it (yes, attack and evaluation traffic were coming from the same host here, something we changed on later trials). The device was connected to this internet through a cellular hotspot.

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

TODO: More trials, with countermeasures

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
- [BIND](https://www.isc.org/bind/)
- [Trickest's list of trusted public DNS resolvers](https://github.com/trickest/resolvers/blob/main/resolvers-trusted.txt)
- [Trickest's full list of public DNS resolvers](https://github.com/trickest/resolvers/blob/main/resolvers.txt)
- Fortinet: [DDoS Attack Mitigation Technologies Demystified](https://www.fortinet.com/content/dam/fortinet/assets/white-papers/DDoS-Attack-Mitigation-Demystified.pdf)
