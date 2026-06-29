# Securing IOAM Data

"Securing IOAM in the Linux Kernel: Toward Trustworthy In Situ Network Telemetry"

This repository contains the source code, configuration files, measurement data, and scripts for the paper.

## Directories

- [baseline/](./baseline/) contains the measurement data and plots for evaluating the baseline (i.e., the number of packets per second that can be forwarded before any packet loss occurs);
- [evaluation/](./evaluation/) contains the measurement data for both the encapsulating and transit nodes. [parsed_data/](./parsed_data/) contains the parsed data. [plots/](./plots) contains the plots.
- [local_test/](./local_test/) contains scripts for testing IOAM locally using Linux namespaces;
- [patches/](./patches/) contains the patches for `iproute2` and kernel-space implementations;
- [test_scripts/](./test_scripts/) contains the test scripts, including scripts to configure both the server generating the packets and the DUT.
