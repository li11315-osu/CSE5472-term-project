# Move the original config file back in place and stop the daemon
sudo mv "/etc/bind/named.conf.local.original" "/etc/bind/named.conf.local"
sudo mv "/etc/bind/named.conf.options.original" "/etc/bind/named.conf.options"
sudo rm /etc/bind/zonefile
sudo service named stop

