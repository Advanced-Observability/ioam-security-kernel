#!/bin/bash

# Functions to help with the configuration of the machines

warning () {
    echo -e "\033[93m[WARNING] $1\033[0m"
}

error () {
    echo -e "\033[91m[ERROR] $1\033[0m"
}

success () {
    echo -e "\033[92m$1\033[0m"
}

die () {
    >&2 error "$1"
    exit 1
}

ensure_root () {
    [ "$(id -u)" = "0" ] || die "$0 must be run as root."
}

# Get version of TRex installed on server
find_trex_version () {
    echo $(find /opt -iname "*trex*" | grep -E -o "v[0-9]\.[0-9]+" | uniq)
}

# Get driver of given interface
get_nic_driver () {
    INTERFACE=$1

    if ! command -v ethtool >/dev/null 2>&1; then
        die "Install ethtool (sudo apt install ethtool)!"
    fi

    echo $(ethtool -i "$INTERFACE" | grep driver | sed 's/driver://g')
}

# Get PCI address of given interface
get_pci_addr_nic () {
    INTERFACE=$1

    if ! command -v ethtool >/dev/null 2>&1; then
        die "Install ethtool (sudo apt install ethtool)!"
    fi

    echo $(ethtool -i "$INTERFACE" | grep bus-info | sed 's/bus-info: 0000://g')
}

# Get maximum ring buffer size of given interface
get_nic_max_ring_size () {
    INTERFACE=$1

    echo $(ethtool -g "$INTERFACE" | grep -A 4 -i "maximum" | grep RX: | sed 's/RX://g' | xargs)
}

# Check whether generic receive offload is available on the given interface
# 0 => GRO available. Else, GRO *not* available
check_nic_gro_available () {
    INTERFACE=$1

    ! sudo ethtool -k "$INTERFACE" | grep generic-receive-offload | grep fixed
}

# Check if interfaces are named "in" and "out"
check_interfaces_names () {
    if ! ip addr | grep -q "in:"; then
        die "Missing \"in\" interface!"
    fi

    if ! ip addr | grep -q "out:"; then
        die "Missing \"out\" interface!"
    fi

    return 0
}

# Clear IP information associated with INTERFACE.
cleanup_interface () {
    INTERFACE="$1"

    # Remove existing addresses from interface and routing table
    ip addr flush "$INTERFACE"
    ip -6 addr flush "$INTERFACE"
    # Clear ARP cache
    ip neigh flush dev "$INTERFACE"
    ip -6 neigh flush dev "$INTERFACE"

    ip link set "$INTERFACE" down
}

# Configure IPv6 address of given interface
setup_interface_ipv6 () {
    IP="$1"
    PREFIX="$2"
    INTERFACE="$3"

    ip link set "$INTERFACE" up
    ip -6 addr add "$IP/$PREFIX" dev "$INTERFACE"
}

# Configure IPv4 address of given interface
setup_interface_ipv4 () {
    IP="$1"
    PREFIX="$2"
    INTERFACE="$3"

    ip link set "$INTERFACE" up
    ip addr add "$IP/$PREFIX" dev "$INTERFACE"
}

# Set the CPU frequency scaling director to the given mode. Typically,
# performance is used during experiments, and powersave the remainder of the
# time.
set_scaling_governor () {
    MODE="$1"

    # check if cpufreq is available
    if ! test -f /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor; then
        warning "Scaling governor *not* modifiable!"
        return
    fi

    # check if performance is available
    if ! grep -q -i "$MODE" /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors; then
        echo "$MODE governor is *not* available!"
        exit 2
    fi

    # setting governor on all cores
    for governor in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        echo "$MODE" > "$governor"
    done
}

# Tweak various network-related kernel settings. The value can be overriden by
# adding a corresponding variable in the environment before calling this
# function.
# Note: rx-gro-hw not supported by our NICs (Intel XL710 and ConnectX-6)
maximize_performance () {
    # Modify governor
    set_scaling_governor performance

    # Disable checksumming
    echo "Disabling checksum..."
    ethtool -K out rx off tx off
    ethtool -K in rx off tx off

    # Change ring buffer size
    echo "Changing ring buffer..."
    ethtool -G out rx "$(get_nic_max_ring_size in)" tx "$(get_nic_max_ring_size in)"
    ethtool -G in rx "$(get_nic_max_ring_size in)" tx "$(get_nic_max_ring_size in)"

    # limit forwarding to 1 cpu core on input interface
    echo "Changing forwarding hash..."
    ethtool -X in equal 1

    # Increase MTU size
    echo "Increasing MTU..."
    ip link set dev in mtu 9000
    ip link set dev out mtu 9000

    # Increase queue len
    echo "Increasing txqueuelen..."
    ip link set dev in txqueuelen 20000
    ip link set dev out txqueuelen 20000

    # Enable GRO if available
    echo "Checking and enabling GRO..."
    if check_nic_gro_available in; then
        ethtool -K in gro on
    fi
    if check_nic_gro_available out; then
        ethtool -K out gro on
    fi

    # Interrupt coalescence
    echo "Enabling interrupt coalescence..."
    ethtool -C in adaptive-rx on adaptive-tx on
    ethtool -C out adaptive-rx on adaptive-tx on

    # Enable pause
    echo "Enabling pause..."
    ethtool -A in rx on tx on
    ethtool -A out rx on tx on

    # Increase netdev kernel parameters
    echo "Modifying netdev parameters..."
    sysctl -w net.core.netdev_budget=600
    sysctl -w net.core.netdev_budget_usecs=40000
    sysctl -w net.core.netdev_max_backlog=250000
    #sysctl -w net.core.netdev_backlog=250000

    # Pooling
    echo "Enabling busy poll..."
    sysctl -w net.core.busy_poll=1

    # Increase window size
    echo "Modifying window size..."
    NET_CORE_RMEM_MAX=536870912
    NET_CORE_WMEM_MAX=536870912
    sysctl -q -w \
        net.core.rmem_max="$NET_CORE_RMEM_MAX" \
        net.core.wmem_max="$NET_CORE_WMEM_MAX" \
	    net.core.rmem_default="$NET_CORE_RMEM_MAX" \
	    net.core.wmem_default="$NET_CORE_WMEM_MAX"

    # Queue management algorithm
    echo "Modifying qdisc..."
    NET_CORE_DEFAULT_QDISC="fq_codel"
    sysctl -q -w net.core.default_qdisc="$NET_CORE_DEFAULT_QDISC"
}

# Restore default value
unset_network_settings () {
    sysctl -q -w \
	    net.core.rmem_max="212992" \
	    net.core.wmem_max="212992" \
	    net.core.rmem_default="212992" \
	    net.core.wmem_default="212992" \
	    net.core.default_qdisc="pfifo_fast"
}
