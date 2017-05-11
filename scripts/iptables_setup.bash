#!/bin/bash
#
# iptables example configuration script
#
# Flush all current rules from iptables
#
 iptables -F
#
# Allow connections on tcp port 8080, 8000 
#
 iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
 iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
 iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
#
# Set default policies for INPUT, FORWARD and OUTPUT chains
#
 iptables -P INPUT DROP
 iptables -P FORWARD DROP
 iptables -P OUTPUT ACCEPT
#
# Set access for localhost
#
 iptables -A INPUT -i lo -j ACCEPT
#
# Accept packets belonging to established and related connections
#
 iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
#
# Save settings
#
 /sbin/service iptables save
#
# List rules
#
 iptables -L -v

