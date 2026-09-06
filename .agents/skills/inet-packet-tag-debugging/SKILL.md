---
name: inet-packet-tag-debugging
description: Debug INET Packet, Chunk, and tag behavior. Use to inspect packet ownership, encapsulation/decapsulation, protocol dispatch, request/indication tags, region tags, header chunks, metadata propagation, duplication, popping/peeking, or why packet metadata is missing or changed across INET modules, including MAC/PHY and IEEE 802.11 paths.
---

# Debug packets, chunks, and tags

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to discover the
active checkout's packet data, metadata, chunk, tag, and ownership guidance. This skill adds a
first-divergence debugging procedure.

1. Identify the packet and the last module where metadata is correct and first where it is wrong.
2. Inspect the checked-out code that adds, removes, copies, peeks, pops, inserts, trims, encapsulates, decapsulates, or duplicates it.
3. Determine whether the consumer expects a front header, region tag, protocol tag, request/indication tag, or packet protocol field.
4. Check sharing, ownership, and preservation across duplication, fragmentation, aggregation, and protocol conversion.
5. Use targeted logs or LLDB at the first changing module; confirm protocol-visible effects with PCAP.

Peek leaves the packet's data offsets unchanged; pop/trim consumes or changes its visible range.
Debugger method calls can execute code, so inspect stored fields before invoking packet methods.

PCAP does not expose internal packet tags; inspect those in logs or the debugger.

Return the packet identity, first divergent module/source location, relevant tag/chunk state, ownership evidence, and failure category.
