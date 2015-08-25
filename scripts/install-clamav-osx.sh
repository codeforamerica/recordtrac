brew install clamav
cp /usr/local/etc/clamav/freshclam.conf.sample /usr/local/etc/clamav/freshclam.conf
sed -i -e "s/^Example/#Example/" /usr/local/etc/clamav/freshclam.conf
cp /usr/local/etc/clamav/clamd.conf.sample /usr/local/etc/clamav/clamd.conf
sed -i -e "s/^Example/#Example/" /usr/local/etc/clamav/clamd.conf
sed -i -e "s/^#TCPSocket/TCPSocket/" /usr/local/etc/clamav/clamd.conf
freshclam
