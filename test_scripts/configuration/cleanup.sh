#!/bin/bash

# Clean the machines after usage
#
# Usage: sudo ./cleanup.sh
#

set -euo pipefail

DIR="$(dirname "$(readlink -f "$0")")"
. "$DIR/utils.sh"

ensure_root

check_interfaces_names

echo "Modifying governor..."
set_scaling_governor powersave

echo "Flushing interfaces configuration..."
cleanup_interface in
cleanup_interface out

echo "Restoring basic network kernel parameters..."
unset_network_settings

echo "Reverting NIC config..."
ethtool -K in rx on tx on
ethtool -K out rx on tx on
ethtool -G in rx 512 tx 512
ethtool -G out rx 512 tx 512
# reset packet forwarding to all cpu cores
ethtool -X in default

echo "Disabling forwarding..."
sysctl -w net.ipv4.conf.all.forwarding=0
sysctl -w net.ipv6.conf.all.forwarding=0

echo "Restoring all kernel parameters..."
sysctl -p

success "DONE"
