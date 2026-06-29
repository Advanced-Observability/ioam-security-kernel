#!/bin/bash

# Simple script to configure IPv4 on the machines
#
# Usage: sudo ./setup_ipv4.sh <trex|dut> <remote_in_mac> <remote_out_mac>
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
	die "Usage: ./setup_ipv4.sh <trex|dut> <remote_in_mac> <remote_out_mac>"
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
		echo "$(get_nic_driver in)" "$(get_pci_addr_nic in)" "$(get_pci_addr_nic out)"
		./dpdk_nic_bind.py -b "$(get_nic_driver in)" "$(get_pci_addr_nic in)" "$(get_pci_addr_nic out)"

		echo "Setting IP addresses..."
		setup_interface_ipv4 11.11.11.2 16 out
		setup_interface_ipv4 12.12.12.2 16 in

		echo "Setting neighbors..."
		ip neigh add 11.11.11.1 lladdr "$REMOTE_IN_MAC" nud permanent dev out
		ip neigh add 12.12.12.1 lladdr "$REMOTE_OUT_MAC" nud permanent dev in

		echo "Maximizing network performance..."
		maximize_performance
		;;
	"dut")
		echo "Configuring as DUT..."

		echo "Enabling forwarding..."
		sysctl -w net.ipv4.conf.all.forwarding=1

		echo "Setting IP addresses..."
		setup_interface_ipv4 11.11.11.1 16 in
		setup_interface_ipv4 12.12.12.1 16 out

		echo "Setting neighbors..."
		ip neigh add 11.11.11.2 lladdr "$REMOTE_OUT_MAC" nud permanent dev in
		ip neigh add 12.12.12.2 lladdr "$REMOTE_IN_MAC" nud permanent dev out

		echo "Configuring routes..."
		ip route add 48.0.0.0/8 via 12.12.12.2
		ip route add 16.0.0.0/8 via 11.11.11.2

		echo "Maximizing performance..."
		maximize_performance
		;;
	*)
		usage
esac

success "DONE"
