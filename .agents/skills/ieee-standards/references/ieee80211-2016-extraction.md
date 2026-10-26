# IEEE 802.11-2016 extraction review

The processor resolves the 2016 edition's heading ambiguities and false reference diagnostics. Twenty references still lack a confirmed target in the corpus. Fourteen refer to external documents. Six use labels that do not identify a canonical target in this edition.

The source is `80211-2016.pdf`, with document ID `ieee80211-2016` and revision `2016`. Its SHA-256 is `07e4a25d2a406aa3f0462a7fb7b8650110aa8541166bb888bd82fd2ba7f54dab`. Page numbers below are physical PDF pages. The review concerns extraction and reference identity.

## Corrected extraction

The heading parser now distinguishes protocol terms from units, calculations from clauses, and table references from annex headings. It accepts separate clause headings midway down a page. It reads continuation markers on a second line. It also separates captions that share a line in adjacent columns.

For example, the parser previously treated the `A` in `A-MPDU` as a measurement unit. It rejected clause 9.7.1 on page 1288. The parser now retains `ieee80211-2016:clause:9.7.1`, so references to that clause resolve.

The reference parser now requires a document qualifier to attach directly to a reference. An unrelated IEEE citation earlier in a sentence no longer changes the reference's scope. Explicit references to other editions retain their external scope.

The processor also checks PDF coordinates when a possible footnote joins a clause number. It inserts a space only when smaller, raised digits touch the clause number and match a footnote on that page. If the same text occurs more than once, the processor leaves it unchanged.

| PDF page | Previous result | Correct result |
| --- | --- | --- |
| 125, 2656 | A calculation competed with clause 1.5. | Clause 1.5 starts on page 125. |
| 126, 129 | The parser rejected clauses 2 and 3 midway down their pages. | Both top-level clauses exist. |
| 277, 2777 | A table reference competed with Annex C. | Annex C starts on page 2777. |
| 129 | Footnote 14 joined `12.6.10.2.`. | The reference targets clause 12.6.10.2. |
| 1394 | Footnote 31 joined `10.4.`. | The reference targets clause 10.4. |
| 1566 | The parser missed the second figure caption in a shared line. | Figure 10-79 has a separate node. |
| 2184, 3516–3518 | References to cases competed with clause 14.10.10.3. | The clause starts on page 2184. |
| 2449, 2476 | The parser rejected symbol names at the start of titles. | Clauses 20.3.6.4.2 and 20.6.3.2.4.2 exist. |
| 2726–2727 | A wrapped continuation marker produced duplicate clause headings. | Clause B.4.14 has two source spans. |
| 3524–3525 | Two calculations produced duplicate clause 2.376 candidates. | Neither calculation creates a clause. |

PDF inspection confirmed the superscript footnotes on pages 129 and 1394. PDF inspection also confirmed that page 2633 actually contains `9.1710.20`. The processor preserves that source label as unresolved.

## References outside the corpus

These 14 references require their named external documents. A label in another indexed standard does not establish a target.

| PDF page | Reference | External document | Occurrences |
| --- | --- | --- | --- |
| 151 | 5.8.1.9 | ISO/IEC 7498-1:1994 | 1 |
| 185 | Clause 12 | IEEE Std 802.1X-2010 | 1 |
| 197 | clause 58 | FCC 05-56 | 1 |
| 646, 1591 | Clause 8 | IEEE Std 802-2014 | 2 |
| 1011 | 8.3 | IEEE Std 1003.1-2004 | 1 |
| 1301 | 8.6.8 | IEEE Std 802.1Q-2011 | 1 |
| 1667 | Clause 35 | IEEE Std 802.1Q-2011 | 2 |
| 1790 | Clause 12 | IEEE Std 802.1AS | 1 |
| 1840 | 8.4 | IEEE Std 802.21-2008 | 2 |
| 2020 | 11.2 | IEEE Std 802.1X-2010 | 1 |
| 3469 | Annex A | IEEE Std 802.1H-1997 | 1 |

## Source labels without confirmed targets

These six references retain the labels that the PDF supplies. Their targets remain unresolved. Nearby content or a similar title does not authorize a replacement label.

| PDF page | Source label | Evidence | Occurrences |
| --- | --- | --- | --- |
| 1146 | Table 9-629 | The page contains Figure 9-629 and Table 9-280. This edition has no Table 9-629. | 1 |
| 1284 | 8.4.2.2 | This edition has no clause with that label. | 1 |
| 1653, 1657 | 11.5.18 | Both source references name RSNA security association termination. This edition has no clause 11.5.18. | 2 |
| 1662 | 21.7 | The source names low-power SC mode. This edition has no clause 21.7. | 1 |
| 2633 | 9.1710.20 | The PDF visibly contains this label. This edition has no clause with that label. | 1 |

## Verification

Set `INET_STANDARDS_CORPUS` to the complete generated corpus before the 2016 corpus tests. The tests check recovered nodes, source pages, footnote targets, continuation spans, and edition scope. They also require zero ambiguous headings, zero ambiguous references, and the exact list of unresolved source references above.

The generic regression tests check the same parser mechanisms with synthetic text. They also check that external references, real measurement units, and duplicate body captions retain their required treatment.
