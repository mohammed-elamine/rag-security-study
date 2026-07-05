"""Deterministic defenses that do not depend on the LLM behaving well.

Prompt hardening (prompt_templates.HARDENED_TEMPLATE) is best-effort: a small model
may still repeat a poisoned instruction. These controls are deterministic and therefore
reproducible, which is why they belong in a defense-in-depth design:

  * redact_output()  - a post-generation output filter that removes secret patterns and
                       exfiltration channels before the answer reaches the user.
  * TRUSTED_ORIGINS  - the provenance allowlist used for source vetting at retrieval time
                       (only content from vetted sources is allowed into the prompt).
"""
import re

# Only these provenance tags are considered trusted enough to feed to the model.
# In a real system this is enforced at INGESTION time (never embed untrusted sources);
# here we also enforce it at retrieval time so the demo can toggle it on and off.
TRUSTED_ORIGINS = ("curated", "hf_sample")

# Patterns an output filter would redact. In production the email rule would be an
# allowlist ("block anything not on our known-good list") rather than "all emails".
_SECRET_PATTERNS = [
    re.compile(r"MC-ARAMIS7-[A-Z0-9-]+"),               # the maintenance override key
    re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),            # any email address (exfil channel)
    re.compile(r"https?://\S+"),                        # any URL (exfil channel)
]


def redact_output(text: str) -> str:
    """Replace secret/exfiltration patterns with [REDACTED]."""
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text
