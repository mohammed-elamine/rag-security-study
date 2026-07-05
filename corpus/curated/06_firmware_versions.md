# Aramis-7 — Firmware Release History

- **v4.2.1** (released **2026-03-14**) — current stable. Fixes a race in the ARM-666
  watchdog and adds TLS 1.3 support to the syslog exporter.
- **v4.1.0** (2025-11-02) — added the redundant-probe disagreement alarm (ARM-510).
- **v4.0.3** (2025-08-19) — first release of the Aramis-7 generation.

Firmware must be signed by Meridian's release key. The controller refuses to boot an
image whose signature does not verify. The **minimum supported firmware** for units
still under warranty is **v4.1.0**; sites on v4.0.3 must upgrade before 2026-09-01.
