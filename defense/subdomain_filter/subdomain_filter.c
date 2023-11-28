/* Code mainly adapted from https://stackoverflow.com/questions/29553990/print-tcp-packet-data */
/* Modified to handle UDP rather than TCP, and interpret payload as DNS packet */
/* Parts also adapted from https://levelup.gitconnected.com/write-a-linux-firewall-from-scratch-based-on-netfilter-462013202686 */

#include <linux/module.h>
#include <linux/netfilter.h>
#include <linux/netfilter_ipv4.h>
#include <linux/ip.h>
#include <linux/udp.h>

#define DNS_PORT 53
#define UDP_HEADER_LEN 8 /* In bytes */
#define DNS_HEADER_LEN 12 /* In bytes */

#define NUM_VALID_SUBDOMAINS 4
static const char * valid_subdomains[NUM_VALID_SUBDOMAINS] = {
	"www",
	"ns1",
	"ns2",
	"dummy-site-for-dns-ddos-testing", /* For case of no subdomain given, main domain is first domain segment */
};
static const size_t valid_subdomain_lens[NUM_VALID_SUBDOMAINS] = { /* List these here instead of using strlen so as to save time */
	3,
	3,
	3,
	31
}; 

static struct nf_hook_ops nfho;

static unsigned int subdomain_filter_hook_func(
		void *priv,
		struct sk_buff *skb,
		const struct nf_hook_state *state
		) {
	struct iphdr *iph; /* IPv4 header */
	struct udphdr *udph; /* UDP header */
	u16 sport, dport; /* Source and destination ports */
	u32 saddr, daddr; /* Source and destination addresses */
	unsigned char *user_data; /* UDP data begin pointer */
	unsigned char *tail; /* UDP data end pointer */
	unsigned char *it; /* UDP data iterator */

	/* Info about queried subdomain */
	size_t subdomain_len;
	const char* subdomain;

	/* Skip empty packets */
	if (!skb)
		return NF_ACCEPT;

	iph = ip_hdr(skb); /* Get IP header */

	/* Skip non-UDP packets */
	if (iph->protocol != IPPROTO_UDP)
		return NF_ACCEPT;

	udph = udp_hdr(skb); /* Get UDP header */

	/* Convert network endianness to host endianness */
	saddr = ntohl(iph->saddr);
	daddr = ntohl(iph->daddr);
	sport = ntohs(udph->source);
	dport = ntohs(udph->dest);

	/* Only watch DNS packets */
	if (dport != DNS_PORT)
		return NF_ACCEPT;

	/* Calculate pointers for begin and end of DNS packet data */
	/* Skip past DNS header and go to question section */
	user_data = (unsigned char *)((unsigned char *) udph + UDP_HEADER_LEN + DNS_HEADER_LEN);
	tail = skb_tail_pointer(skb);

	/* Debug printouts */

	/* Request source */
	pr_debug("subdomain filter: received DNS query\n");
	printk("IP addr %u, port %u\n", saddr, sport);

	/* Question section payload, with one line per byte */
	/* pr_debug("subdomain_filter: request question section:\n");
	for (it = user_data; it != tail; ++it) {
		char c = *(char *)it;

		if (c == '\0')
			break;

		printk("%c", c);
	}
	printk("\n\n"); */

	/* Question section payload, single line */
	/* pr_debug("subdomain_filter: request question section:\n");
	printk("%s\n", user_data); */

	/* This is the part that does the filtering - it's also basically the only thing here that I wrote myself instead of copying and slightly modifying */

	/* First byte of question section tells us the length of the first domain segment */
	/* Subsequent bytes are contents of segment */
	subdomain_len = (size_t) *user_data;
	subdomain = user_data + 1;
	/* pr_debug("subdomain_filter: Examining subdomain of DNS query\n");
	printk("First domain segment has length %li\n", subdomain_len); */
	for (int subdomain_index = 0; subdomain_index < NUM_VALID_SUBDOMAINS; ++subdomain_index) {
		/* printk("Comparing to %s...\n", valid_subdomains[subdomain_index]); */
		if (subdomain_len == valid_subdomain_lens[subdomain_index] 
			&& strncasecmp( /* Case-insensitive since some resolvers randomize case */
				subdomain,
				valid_subdomains[subdomain_index], 
				subdomain_len) == 0
		) {
			/* printk("Matches %s, accepting packet\n\n", valid_subdomains[subdomain_index]); */
			return NF_ACCEPT;
		}
	}	

	/* printk("Doesn't match any valid options, dropping packet\n\n"); */
	return NF_DROP;
}

static int __init subdomain_filter_init(void) {
	int res;

	nfho.hook = (nf_hookfn *)subdomain_filter_hook_func; /* hook function */
	nfho.hooknum = NF_INET_PRE_ROUTING; /* received packets */
	nfho.pf = PF_INET; /* IPv4 */
	nfho.priority = NF_IP_PRI_FIRST; /* max hook priority */

	res = nf_register_net_hook(&init_net, &nfho);
	if (res < 0) {
		pr_err("subdomain_filter: error in nf_register_hook()\n");
		return res;
	}

	pr_debug("subdomain_filter: loaded\n");
	return 0;
}

static void __exit subdomain_filter_exit(void) {
	nf_unregister_net_hook(&init_net, &nfho);
	pr_debug("subdomain_filter: unloaded\n");
}

module_init(subdomain_filter_init);
module_exit(subdomain_filter_exit);

MODULE_AUTHOR("Thomas Li");
MODULE_DESCRIPTION("Module to filter DNS traffic based on subdomain to counteract DNS Laundering attacks, written for a class project at OSU");
MODULE_LICENSE("GPL");

