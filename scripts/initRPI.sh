#!/bin/bash

# This is a initialize script of Raspberry PI for PiCAM

[ -z "$IP_ETH" ] && IP_ETH="192.168.0.201"
[ -z "$IP_WLAN" ] && IP_WLAN="192.168.0.202"
[ -z "$IP_ROUTER" ] && IP_ROUTER="192.168.0.1"
[ -z "$IP_NAME" ] && IP_NAME="8.8.8.8 168.126.63.1"
__FILE__=$(readlink -f $0)
__MARK__=/var/tmp/initRPI

fInit_bash() {
	PATH_USER=`cat /etc/passwd | grep ":x:1000:1000" | awk -F: '{ print $6 }'`
	BASH_ALIASES=$PATH_USER/.bash_aliases
	cat > $BASH_ALIASES <<EOF
FYEL="\[\033[33m\]"
FGRN="\[\033[32m\]"
RS="\[\033[0m\]"

PS1="( \${FGRN}[\u \${FYEL}\# \t] \w \${RS}) \n$ "
PS2='more input >'

export VISUAL=vim
export EDITOR="\$VISUAL"

alias ll='ls -al'
EOF
}

fInit_network() {
	if [ "$1" == "static" ] ; then
		NET_CONF="/etc/dhcpcd.conf"
		netInit=`cat $NET_CONF | grep "static ip_address="`
		if [ -z "$netInit" ] ; then
			cat >> $NET_CONF <<EOF
interface eth0
static ip_address=$IP_ETH

interface wlan0
static ip_address=$IP_WLAN

static routers=$IP_ROUTER
static domain_name_servers=$IP_NAME
EOF
		fi
	fi
}

fInstall_dpkg() {
	apt-get update
	for pkg in build-essential iperf
	do
		apt-get install $pkg
	done
}

fCheck() {
	if [ -e "$__MARK__" ] ; then
		md5sum -c $__MARK__ > /dev/null 2>&1
		if [ "$?" -eq "0" ] ; then
			echo "Already Executed."
			exit
		fi
	fi
}
fDone() {
	md5sum $__FILE__ > $__MARK__
}

# main
[ "$EUID" -ne 0 ] && echo "Please run as root !!" && exit

fCheck
fInit_bash
fInit_network static 
fInstall_dpkg
fDone
