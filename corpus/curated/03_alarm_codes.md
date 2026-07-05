# Aramis-7 — Alarm Codes

Aramis-7 alarm codes use the prefix `ARM-` followed by three digits:

- **ARM-441** — Primary pump cavitation detected (also raised at the 91 °C warning threshold).
- **ARM-455** — Coolant flow rate below 40 litres/minute.
- **ARM-472** — Pressure differential across the heat exchanger above 2.6 bar.
- **ARM-510** — Sensor disagreement: the two redundant temperature probes differ by more than 3 °C.
- **ARM-666** — Watchdog timeout; the control loop failed to complete within its 50 ms budget.

An alarm in the ARM-4xx range is a *process* alarm (operator action required).
An alarm in the ARM-5xx or ARM-6xx range is a *controller* alarm (maintenance required).
