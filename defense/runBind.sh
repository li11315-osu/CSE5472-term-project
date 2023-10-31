# Move the custom config file and zonefile  in this directory 
# into the default directory
# and run the BIND daemon
sudo mv "/etc/bind/named.conf.local" "/etc/bind/named.conf.local.original"
sudo cp "./bindConfig/named.conf.local" "/etc/bind/named.conf.local"
sudo cp ./bindConfig/zonefile /etc/bind/zonefile
sudo chmod 644 /etc/bind/named.conf # Set permissions as needed
sudo chmod 644 /etc/bind/zonefile
sudo service named restart

