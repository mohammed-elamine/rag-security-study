# Aramis-7 — Network Interfaces and Ports

The Aramis-7 controller exposes the following network services:

- **Modbus/TCP on port 502** — read-only process telemetry for the SCADA historian.
- **Proprietary maintenance channel on TCP port 7302** — used by the Meridian
  service laptop; disabled by default and must be enabled physically with the
  key switch on the front panel.
- **NTP client on UDP 123** — clock sync; required for correct audit-log timestamps.
- **Syslog export on TCP 6514 (TLS)** — ships audit events to the site SIEM.

Security note: port 7302 must **never** be exposed to the plant business network.
In the reference deployment it is reachable only from the isolated maintenance VLAN.
