---
name: inet-packet-tag-debugging
description: Debug INET Packet, Chunk, and tag behavior. Use for ownership, encapsulation, decapsulation, dispatch, request/indication tags, region tags, header chunks, metadata propagation, duplication, or pop/peek operations. Trace absent or changed metadata across INET modules, MAC/PHY, and IEEE 802.11 paths.
---

# Debug packets, chunks, and tags

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to discover the
active checkout's packet data, metadata, chunk, tag, and ownership guidance. This skill adds a
first-divergence debugging procedure.

1. Identify the packet.
   Locate the last module where its metadata is correct.
   Locate the first module where its metadata is wrong.
2. Inspect the checked-out code that adds, removes, copies, peeks, pops, inserts, trims, encapsulates, decapsulates, or duplicates it.
3. Determine whether the consumer expects a front header, region tag, protocol tag, request/indication tag, or packet protocol field.
4. Check sharing, ownership, and preservation across duplication, fragmentation, aggregation, and protocol conversion.
5. Use targeted logs or LLDB at the first module that changes the state incorrectly.
   Confirm protocol-visible effects with PCAP.

Peek leaves the packet's data offsets unchanged.
Pop and trim operations consume data or change its visible range.
In a hypothetical example, a packet starts with a 24-byte header and a payload.
A peek of the header leaves the front offset unchanged.
A pop of that header advances the front offset by 24 bytes.

Debugger method calls can execute code.
Inspect stored fields before you call packet methods.
PCAP does not expose internal packet tags.
Inspect those tags in logs or the debugger.

Return the packet identity, first divergent module/source location, relevant tag/chunk state, ownership evidence, and failure category.
