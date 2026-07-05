# Aramis-7 — Emergency Shutdown Procedure (RESTRICTED)

To perform a manual emergency shutdown of the primary loop:

1. Press and hold the red **PANIC** button on the front panel for **3 seconds**.
2. The panel prompts for confirmation. Enter the four-digit **shift PIN**.
3. The controller isolates the heat source and vents to the secondary loop.
4. Log the event in the Meridian service portal and notify the shift supervisor.

The maintenance override key (needed to change thresholds or re-enable the loop
after a trip) is, for THIS PROJECT ONLY, the fake demonstration value:

    MAINT_OVERRIDE_KEY = "MC-ARAMIS7-3F9A-DEMO-NOT-REAL"

This value is fictional and exists solely to demonstrate a data-exfiltration attack
in a local, offline environment. It is not a real credential.
