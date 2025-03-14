"""Contains the job definitions"""

from typing import Any, Dict, Optional, Tuple


def error_response(msg: str) -> Tuple[str, None, None, None]:
    """Return an error mech response."""
    return msg, None, None, None


def run(**kwargs) -> Tuple[Optional[str], Optional[Dict[str, Any]], Any, Any]:
    """Run the task"""

    # RPC
    RPC = kwargs.get("api_keys", {}).get("RPCS", {}).get("base", None)
    if not RPC:
        return error_response("RPC was not provided")

    return new_tokens, None, None, None
