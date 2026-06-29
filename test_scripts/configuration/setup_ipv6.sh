#!/bin/bash

# Simple script to configure IPv6 on the machines
#
# Usage: sudo ./setup_ipv6.sh <trex|dut> <remote_in_mac> <remote_out_mac>
#
# Parameters:
# 	- <trex|dut> depending on which machine the script is being run
# 	- <remote_in_mac> MAC address of remote IN interface
#	- <remote_out_mac> MAC address of remote OUT interface

set -euo pipefail

DIR="$(dirname "$(readlink -f "$0")")"
. "$DIR/utils.sh"

ensure_root

check_interfaces_names

usage () {
	die "Usage: ./setup_ipv6.sh <trex|dut> <remote_in_mac> <remote_out_mac>"
}

if [ $# -ne 3 ]; then
	usage
fi

MODE=$1
REMOTE_IN_MAC=$2
REMOTE_OUT_MAC=$3

case $MODE in
	"trex")
		echo "Configuring as TRex server..."
		cd /opt/trex/"$(find_trex_version)"

		echo "Binding network interfaces..."
        ./dpdk_nic_bind.py -b "$(get_nic_driver in)" "$(get_pci_addr_nic in)" "$(get_pci_addr_nic out)"

		echo "Setting IP addresses..."
		setup_interface_ipv6 db01::2 64 out
		setup_interface_ipv6 db02::2 64 in

		echo "Setting neighbors..."
		ip -6 neigh add db01::1 lladdr "$REMOTE_IN_MAC" nud permanent dev out
		ip -6 neigh add db02::1 lladdr "$REMOTE_OUT_MAC" nud permanent dev in

		echo "Maximizing network performance..."
		maximize_performance
		;;
	"dut")
		echo "Configuring as DUT..."

		echo "Enabling forwarding..."
		sysctl -w net.ipv6.conf.all.forwarding=1

		echo "Setting IP addresses..."
		setup_interface_ipv6 db01::1 64 in
		setup_interface_ipv6 db02::1 64 out

		echo "Setting neighbors..."
		ip -6 neigh add db01::2 lladdr "$REMOTE_OUT_MAC" nud permanent dev in
		ip -6 neigh add db02::2 lladdr "$REMOTE_IN_MAC" nud permanent dev out

		echo "Configuring routes..."
		ip -6 route add cd00::1 via db02::2
		ip -6 route add ab00::1 via db01::2

		echo "Maximizing performance..."
		maximize_performance
		;;
	*)
		usage
esac

success "DONE"
