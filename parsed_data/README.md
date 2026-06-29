# Parsed Data for the Evaluation

We evaluate the imapct on IPv6 packet forwarding performance for both the encapsulating and transit nodes.

## Encapsulating node

First, we measure the imapct depending on the AEAD scheme with the maximum PTO data (i.e., 976 bytes).

Raw data is in [encap_max_size/](./../evaluation/encap/encap_max_size/).
The parsed data is [encap_976B.csv](./encap_976B.csv).

Second, we measure the impact depending on the size of PTO data, ranging from 32 bytes (minimum) to 976 bytes (maximum).

Raw data is in [encap_var_size/](./../evaluation/encap/encap_var_size/).
The parsed data is [encap_pto_size.csv](./encap_pto_size.csv).

## Transit node

First, we measure the impact of the number of IOAM data fields being protected, ranging from 4 bytes (minimum) to 48 bytes (maximum in current Linux implementation), using AES-GCM.

Raw data is in [transit_aes/](./../evaluation/transit/transit_aes/).
The parsed data is [transit_data_fields.csv](./transit_data_fields.csv).

Second, we measure the impact of the chosen AEAD scheme to protect the maximum number of IOAM data fields (48 bytes in current Linux implementation).

Raw data is in [transit_max_size/](./../evaluation/transit/transit_max_size/).
The parsed data is [transit_48B.csv](./transit_48B.csv).
