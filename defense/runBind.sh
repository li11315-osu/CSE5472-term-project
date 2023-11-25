# Move the custom config file and zonefile  in this directory 
# into the default directory
# and run the BIND daemon

if ! [ -e /etc/bind/named.conf.local.original ] # Avoid overwriting original on repeat calls
then
	sudo mv "/etc/bind/named.conf.local" "/etc/bind/named.conf.local.original"
fi
sudo cp "./bindConfig/named.conf.local" "/etc/bind/named.conf.local"

if ! [ -e /etc/bind/named.conf.options.original ]
then
	sudo mv "/etc/bind/named.conf.options" "/etc/bind/named.conf.options.original"
fi
sudo cp "./bindConfig/named.conf.options" "/etc/bind/named.conf.options"

sudo cp ./bindConfig/zonefile /etc/bind/zonefile

sudo chmod 644 /etc/bind/named.conf # Set permissions as needed
sudo chmod 644 /etc/bind/zonefile

sudo service named restart

