#!/bin/bash

# Simple script to configure IOAM on the DUT
#
# Usage: sudo ./setup_ioam.sh <encap|forward|decap>

set -euo pipefail

DIR="$(dirname "$(readlink -f "$0")")"
. "$DIR/utils.sh"

ensure_root

check_interfaces_names

usage () {
	echo "Usage: $0 <encap|forward|decap>"
}

if [ $# -ne 1 ]; then
	usage
	exit
fi

# Delete existing configuration
ip -6 r d cd00::/64 2> /dev/null || true
ip ioam namespace del 123 2> /dev/null || true
ip ioam schema del 777 2> /dev/null || true

case $1 in
    "encap")
	echo "Configuring as encapsulating node..."
	sysctl -w \
	  net.ipv6.conf.all.forwarding=1 \
	  net.ipv6.ioam6_id=1 \
	  net.ipv6.conf.all.ioam6_id=1 \
	  net.ipv6.conf.default.ioam6_id=1 \
	  net.ipv6.conf.all.ioam6_enabled=1 \
	  net.ipv6.conf.default.ioam6_enabled=1 \
	  net.ipv6.conf.in.ioam6_enabled=1 \
	  net.ipv6.conf.in.ioam6_id=11 \
	  net.ipv6.conf.out.ioam6_enabled=1 \
	  net.ipv6.conf.out.ioam6_id=12

	echo "Configuring route..."
	ip -6 r a cd00::/64 encap ioam6 trace prealloc type 0x80000 ns 123 size 8 via db02::2 dev out
    	;;
    "forward")
	echo "Configuring as forwarding node..."
	sysctl -w \
	  net.ipv6.conf.all.forwarding=1 \
	  net.ipv6.ioam6_id=2 \
	  net.ipv6.conf.all.ioam6_id=2 \
	  net.ipv6.conf.default.ioam6_id=2 \
	  net.ipv6.conf.all.ioam6_enabled=1 \
	  net.ipv6.conf.default.ioam6_enabled=1 \
	  net.ipv6.conf.in.ioam6_enabled=1 \
	  net.ipv6.conf.in.ioam6_id=21 \
	  net.ipv6.conf.out.ioam6_enabled=1 \
	  net.ipv6.conf.out.ioam6_id=22

	echo "Configuring namespace..."
	ip ioam namespace add 123

	echo "Configuring route..."
	ip -6 r a cd00::/64 via db02::2 dev out
    	;;
    "decap")
	;;
    *)
	usage
esac

success "DONE"
