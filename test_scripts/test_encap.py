"""
Usage on the DUT: sudo python3 test_encap.py

Tests the encapsulation of IOAM PTO in inline mode with
the proposed security solution.
"""

import os, sys

# IP IOAM commands
DEL_SCHEMA = "sudo ip ioam schema del 21"

# IP route commands
REMOVE_IP_ROUTE = "sudo ip -6 r d cd00::/64 via db02::2"
INLINE_IP_ROUTE = "sudo ip -6 r a cd00::/64 encap ioam6 freq {}/{} mode inline trace prealloc type 0x800000 ns 123 size {} via db02::2 dev out"

# path to python script to generate the packets
RUN_PROFILE_FILE = "/opt/trex/vX/automation/trex_control_plane/interactive/trex/examples/stl/test_profile.py"

# exec formatted command on remote
EXEC_CMD_REMOTE = "ssh -i id_ed25519 -oStrictHostKeyChecking=no X@Y {}"

# sizes of PTO
SIZES = [8, 40, 72, 104, 136, 168, 200, 232, 244]

# frequencies of IOAM - 0.001%, 0.01%, 0.1%, 1%, 5%, 10%, 25%, 50%, 100%
NB_MTUS = [99999, 9999, 999, 99, 19, 9, 3, 1, 0]
NB_IOAMS = [1, 1, 1, 1, 1, 1, 1, 1, 1]

# Number of test runs
NB_ITERS = 20

def check_root():
    return os.geteuid() == 0

def switch_security(enable : bool = False, chacha : bool = False):
    """Enable or not IOAM security."""

    os.system(f"sysctl -q -w net.ipv6.ioam6_encap_security={1 if enable else 0}")
    os.system(f"sysctl -q -w net.ipv6.ioam6_encap_security_chacha={1 if chacha else 0}")

def run_tests_encapsulation(ptoSize: int, nbMTU : int, nbIOAM : int, enable: bool, chacha: bool):
    switch_security(enable, chacha)

    print(f"\n\n~ Running {os.path.basename(__file__)} inline with PTO {ptoSize}B and frequencies {nbMTU}/{nbIOAM} and security {enable} and chacha {chacha} ~\n")

    os.system(REMOVE_IP_ROUTE)
    if os.system(INLINE_IP_ROUTE.format(nbIOAM, nbIOAM+nbMTU, ptoSize)):
        print(f"Could not add route with PTO of size {ptoSize} in inline mode")
        sys.exit(-1)

    # launch trex on remote machine
    # name of packet does not matter because it will be replaced by another one in profile.py
    data = build_extra_data("INLINE_4B", nbMTU, nbIOAM, True, ptoSize)
    if os.system(EXEC_CMD_REMOTE.format(f"python3 {RUN_PROFILE_FILE} -n {NB_ITERS} -e {data}")) != 0:
        print(f"Error while launching TRex with PTO size {ptoSize}")
        sys.exit(-2)

    # save data on remote machine
    destFilename = f"encap_inline_size_{ptoSize}_security_{enable}_chacha_{chacha}_mtu_{nbMTU}_ioam_{nbIOAM}_stats.csv"
    if os.system(EXEC_CMD_REMOTE.format(f"mv stats.csv {destFilename}")) != 0:
        print(f"Error while saving the stats on the remote machine for inline size {ptoSize}")
        sys.exit(-3)

def build_extra_data(ioamPacketName : str, nbMTU : int, nbIOAM : int, insertionPTO : bool, ptoSize: int):
    if ioamPacketName == "":
        raise RuntimeError("Name of IOAM packet cannot be empty")
    if nbMTU < 0 or nbIOAM < 0:
        raise RuntimeError("nbMTU and nbIOAM cannot be < 0")
    if nbMTU == 0 and nbIOAM == 0:
        raise RuntimeError("Cannot have both nbMTU and nbIOAM set to 0")
    if ptoSize < 0:
        raise RuntimeError("ptoSize cannot be < 0")
    if not insertionPTO and ptoSize > 0:
        raise RuntimeError("Insertion of PTO on DUT is not enabled")

    extra = ""
    extra+=f"ioamPacketName={ioamPacketName},"
    extra+=f"nbMTU={nbMTU},"
    extra+=f"nbIOAM={nbIOAM},"
    extra+=f"insertionPTO={insertionPTO},"
    extra+=f"ptoSize={ptoSize}"

    return extra

if __name__ == "__main__":
    if not check_root():
        print("Must be running as root")
        sys.exit(-1)

    if not len(NB_IOAMS) == len(NB_MTUS):
        raise RuntimeError("Cannot have NB_IOAMS and NB_MTUS with different length")

    # config DUT
    print("Removing IOAM schema for OSS")
    os.system(DEL_SCHEMA)

    # Measuring various sizes of IOAM PTO
    for size in SIZES:
        for i in range(len(NB_MTUS)):
            run_tests_encapsulation(size, NB_MTUS[i], NB_IOAMS[i], enable=True, chacha=False)

    # Measuring max IOAM PTO size with 3 approaches (no security, AES-GCM, ChaCha20-Poly1305)
    for i in range(len(NB_MTUS)):
        run_tests_encapsulation(244, NB_MTUS[i], NB_IOAMS[i], enable=False, chacha=False)
        run_tests_encapsulation(244, NB_MTUS[i], NB_IOAMS[i], enable=True, chacha=False)
        run_tests_encapsulation(244, NB_MTUS[i], NB_IOAMS[i], enable=True, chacha=True)

    sys.exit(0)
