#!/bin/bash

# Script to test IOAM with fake networks created using network namespaces

# Remove namespaces
cleanup()
{
	nb=$(ip netns list | wc -l)
	if [[ $nb -eq 0 ]]; then
		echo -e "No namespaces to clean\n"
	else
  		ip netns delete encap || true
  		ip netns delete transit || true
  		ip netns delete decap || true
		echo -e "Done cleaning.\n"
	fi
}

echo "Cleaning everything up..."
cleanup

