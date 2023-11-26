# Compiles the subdomain filter code and loads it into the kernel
# Adapted from https://stackoverflow.com/questions/29553990/print-tcp-packet-data

cd subdomain_filter
sudo apt-get install sparse # Install dependencies that may not be initially present
make
sudo insmod subdomain_filter.ko
cd ..

