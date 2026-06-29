# Local Evaluation

The following 2 scripts allow to test IOAM on a single machine using Linux namespaces.

It will create an IOAM domain with 3 nodes: encapsulating, transit, and decapsulating nodes.

[setup_test_net.sh](./setup_test_net.sh) creates the 3 namespaces, while [teardown_test_net.sh](./teardown_test_net.sh) deletes the namespaces.
