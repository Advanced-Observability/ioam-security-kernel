# Evaluation of the baseline

Evaluate the number of MTU-sized IPv6 packets per second the DUT can forward before occurring any loss.

First, we measure the packet drop rate when sending traffic between 100,000 pps and 1 million pps, using increments of 100,000 pps.

The results are [baseline_broad.csv](./baseline_broad.csv) and [drop_broad.pdf](./drop_broad.pdf).

Based on the first experiment, we conclude that the baseline lies between 900,000 pps and 1 million pps.

We did a second measurement between 900,000 pps and 1 million pps, using increments of 10,000 pps.

The results are [baseline_precise.csv](./baseline_precise.csv) and [drop_precise.pdf](./drop_precise.pdf).
