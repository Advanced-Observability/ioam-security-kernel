"""
Usage on the DUT: sudo python3 test_transit.py

Tests as an IOAM transit node with(out) the proposed security solution.
"""

import os, sys

# IOAM schema command
DEL_SCHEMA = "sudo ip ioam schema del 21"

# IOAM namespace command
ADD_NAMESPACE = "sudo ip ioam namespace add 123"

# IP route commands
REMOVE_IP_ROUTE = "sudo ip -6 r d cd00::/64"
ADD_IP_ROUTE = "sudo ip -6 r a cd00::/64 via db02::2 dev out"

# exec formatted command on remote
EXEC_CMD_REMOTE = "ssh -i id_ed25519 -oStrictHostKeyChecking=no X@Y {}"

# path to python script to generate the packets
RUN_PROFILE_FILE = "/opt/trex/vX/automation/trex_control_plane/interactive/trex/examples/stl/test_profile.py"

# packet names
PACKET_NAMES = ["INLINE_4B", "INLINE_8B", "INLINE_16B", "INLINE_24B", "INLINE_32B", "INLINE_48B"]

# frequencies of IOAM - 0.001%, 0.01%, 0.1%, 1%, 5%, 10%, 25%, 50%, 100%
NB_MTUS = [99999, 9999, 999, 99, 19, 9, 3, 1, 0]
NB_IOAMS = [1, 1, 1, 1, 1, 1, 1, 1, 1]

# name of network interfaces
IFACES = ["in", "out"]

# Number of test runs
NB_ITERS = 20

def check_root():
    return os.geteuid() == 0

def switch_security(enable : bool = False, chacha : bool = False):
    """Enable or not IOAM security on all interfaces in `IFACES`."""
    for iface in IFACES:
        os.system(f"sysctl -q -w net.ipv6.conf.{iface}.ioam6_sec_enabled={1 if enable else 0}")
        os.system(f"sysctl -q -w net.ipv6.conf.{iface}.ioam6_sec_chacha={1 if chacha else 0}")

def test_option(name: str, nbMTU: int, nbIOAM: int, secEnable: bool, chacha: bool):
    """Test with given packet `name`."""

    print(f"\n\n~ Test {os.path.basename(__file__)} with pkt {name}, security = {secEnable}, chacha = {chacha}, and frequencies {nbMTU}/{nbIOAM} ~\n")

    switch_security(secEnable, chacha)

    # launch trex on remote machine
    data = build_extra_data(name, nbMTU, nbIOAM)
    if os.system(EXEC_CMD_REMOTE.format(f"python3 {RUN_PROFILE_FILE} -n {NB_ITERS} -e {data}")) != 0:
        print(f"Error while launching TRex with packet {name} with nbMTU = {nbMTU} and nbIOAM = {nbIOAM} and sec = {secEnable}")
        sys.exit(-2)

    # save data on remote machine
    if os.system(EXEC_CMD_REMOTE.format(f"mv stats.csv sec_{secEnable}_chacha_{chacha}_packet_{name}_{nbMTU}_{nbIOAM}.csv")) != 0:
        print(f"Error while saving the stats on the remote machine for packet {name} with nbMTU = {nbMTU} and nbIOAM = {nbIOAM} and sec = {secEnable} and chacha = {chacha}")
        sys.exit(-3)

def build_extra_data(ioamPacketName : str, nbMTU : int, nbIOAM : int):
    if ioamPacketName == "":
        raise RuntimeError("ioam packet name cannot be empty")
    if nbMTU < 0 or nbIOAM < 0:
        raise RuntimeError("nbMTU and nbIOAM cannot be < 0")
    if nbMTU == 0 and nbIOAM == 0:
        raise RuntimeError("Cannot have both nbMTU and nbIOAM set to 0")

    extra = ""
    extra+=f"ioamPacketName={ioamPacketName},"
    extra+=f"nbMTU={nbMTU},"
    extra+=f"nbIOAM={nbIOAM}"

    return extra

if __name__ == "__main__":
    if not check_root():
        print("Must be running as root")
        sys.exit(-1)

    if not len(NB_IOAMS) == len(NB_MTUS):
        raise RuntimeError("Cannot have NB_IOAMS and NB_MTUS with different length")

    # config DUT
    os.system(DEL_SCHEMA)
    os.system(ADD_NAMESPACE)
    os.system(REMOVE_IP_ROUTE)
    os.system(ADD_IP_ROUTE)

    # Measuring various data fields insertion
    for pkt in PACKET_NAMES:
        for i in range(len(NB_MTUS)):
            test_option(pkt, NB_MTUS[i], NB_IOAMS[i], True, False)

    # Measuring maximum number of data fields (48B) with 3 approaches
    for i in range(len(NB_MTUS)):
        test_option(PACKET_NAMES[len(PACKET_NAMES)-1], NB_MTUS[i], NB_IOAMS[i], True, False)
        test_option(PACKET_NAMES[len(PACKET_NAMES)-1], NB_MTUS[i], NB_IOAMS[i], True, True)
        test_option(PACKET_NAMES[len(PACKET_NAMES)-1], NB_MTUS[i], NB_IOAMS[i], False, False)

    sys.exit(0)
