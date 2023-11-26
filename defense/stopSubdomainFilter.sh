# Removes the subdomain filter code from the kernel and cleans up the compiled artifacts
# Adapted from https://stackoverflow.com/questions/29553990/print-tcp-packet-data

cd subdomain_filter
sudo rmmod subdomain_filter
make clean
cd ..

