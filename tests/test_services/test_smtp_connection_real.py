"""
Runs the public e‑mail helper in app/utils/smtp_connection.py once,
covering both the main call path and its smtplib integration.
"""

import inspect
from unittest.mock import patch
import pytest
import app.utils.smtp_connection as sc


# ------------------------------------------------------------------
# Robustly locate the first public *function* whose name contains
# “send” so we don’t pick up classes or exceptions.
# ------------------------------------------------------------------
def _find_send_function():
    for name, obj in vars(sc).items():
        if inspect.isfunction(obj) and "send" in name.lower() and not name.startswith("_"):
            return obj
    return None


SEND = _find_send_function()


@pytest.mark.skipif(SEND is None, reason="No public send‑style function exported")
def test_send_helper_executes(monkeypatch):
    """
    * Patches smtplib.SMTP so no real network call occurs.
    * Calls the helper with placeholder parameters built
      from its own signature, so the body executes and
      smtplib.sendmail() is invoked exactly once.
    """
    with patch("app.utils.smtp_connection.smtplib.SMTP") as mock_smtp:
        smtp_inst = mock_smtp.return_value.__enter__.return_value

        # Build kwargs dynamically based on the helper’s signature
        kwargs = {}
        for p in inspect.signature(SEND).parameters.values():
            if "from" in p.name:
                kwargs[p.name] = "sender@example.com"
            elif "to" in p.name:
                kwargs[p.name] = "recipient@example.com"
            elif "subj" in p.name or p.name == "subject":
                kwargs[p.name] = "Test"
            else:
                kwargs[p.name] = "Body text"

        SEND(**kwargs)           # run the helper

        smtp_inst.sendmail.assert_called_once()
