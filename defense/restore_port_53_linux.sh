# This script reverts the changes made by free_port_53_linux.sh
# Like with that one, I copied the commands from StackExchange
# All it does is delete the config file we added and then restart systemd-resolved

sudo rm /etc/systemd/resolved.conf.d/10-make-dns-work.conf
sudo systemctl restart systemd-resolved

