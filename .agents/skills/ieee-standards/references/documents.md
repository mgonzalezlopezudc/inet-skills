# Reviewed document identities

| Source filename | Document ID | Kind |
| --- | --- | --- |
| `80211-2016.pdf` | `ieee80211-2016` | IEEE Std 802.11-2016 base standard |
| `80211ax-2024.pdf` | `ieee80211-2024` | IEEE Std 802.11-2024 base standard; the filename is misleading |
| `80211be-2024.pdf` | `ieee80211be-2024` | Amendment to IEEE Std 802.11-2024 |
| `802154-2024.pdf` | `ieee802154-2024` | IEEE Std 802.15.4-2024 base standard |

The processor ingests only reviewed profiles, not every PDF in the directory. A ready corpus does not imply an unregistered PDF was indexed. Check the requested document in `status`.

## IEEE 802.11

Select the base or amendment explicitly. Do not infer an amendment’s replacement text from the base alone, or treat identically numbered clauses in separate documents as interchangeable.

Use `--document ieee80211-2016` for the 2016 edition. The 2016 and 2024 editions are separate base standards. The 802.11be-2024 amendment applies to the 2024 base standard only. A clause number alone does not establish the same content across editions.

The build command replaces the corpus at its output path. Omit `--pdf` to include all reviewed PDFs present in the source directory. Use a separate output directory for a build that selects only one PDF. Relative `--pdf` paths start at the current directory, not at `--standards-dir`.

In the 2016 edition, clause 10.24 contains Block Ack, while clause 10.25 contains No Ack. The 2024 edition places Block Ack in clause 10.25. Use the document ID to select the required edition:

```sh
./bin/inet_process_standards get clause 10.24.2 --document ieee80211-2016 --output <corpus-output> --json
./bin/inet_process_standards define "access point (AP)" --document ieee80211-2016 --output <corpus-output> --json
```

The 2016 corpus tests check definitions on physical PDF page 129, Block Ack on pages 1416–1419, HT on page 2335, and VHT on page 2498. The tests also check Table 9-45 on page 729 and Figure 10-17 on page 1328. These checks do not prove complete extraction. Inspect lint diagnostics before retrieval. Use the PDF when a node or reference remains unresolved or ambiguous.

The [2016 extraction review](ieee80211-2016-extraction.md) records the parser corrections and all unresolved references. Fourteen references require external documents. Six source references lack a confirmed target in this edition.

## IEEE 802.15.4

Use `--document ieee802154-2024` on searches and structural lookups. The 2024 edition is a reference edition, not evidence that an existing model claims that edition or every PHY it defines. Older model citations require an explicit edition mapping; unavailable older texts remain a gap. Confirm the applicable PHY and MAC operating mode before deriving a check.

Representative navigation starts at clause 3.1 (definitions), clause 6 (MAC), clause 7 (MAC formats), clause 13 (O-QPSK PHY), and clause 16 (HRP UWB PHY). Verify the exact subclause and its source pages before citing a requirement.

For example:

```sh
./bin/inet_process_standards get clause 6.3.2.1 --document ieee802154-2024 --output <corpus-output> --json
./bin/inet_process_standards get figure 6-2 --document ieee802154-2024 --output <corpus-output> --json
./bin/inet_process_standards define association --document ieee802154-2024 --output <corpus-output> --json
```

Figure 6-2's extracted node locates its caption on physical PDF page 64. Inspect that PDF page for the flowchart arrows and decisions; the caption alone is not the algorithm.
