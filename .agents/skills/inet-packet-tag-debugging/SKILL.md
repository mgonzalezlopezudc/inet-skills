---
name: inet-packet-tag-debugging
description: Debug INET Packet, Chunk, and tag behavior. Use to inspect packet ownership, encapsulation/decapsulation, protocol dispatch, request/indication tags, region tags, header chunks, metadata propagation, duplication, popping/peeking, or why packet metadata is missing or changed across INET modules, including MAC/PHY and IEEE 802.11 paths.
---

# Debug packets, chunks, and tags

Distinguish packet data from metadata: correct bytes can coexist with a missing tag, protocol marker, region annotation, or header representation.

1. Identify the packet and the last module where metadata is correct and first where it is wrong.
2. Inspect the checked-out code that adds, removes, copies, peeks, pops, inserts, trims, encapsulates, decapsulates, or duplicates it.
3. Determine whether the consumer expects a front header, region tag, protocol tag, request/indication tag, or packet protocol field.
4. Check sharing, ownership, and preservation across duplication, fragmentation, aggregation, and protocol conversion.
5. Use targeted logs or LLDB at the first changing module; confirm protocol-visible effects with PCAP.

Remember: peek does not consume data; pop/trim does. Request and indication tags usually carry opposite-direction metadata. Region tags cover byte ranges. PCAP does not expose every internal tag, and debugger method calls may execute code.

Return the packet identity, first divergent module/source location, relevant tag/chunk state, ownership evidence, and failure category.
