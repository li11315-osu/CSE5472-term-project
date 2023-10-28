# This script makes systemd-resolved stop listening on port 53, freeing it up so that we can run our own DNS server
# I didn't come up with stuff, of course - I just copied the commands I saw on aStackExchange answer
# https://unix.stackexchange.com/a/637521

[ -d /etc/systemd/resolved.conf.d ] || sudo  mkdir -p /etc/systemd/resolved.conf.d # Create the config directory if it's not already there

printf "%s\n%s\n" '[Resolve]' 'DNSStubListener=no' | sudo tee /etc/systemd/resolved.conf.d/10-make-dns-work.conf # Add new partial config file that specifies that stub listener, which currently occupies port 53, should be disabled

sudo systemctl restart systemd-resolved # Restart systemd-resolved to make new config apply 

