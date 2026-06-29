# Test Scripts

The scripts in this directory automate the testing of the proposed security solution.

## TRex

The following scripts need to be used with Cisco's [TRex](https://trex-tgn.cisco.com/):
- [profile.py](./profile.py) contains the packets send by TRex;
- [test_profile.py](./test_profile.py) configures TRex to send the packets in [profile.py](./profile.py).

## DUT

The following scripts need to be used on the DUT:
- [test_encap.py](./test_encap.py) to automate the tests when the DUT is acting as the encapsulating node;
- [test_transit.py](./test_transit.py) to automate the tests when the DUT is acting as the transit node.

## Both machines

The scripts in the [configuration/](./configuration/) directory need to be used on both machines to configure the servers.
[setup_ioam.sh](./configuration/setup_ioam.sh) must only be used on the DUT.

For instance, on the DUT:
```shell
sudo ip link set dev ens6f0np0 name in
sudo ip link set dev ens6f1np1 name out
sudo ./setup_ipv4.sh dut 3c:fd:fe:9e:5b:61 3c:fd:fe:9e:5b:60
sudo ./setup_ipv6.sh dut 3c:fd:fe:9e:5b:61 3c:fd:fe:9e:5b:60
sudo ./setup_ioam.sh forward
```
