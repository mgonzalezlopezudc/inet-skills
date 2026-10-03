# Vocabulary for IEEE 802.11 development

This file defines the project vocabulary for Simplified Technical English (STE).
The vocabulary covers IEEE 802.11 protocols, INET models, and simulation evidence.
IEEE means Institute of Electrical and Electronics Engineers.

## Use of the vocabulary

1. Use each approved term with the meaning and part of speech in its table.
2. Use the acronym or the full term shown in the same entry.
3. Keep the spelling and capitalization of the approved term.
4. Use the singular or plural form as the sentence requires.
5. Preserve exact code identifiers, commands, configuration keys, error strings, and quotations.
6. Use the cited standard for protocol requirements.

The tables define vocabulary, not the features that an INET checkout supports.
The definitions describe concepts in plain English.
Official acronym expansions retain their exact technical words.
An acronym in a definition refers to its entry in this file.

## Protocol layers and stations

| Approved term | Part of speech | Definition |
| --- | --- | --- |
| IEEE 802.11 | noun | The family of IEEE standards that defines MAC and PHY operation for wireless local area networks. |
| Wi-Fi | noun | The common name for wireless network technology that uses IEEE 802.11. |
| WLAN | noun | Wireless local area network. A local network that uses a wireless medium. |
| MAC | noun | Medium access control. The protocol layer that controls channel access and exchanges frames. |
| PHY | noun | Physical layer. The protocol layer that sends and receives signals through the medium. |
| LLC | noun | Logical link control. The layer above the MAC that provides a common interface to upper protocols. |
| MIB | noun | Management information base. The set of attributes that describes station configuration and state. |
| STA / station | noun | A device with an IEEE 802.11 MAC and PHY interface. An AP is also a station. |
| AP / access point | noun | A station that gives associated stations access to the distribution system. |
| non-AP station | noun | A station that does not act as an AP. |
| peer | noun | The other station in a protocol exchange or agreement. |
| BSS | noun | Basic service set. A set of stations that follows one coordination function. |
| BSSID | noun | Basic service set identifier. The identifier of a BSS. |
| SSID | noun | Service set identifier. The network name that a station advertises or selects. |
| AID | noun | Association identifier. An identifier that an AP assigns to an associated station. |
| DS | noun | Distribution system. The system that connects BSSs and supports delivery between them. |
| association | noun | The relationship that lets a station use an AP to access the DS. |
| authentication | noun | The protocol procedure that establishes an authentication relationship between stations. It is separate from association. |
| capability | noun | A feature or limit that a station supports. |
| operation element | noun | An information element that describes the parameters for current BSS operation. |
| IE / information element | noun | A structured item in a frame body that carries protocol information. |
| feature gate | noun | A condition that permits a feature to operate when its required capabilities and operation parameters allow it. |

## Frames, addresses, and data units

| Approved term | Part of speech | Definition |
| --- | --- | --- |
| frame | noun | A MAC protocol data unit. A frame has a MAC header and an FCS. |
| data frame | noun | A frame that carries data or performs a function of a data subtype. |
| control frame | noun | A frame that supports MAC exchange control, such as RTS, CTS, ACK, BAR, or Block Ack. |
| management frame | noun | A frame that supports station management, such as discovery, authentication, association, or an Action exchange. |
| Beacon | noun | A management frame that advertises BSS information at regular intervals. |
| Action frame | noun | A management frame that carries an action from a defined action category. ADDBA and DELBA use Action frames. |
| header | noun | The fields at the start of a data unit that identify or control that data unit. |
| payload | noun | The content that a protocol carries for another protocol or service. |
| FCS | noun | Frame check sequence. The field that lets the recipient check a frame for transmission errors. |
| MSDU | noun | MAC service data unit. The data unit that the MAC receives from its service user. |
| MPDU | noun | MAC protocol data unit. A MAC frame with its header and FCS. |
| PSDU | noun | PHY service data unit. The data unit that the MAC supplies to the PHY for transmission. |
| PPDU | noun | PHY protocol data unit. The unit that the PHY transmits, with its preamble, PHY header, and data. |
| RA | noun | Receiver address. The MAC address of the immediate receiver of a frame. |
| TA | noun | Transmitter address. The MAC address of the immediate transmitter of a frame. |
| SA | noun | Source address. The MAC address of the original source of the data. |
| DA | noun | Destination address. The MAC address of the final destination of the data. |
| unicast | noun; adjective | Delivery to one station. A unicast address identifies one recipient. |
| group address | noun | A MAC address that identifies multiple recipients. Multicast and broadcast addresses are group addresses. |
| sequence number | noun | The number that identifies an MPDU within its sequence space. IEEE 802.11 sequence numbers wrap from 4095 to 0. |
| fragment | noun | An MPDU that carries part of a larger MAC service data unit or management data unit. |
| fragmentation | noun | The process that splits a data unit into fragments. |
| duplicate | noun; adjective | A received frame that repeats an MPDU or fragment that the recipient already received. |
| frame exchange | noun | A related sequence of transmitted frames and responses between stations. |

_Avoid_: `packet` as a synonym for `frame`, `MPDU`, `MSDU`, or `PPDU`. Name the required unit.

## Channel access and responses

| Approved term | Part of speech | Definition |
| --- | --- | --- |
| channel access | noun | The procedure that gives a station permission to start a transmission on the medium. |
| contention | noun | Competition between stations or access functions for channel access. |
| CSMA/CA | noun | Carrier sense multiple access with collision avoidance. An access method that checks the medium and uses delays to reduce collisions. |
| DCF | noun | Distributed coordination function. The basic IEEE 802.11 coordination function that uses contention for channel access. |
| HCF | noun | Hybrid coordination function. The coordination function that includes EDCA and controlled channel access for QoS traffic. |
| QoS | noun | Quality of service. Traffic treatment that accounts for requirements such as priority, delay, and throughput. |
| EDCA | noun | Enhanced distributed channel access. The contention method that gives access categories different channel access parameters. |
| EDCAF | noun | Enhanced distributed channel access function. An access function that manages contention for one access category. |
| AC | noun | Access category. One of the four EDCA traffic categories: AC_BK, AC_BE, AC_VI, and AC_VO. |
| AC_BK | noun | The background access category. |
| AC_BE | noun | The best effort access category. |
| AC_VI | noun | The video access category. |
| AC_VO | noun | The voice access category. |
| UP | noun | User priority. A priority value from 0 to 7 that maps traffic to an access category. |
| TID | noun | Traffic identifier. The identifier of a traffic class or stream. Block Ack state uses the peer and TID. |
| CCA | noun | Clear channel assessment. The PHY procedure that decides whether the channel is busy. |
| NAV | noun | Network allocation vector. MAC state that records a reservation of the medium from protocol duration information. |
| CW | noun | Contention window. The range parameter that bounds the random choice of a backoff counter. |
| CWmin / CWmax | noun | The minimum and maximum values of the contention window. |
| backoff | noun | The procedure that delays channel access by a selected number of idle slots. |
| IFS | noun | Interframe space. A required time interval between specified frame transmissions. |
| SIFS | noun | Short interframe space. The interval that separates specified immediate responses and frames within an exchange. |
| DIFS | noun | DCF interframe space. The interval that the DCF uses before contention can proceed on an idle medium. |
| AIFS | noun | Arbitration interframe space. The interval that an EDCAF uses before contention can proceed on an idle medium. |
| AIFSN | noun | Arbitration interframe space number. The number of slot times that supplements SIFS to determine AIFS. |
| EIFS | noun | Extended interframe space. An access delay that applies after specified reception errors. |
| TXOP | noun | Transmission opportunity. A time interval in which a QoS station has the right to start frame exchange sequences. |
| TXOP limit | noun | The duration limit that applies to a TXOP. |
| RTS | noun | Request to send. A control frame that requests protection for a subsequent exchange. |
| CTS | noun | Clear to send. A control frame that provides protection, usually as a response to RTS. |
| ACK | noun | Acknowledgment. The control frame that confirms successful reception of a frame that requires this response. |
| acknowledgment | noun | Protocol confirmation of successful reception. ACK and Block Ack are distinct acknowledgment mechanisms. |
| ACK policy | noun | The rule that specifies the acknowledgment mechanism for a frame. |
| retry | noun | A further transmission attempt after an unsuccessful attempt. |
| retransmission | noun | Another transmission of the same MPDU or fragment. |
| retry limit | noun | The bound on retries that determines when the MAC stops attempts for a frame. |
| timeout | noun | The expiry of a time limit while a required event or response remains absent. |

_Avoid_: `ACK` as a name for a Block Ack frame. Use `Block Ack` or `BA`.

## Aggregation and Block Ack

| Approved term | Part of speech | Definition |
| --- | --- | --- |
| aggregation | noun | The process that combines multiple data units into one aggregate. Specify A-MSDU or A-MPDU when the distinction matters. |
| A-MSDU | noun | Aggregate MAC service data unit. An aggregate of MSDU subframes that one MPDU carries. |
| A-MPDU | noun | Aggregate MAC protocol data unit. An aggregate of MPDU subframes within a PSDU. Each MPDU retains its own FCS. |
| subframe | noun | One constituent unit of an aggregate. Its structure depends on the aggregate format. |
| delimiter | noun | The structure that identifies an MPDU boundary and length within an A-MPDU subframe. |
| padding | noun | Extra bits or bytes that meet alignment or duration requirements. |
| BA / Block Ack | noun | Block acknowledgment. A mechanism and control frame that report reception status for multiple MPDUs. |
| BAR | noun | Block acknowledgment request. A control frame that requests a Block Ack response. |
| ADDBA | noun | Add block acknowledgment. The request and response procedure that establishes a Block Ack agreement. |
| DELBA | noun | Delete block acknowledgment. An Action frame that ends a Block Ack agreement. |
| Block Ack agreement | noun | The shared protocol parameters that permit Block Ack operation between an originator and a recipient. |
| originator | noun | The station that sends data under a Block Ack agreement. |
| recipient | noun | The station that receives data under a Block Ack agreement. |
| dialog token | noun | A field that links a management response to its request within the applicable procedure. |
| SSN | noun | Starting sequence number. The sequence number that marks the start of the applicable Block Ack range. |
| bitmap | noun | A set of bits that records reception status for the sequence positions in a Block Ack range. |
| reorder buffer | noun | The storage that holds received MPDUs until the recipient can deliver them in the required order. |
| reorder window | noun | The range of sequence numbers that the recipient currently accepts for reorder processing. |
| buffer size | noun | The negotiated capacity for MPDUs under a Block Ack agreement. It is not a byte count. |

_Avoid_: `aggregation` as proof of A-MPDU support. Name the aggregate format.

## PHY formats, channels, and error models

| Approved term | Part of speech | Definition |
| --- | --- | --- |
| HT | noun; adjective | High throughput. The MAC and PHY features introduced by IEEE 802.11n. |
| VHT | noun; adjective | Very high throughput. The MAC and PHY features introduced by IEEE 802.11ac. |
| HE | noun; adjective | High efficiency. The MAC and PHY features introduced by IEEE 802.11ax. |
| EHT | noun; adjective | Extremely high throughput. The MAC and PHY features introduced by IEEE 802.11be. |
| legacy | adjective | A format or procedure that precedes the feature family under discussion. Specify the family or format when the distinction matters. |
| PHY mode | noun | A defined combination of PHY format and transmission parameters. |
| mode set | noun | The collection of PHY modes available to a radio or MAC configuration. |
| MCS | noun | Modulation and coding scheme. The scheme that selects modulation and error correction parameters for a transmission. |
| NSS | noun | Number of spatial streams. The count of spatial streams in a transmission. |
| spatial stream | noun | An independent data stream that a multiple-antenna PHY carries. |
| subcarrier | noun | One component carrier frequency within an OFDM signal. |
| MIMO | noun; adjective | Multiple input, multiple output. A radio technique that uses multiple antennas at the transmitter and receiver. |
| SU / single-user | adjective | A single-user transmission serves one user. |
| MU / multi-user | adjective | A multi-user transmission serves multiple users. |
| OFDM | noun | Orthogonal frequency division multiplexing. A modulation method that carries data on orthogonal subcarriers. |
| OFDMA | noun | Orthogonal frequency division multiple access. A method that assigns groups of orthogonal subcarriers to different users. |
| RU | noun | Resource unit. A defined set of subcarriers that a PHY allocates to a user. |
| GI | noun | Guard interval. An interval between symbols that reduces interference from delayed signal paths. |
| LDPC | noun; adjective | Low-density parity-check. A family of error correction codes. |
| BCC | noun | Binary convolutional code. An error correction code that uses convolutional encoding. |
| preamble | noun | The first part of a PPDU that supports signal detection, synchronization, and channel estimation. |
| channel | noun | A defined frequency allocation for wireless communication. |
| channel width | noun | The frequency span of a channel or transmission, usually expressed in MHz. |
| primary channel | noun | The designated channel that anchors channel access and operation within a wider channel. |
| secondary channel | noun | An additional channel that forms part of a wider channel beside its primary channel. |
| channel bonding | noun | The use of adjacent channels together as a wider channel. |
| link | noun | A wireless communication path between two stations. An MLD can use multiple links through its affiliated stations. |
| MLO | noun | Multi-link operation. Operation that lets a multi-link device use multiple affiliated links. |
| MLD | noun | Multi-link device. A device that contains affiliated stations for multi-link operation. |
| interference | noun | Unwanted signal energy that affects reception of the desired signal. |
| noise | noun | Unwanted random signal energy, separate from transmissions that cause interference in the model. |
| RSSI | noun | Receive signal strength indicator. An indication of received signal strength. Its scale depends on the implementation. |
| SNR | noun | Signal-to-noise ratio. The ratio of desired signal power to noise power. |
| SNIR | noun | Signal-to-noise-and-interference ratio. The INET term for the ratio of signal power to combined noise and interference power. |
| SINR | noun | Signal-to-interference-plus-noise ratio. The common literature term for the same ratio that INET calls SNIR. |
| BER | noun | Bit error rate. The fraction or probability of incorrect bits, as specified by the measurement or model. |
| PER | noun | Packet error rate. The fraction or probability of failed data units. Specify whether the unit is an MPDU or PPDU. |
| error model | noun | A model that calculates reception errors from the signal conditions and transmission parameters. |
| EESM | noun | Exponential effective SNR mapping. A method that maps multiple signal quality values to one effective value for an error model. |
| TGn | noun | IEEE 802.11 Task Group n. Its channel models describe propagation conditions for HT studies. |
| rate selection | noun | The choice of a PHY mode for a frame or transmission. |
| rate control | noun | A procedure that adapts rate selection to observed link conditions. |

_Avoid_: `bandwidth` when the intended quantity is `channel width` or `data rate`. Name the quantity.
_Avoid_: `SINR` in place of the INET term `SNIR` when the text describes an INET API or result.

## INET models and simulation evidence

| Approved term | Part of speech | Definition |
| --- | --- | --- |
| OMNeT++ | noun | The discrete event simulation framework that executes INET models. |
| INET | noun | The network model framework for OMNeT++. INET is the project name. |
| NED | noun | Network Description. The OMNeT++ language that defines module types, parameters, gates, and connections. |
| MSG | noun; adjective | The OMNeT++ message definition format. The tool generates C++ types from `.msg` files. |
| INI | noun; adjective | The configuration file format that supplies simulation parameters and run settings. INET commonly uses `omnetpp.ini`. |
| module | noun | An OMNeT++ simulation component with parameters and gates. A compound module contains submodules. |
| gate | noun | A module endpoint through which an OMNeT++ message enters or leaves. |
| Packet | noun | The INET class that holds packet content and metadata. A Packet can represent data units at different protocol layers. |
| chunk | noun | An INET object that represents part of packet content, such as a header or payload. |
| tag | noun | Metadata attached to an INET Packet for local processing. A tag is separate from the protocol bytes. |
| region tag | noun | Metadata attached to a region of packet content. It follows that region through content operations. |
| serializer | noun | Code that converts a protocol representation to bytes and converts bytes to that representation. |
| dissector | noun | Code that identifies the protocol parts of packet content. |
| radio medium | noun | The INET module that models signal propagation and interaction between radios. |
| transmission | noun | One attempt to send a signal or data unit. A retransmission is a separate transmission. |
| reception | noun | The receiver's process for a signal. Reception can succeed or fail. |
| simulation signal | noun | An OMNeT++ notification that a module emits for listeners or result recorders. |
| wireless signal | noun | The representation of a radio transmission that travels through the modeled medium. |
| self-message | noun | An OMNeT++ message that a module schedules for itself, usually as a timer. |
| Cmdenv | noun | The OMNeT++ command-line interface for simulation execution. |
| Qtenv | noun | The OMNeT++ graphical interface for simulation execution. |
| PCAP | noun; adjective | Packet capture. A capture file format that stores packet bytes and capture metadata. |
| TShark | noun | The command-line packet analysis tool from Wireshark. |
| event log | noun | An OMNeT++ record of simulation events and message operations. |
| scalar | noun | One recorded result value, such as a count or mean. OMNeT++ commonly stores scalars in `.sca` files. |
| vector | noun | A sequence of recorded values with simulation times. OMNeT++ commonly stores vectors in `.vec` files. |
| fingerprint | noun | A digest of selected simulation properties that a regression test compares with an expected digest. |
| regression test | noun | A test that detects an unintended change to behavior that an earlier version supported. |
| baseline | noun | The stored expectation against which a test or result comparison checks current output. |
| seed | noun | The initial value that determines a random number sequence. |
| throughput | noun | The amount of data that crosses a specified measurement boundary per unit of time. State the boundary and counted data. |
| goodput | noun | The useful application data delivered per unit of time. It excludes protocol overhead and repeated delivery. |
| data rate | noun | The number of data bits per unit of time at a specified protocol layer. |
| latency | noun | The elapsed time between specified start and end events. State both events. |

_Avoid_: `signal` without qualification when a simulation signal and a wireless signal are both possible.
_Avoid_: `throughput`, `goodput`, and `data rate` as interchangeable terms.

## Approved technical verbs

| Approved term | Part of speech | Definition |
| --- | --- | --- |
| transmit | verb | Send a frame or signal through the wireless medium. |
| receive | verb | Accept a signal or data unit at the specified receiver or protocol boundary. |
| acknowledge | verb | Confirm successful reception through the required protocol response. |
| retransmit | verb | Transmit the same MPDU or fragment again. |
| aggregate | verb | Combine data units into an aggregate of the specified format. |
| encapsulate | verb | Place a data unit inside the representation of an outer protocol. |
| decapsulate | verb | Remove the outer protocol representation to expose its payload. |
| serialize | verb | Convert a protocol representation to bytes. |
| deserialize | verb | Convert bytes to a protocol representation. |
| drop | verb | Remove a data unit from further processing or delivery at the specified point. |
| deliver | verb | Pass a data unit to the specified recipient or upper protocol. |

## Definition sources

The protocol vocabulary follows IEEE Std 802.11-2024 and IEEE Std 802.11be-2024.
The sources define terminology; they do not establish support in a particular INET checkout.

- IEEE Std 802.11-2024, Clauses 3.1 and 3.2: protocol definitions.
  The TXOP definition is in Clause 3.1, physical PDF page 278.
  The corpus identifier is `ieee80211-2024:definition:transmission%20opportunity%20%28TXOP%29`.
- IEEE Std 802.11-2024, Clause 3.4: acronyms and abbreviations, physical PDF pages 324–339.
  The corpus identifier is `ieee80211-2024:clause:3.4`.
- IEEE Std 802.11be-2024, Clause 3.4: EHT, MLO, and MLD expansions, physical PDF pages 65–66.
  The corpus identifier is `ieee80211be-2024:clause:3.4`.
- [IEEE 802.11 QoS tutorial](https://www.ieee802.org/1/files/public/docs2008/avb-gs-802-11-qos-tutorial-1108.pdf): explanations of EDCA and TXOP.
- [IEEE 802.11 packet analysis references](.agents/skills/inet-80211-packet-debugging/SKILL.md): frame, channel access, aggregation, and PHY concepts used by this repository.
- [INET packet analysis skill](.agents/skills/inet-packet-tag-debugging/SKILL.md): Packet, chunk, and tag concepts.
- [OMNeT++ result analysis skill](.agents/skills/omnetpp-result-analysis/SKILL.md): scalar and vector evidence.

The local standards corpus supplied the standard text and page locations.
The entries above cite definition and acronym clauses.
No PDF inspection was necessary.
