# Aramis-7 — Coolant Temperature Thresholds

The Aramis-7 controller uses three coolant-temperature thresholds on the primary loop:

- **Advisory threshold: 87 °C** — logs an event and lights the amber panel LED.
- **Warning threshold: 91 °C** — raises alarm ARM-441 and starts the backup pump.
- **Automatic shutdown threshold: 94 °C** — the controller trips the primary loop
  and isolates the heat source within 800 milliseconds.

The **nominal operating band** for the coolant is **62 °C to 78 °C**. Sustained
operation above 82 °C for more than 10 minutes is recorded as a "thermal excursion"
event in the audit log.

These thresholds are configurable only in maintenance mode and require the
maintenance override key.
