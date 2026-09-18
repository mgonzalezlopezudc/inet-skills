# Reviewed document identities

| Source filename | Document ID | Kind |
| --- | --- | --- |
| `80211ax-2024.pdf` | `ieee80211-2024` | IEEE Std 802.11-2024 base standard; the filename is misleading |
| `80211be-2024.pdf` | `ieee80211be-2024` | Amendment to IEEE Std 802.11-2024 |
| `802154-2024.pdf` | `ieee802154-2024` | IEEE Std 802.15.4-2024 base standard |

The processor ingests only reviewed profiles, not every PDF in the directory. A ready corpus
does not imply an unregistered PDF was indexed. Check the requested document in `status`.

## IEEE 802.11

Select the base or amendment explicitly. Do not infer an amendment’s replacement text from
the base alone, or treat identically numbered clauses in separate documents as interchangeable.

## IEEE 802.15.4

Use `--document ieee802154-2024` on searches and structural lookups. The 2024 edition is a
reference edition, not evidence that an existing model claims that edition or every PHY it defines.
Older model citations require an explicit edition mapping; unavailable older texts remain a gap.
Confirm the applicable PHY and MAC operating mode before deriving a check.

Representative navigation starts at clause 3.1 (definitions), clause 6 (MAC), clause 7
(MAC formats), clause 13 (O-QPSK PHY), and clause 16 (HRP UWB PHY). Verify the exact
subclause and its source pages before citing a requirement.

For example:

```sh
./bin/inet_process_standards get clause 6.3.2.1 --document ieee802154-2024 --output <corpus-output> --json
./bin/inet_process_standards get figure 6-2 --document ieee802154-2024 --output <corpus-output> --json
./bin/inet_process_standards define association --document ieee802154-2024 --output <corpus-output> --json
```

Figure 6-2's extracted node locates its caption on physical PDF page 64. Inspect that PDF
page for the flowchart arrows and decisions; the caption alone is not the algorithm.
