apt-get install clamav-daemon
sed -i -e "s/^Example/#Example/" /etc/clamav/freshclam.conf
sed -i -e "s/^Example/#Example/" /etc/clamav/clamd.conf
sed -i -e "s/^#TCPSocket/TCPSocket/" /etc/clamav/clamd.conf
/etc/init.d/clamd start
freshclam
