yum install -y epel-release
yum install -y clamav
yum install -y clamd
/etc/init.d/clamd start
freshclam
