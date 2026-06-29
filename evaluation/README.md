# Evaluation of the Impact on IPv6 Packet Forwarding

We evaluate the imapct on IPv6 packet forwarding performance for both the encapsulating and transit nodes.

## Encapsulating node

First, we measure the imapct depending on the AEAD scheme with the maximum PTO data (i.e., 976 bytes).

Results are in [encap/encap_max_size/](./encap/encap_max_size/).
The plot is [encap_976B.pdf](./../plots/encap_976B.pdf).

Second, we measure the impact depending on the size of PTO data, ranging from 32 bytes (minimum) to 976 bytes (maximum).

Results are in [encap/encap_var_size/](./encap/encap_var_size/).
The plot is [encap_pto_size.pdf](./../plots/encap_pto_size.pdf).

## Transit node

First, we measure the impact of the number of IOAM data fields being protected, ranging from 4 bytes (minimum) to 48 bytes (maximum in current Linux implementation), using AES-GCM.

Results are in [transit/transit_aes/](./transit/transit_aes/).
The plot is [transit_data_fields.pdf](./../plots/transit_data_fields.pdf).

Second, we measure the impact of the chosen AEAD scheme to protect the maximum number of IOAM data fields (48 bytes in current Linux implementation).

Results are in [transit/transit_max_size/](./transit/transit_max_size/).
The plot is [transit_48B.pdf](./../plots/transit_48B.pdf).
