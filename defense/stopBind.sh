# Move the original config file back in place and stop the daemon
sudo mv "/etc/bind/named.conf.local.original" "/etc/bind/named.conf.local"
sudo rm /etc/bind/zonefile
sudo service named stop

