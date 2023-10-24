# An Exploration of DNS Denial of Service

*CSE 5472: Information Security Projects, The Ohio State University*

*Term Project, Autumn 2023*

*Group: Thomas Li, Prasanth Umapathy, Benjamin Wenger*

*Topic: DNS Security*

In this project, we examine the level of threat posed by various forms of denial of service (DoS) and distributed denial of service (DDoS) attacks directed towards or propogated through Domain Name System (DNS) infrastructure, as well as the effectiveness and practicality of countermeasures that we attempted to devise for them. 

This repository contains the code artifacts, documentation, and instructions needed for running our experiments, with files organized into three categories:

- **Defense**

    - The code and configuration information needed for self-hosting an authoritative DNS server, which we made internet-accessible through the registration of a domain name and a static IP address in order to fully reflect the behavior of regular real-world nameservers. The external setup steps do not involve any of our own code artifacts, but instructions are included in this README to allow their replication. 

    - A one-line script to self-host a web server for which our DNS server resolves the domain name into the corresponding IP address. When btoh servers are running, any internet user can access our dummy website by looking up the domain name, representing arguably the most simple and common use case for DNS.

    - The countermeasures we implemented to prevent our attacks from disrupting the functionality of our servers. Each of these are described in detail later in this README.

- **Attack**

    - Programs to execute the attacks that we implemented, which each have the goal of disabling proper usage of our DNS server. Each of these are described in detail later in this README.

- **Evaluation**

    - Programs to quantify the functionality of our server setup and the effects of our attacks and countermeasures on it by simulating "normal" server traffic coming from spoofed users attempting to access the site through its domain name, with measurements taken for the speed and success status of each user's request sequence. Sample results are shown later in this README alongside the attacks and countermeasures that produced them.

    - Programs to process and visualize the raw measurements

We tried to make the code artifacts as modular and interchangeable as possible to make this work extensible. All that is necessary for the attack and evaluation programs to run is for the DNS server and web server to be running and to be accessible through the chosen domain name using public internet-based DNS resolution. Granted, the registered domain name and static IP needed for consistent internet accessibility both involve small monthly fees, though we considered that to be worth it for the improved convenience and realisticness.

In the next section, we will briefly discuss of the background and general real-world relevance of DNS denial-of-service threats, after which we will move on to the detailed instructions for properly configuring and running our setup with full internet accessibility and for executing the programs present in this repository. The bulk of this README will discuss the attacks and corresponding countermeasures that we implemented, with analysis of their measured effectiveness and their real-world applicability and prevalence. The closing sections will discuss our overall takeaways and insights from this work, the extent of its usefulness in the real world, and potential improvements and expansions.

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

### DNS and Denial of Service


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

