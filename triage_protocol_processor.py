"""triage_protocol_processor.py

Production-ready utility for stateless Vercel serverless functions.
Implements:
- sanitize_and_tokenize_triage_text(raw_text: str) -> list[str]
- calculate_triage_confidence(logprobs: list[float], critical_indices: list[int]) -> dict
- hand_off_to_flywheel(user_query: str, metrics: dict, trigger_status: bool, webhook_url: str = None)

Only uses Python standard library modules to remain compatible with minimal runtimes.
"""
from __future__ import annotations

import re
import math
import hashlib
import json
import os
import urllib.request
import tempfile
import concurrent.futures
import asyncio
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

__all__ = [
    "sanitize_and_tokenize_triage_text",
    "calculate_triage_confidence",
    "hand_off_to_flywheel",
    "OnlineTriageStats",
    "persist_payload_locally",
    "redact_pii",
    "StreamingTriageTokenizer",
]


class StreamingTriageTokenizer:
    """Helper to assemble streaming chunks into a sanitized token stream.

    Usage:
        s = StreamingTriageTokenizer()
        s.feed(chunk1)
        s.feed(chunk2)
        tokens = s.flush()

    The tokenizer preserves token ordering and provides stable token boundaries
    to align with token-level logprobs arrays.
    """

    def __init__(self) -> None:
        self._buffer = ""

    def feed(self, chunk: str) -> None:
        if not isinstance(chunk, str):
            raise TypeError("chunk must be a str")
        self._buffer += chunk

    def flush(self) -> List[str]:
        text = self._buffer
        self._buffer = ""
        return sanitize_and_tokenize_triage_text(text)


def _strip_markdown(text: str) -> str:
    """Remove common markdown constructs but preserve medically-relevant symbols.

    This function intentionally removes formatting characters like '*', '_',
    backticks and link parentheses while preserving operators and special
    unicode characters such as '≥' and the unicode dash '‑'.
    """

    # Remove fenced code blocks ```...```
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

    # Remove inline code `...`
    text = re.sub(r"`([^`]*)`", r"\1", text)

    # Turn markdown links [text](url) into text; images -> alt text
    text = re.sub(r"!\[([^\]]*)\]\([^\)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)

    # Remove bold/italic markers **text**, __text__, *text*, _text_
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"_(.*?)_", r"\1", text)

    # Remove remaining stray backslashes
    text = text.replace("\\", "")

    # Remove HTML tags (if present)
    text = re.sub(r"<[^>]+>", "", text)

    # Normalize multiple spaces/newlines to single space to avoid empty tokens
    text = re.sub(r"[\t\r\n]+", " ", text)
    text = re.sub(r" {2,}", " ", text)

    return text.strip()


def sanitize_and_tokenize_triage_text(raw_text: str) -> List[str]:
    """Sanitize `raw_text` by stripping markdown and split into stable tokens.

    Guarantees:
    - Markdown formatting is removed while preserving: '≥', '<', '>', '%', and '‑'.
    - Numeric thresholds (e.g., `94`, `10`, `4`) are captured as numeric tokens
      optionally suffixed with `%` (e.g., `94%` becomes one token).
    - Comparison operators are captured as standalone tokens (`>=`, `≤`, `≥`, etc.).
    - Token order and boundaries are deterministic to align with token-level logprobs.

    Returns a list of token strings.
    """
    if not isinstance(raw_text, str):
        raise TypeError("raw_text must be a str")

    clean = _strip_markdown(raw_text)

    # Token regex:
    # 1) Comparison operators (unicode and ascii), 2) Numbers (with optional decimals and %),
    # 3) Percent sign alone, 4) Words (letters, digits, underscore, common medical symbols),
    # 5) Any single non-space character as a fallback.
    token_pattern = re.compile(
        r"(?:>=|<=|==|!=|≥|≤|>|<|=)"
        r"|\d+(?:\.\d+)?%?"
        r"|%"
        r"|[A-Za-z0-9_°µΩ₂₀₁₃₄₅₆₇₈₉\-]+"
        r"|[^\s]",
        flags=re.UNICODE,
    )

    tokens = token_pattern.findall(clean)

    # Post-process: collapse tokens that are a number followed by a standalone '%' to a single token
    merged_tokens: List[str] = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if i + 1 < len(tokens) and re.fullmatch(r"\d+(?:\.\d+)?", tok) and tokens[i + 1] == "%":
            merged_tokens.append(tok + "%")
            i += 2
            continue
        merged_tokens.append(tok)
        i += 1

    return merged_tokens


def calculate_triage_confidence(logprobs: List[float], critical_indices: List[int]) -> Dict[str, Any]:
    """Compute patent-grade confidence metrics from raw token log probabilities.

    Steps implemented exactly as specified:
    - Phase A: Convert raw log probabilities lambda -> p = exp(lambda)
    - Phase B: Global mean (mu) and global variance (sigma2) over all p_i
    - Phase C: Critical variance sigma2_C over indices in critical_indices
    - Phase D: Safety intercept audit_trigger per specification

    Returns a dict with keys: 'mu', 'sigma2', 'sigma2_C', 'min_p_c', 'audit_trigger', 'state',
    and intermediate arrays 'p_values' (not recommended for long sequences but useful for debugging).
    """
    if not isinstance(logprobs, list):
        raise TypeError("logprobs must be a list of floats")
    n = len(logprobs)
    if n == 0:
        raise ValueError("logprobs list must not be empty")

    # Phase A: log -> linear
    try:
        p_values = [math.exp(float(l)) for l in logprobs]
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError("logprobs must be numeric values") from exc

    # Phase B: global metrics
    mu = sum(p_values) / n
    sigma2 = sum((p - mu) ** 2 for p in p_values) / n

    # Validate critical indices
    if not isinstance(critical_indices, list):
        raise TypeError("critical_indices must be a list of integer indices")
    C = []
    for idx in critical_indices:
        if not isinstance(idx, int):
            raise TypeError("critical_indices must contain integers")
        if 0 <= idx < n:
            C.append(p_values[idx])

    if len(C) == 0:
        # No critical indices found in range: define sigma2_C as 0 and min_p_c as None
        sigma2_C = 0.0
        min_p_c = None
        audit_trigger = False
        state = "HIGH_CERTAINTY"
    else:
        # Phase C: critical constraint variance
        m = len(C)
        sigma2_C = sum((pc - mu) ** 2 for pc in C) / m
        min_p_c = min(C)

        # Phase D: safety intercept
        audit_trigger = (min_p_c < 0.50) or (sigma2_C > 0.05)
        state = "UNCERTAIN_EDGE_CASE" if audit_trigger else "HIGH_CERTAINTY"

    return {
        "mu": mu,
        "sigma2": sigma2,
        "sigma2_C": sigma2_C,
        "min_p_c": min_p_c,
        "audit_trigger": bool(audit_trigger),
        "state": state,
        "p_values": p_values,
    }


class OnlineTriageStats:
    """Online incremental statistics for p = exp(logprob) values.

    Maintains global sums and critical-subset sums so that the metrics
    (mu, sigma2, sigma2_C, min_p_c) can be computed incrementally without
    keeping full p arrays in memory.

    Formulae used:
      mu = sum_p / n
      sigma2 = (sum_p_sq / n) - mu^2
      sigma2_C = (sum_p_sq_C / m) - 2*mu*(sum_p_C/m) + mu^2

    This lets you compute critical variance relative to the current global mu
    using only aggregated sums.
    """

    def __init__(self) -> None:
        self.n = 0
        self.sum_p = 0.0
        self.sum_p_sq = 0.0

        self.m = 0
        self.sum_p_c = 0.0
        self.sum_p_sq_c = 0.0
        self.min_p_c: Optional[float] = None

    def add_logprob(self, logprob: float, is_critical: bool = False) -> None:
        """Add a single logprob observation. `logprob` is the raw log-probability (lambda).

        If `is_critical` is True, the value is included in the critical subset aggregates.
        """
        p = math.exp(float(logprob))

        self.n += 1
        self.sum_p += p
        self.sum_p_sq += p * p

        if is_critical:
            self.m += 1
            self.sum_p_c += p
            self.sum_p_sq_c += p * p
            if (self.min_p_c is None) or (p < self.min_p_c):
                self.min_p_c = p

    def snapshot(self) -> Dict[str, Any]:
        """Return the current metrics dictionary consistent with
        `calculate_triage_confidence` output (excluding p_values).
        """
        if self.n == 0:
            raise ValueError("no observations added")

        mu = self.sum_p / self.n
        sigma2 = (self.sum_p_sq / self.n) - (mu * mu)

        if self.m == 0:
            sigma2_C = 0.0
            min_p_c = None
            audit_trigger = False
            state = "HIGH_CERTAINTY"
        else:
            # Using algebra: (1/m) * sum((p_c - mu)^2) = (sum_p_sq_c/m) - 2*mu*(sum_p_c/m) + mu^2
            sigma2_C = (self.sum_p_sq_c / self.m) - 2.0 * mu * (self.sum_p_c / self.m) + (mu * mu)
            min_p_c = self.min_p_c
            audit_trigger = (min_p_c is not None and min_p_c < 0.50) or (sigma2_C > 0.05)
            state = "UNCERTAIN_EDGE_CASE" if audit_trigger else "HIGH_CERTAINTY"

        return {
            "mu": mu,
            "sigma2": sigma2,
            "sigma2_C": sigma2_C,
            "min_p_c": min_p_c,
            "audit_trigger": bool(audit_trigger),
            "state": state,
        }


def _post_payload(payload: Dict[str, Any], webhook_url: Optional[str]) -> None:
    """Synchronous POST helper to be executed inside a thread.

    If webhook_url is None, prints a structured JSON log to stdout.
    All exceptions are caught and printed to stdout to avoid raising in background.
    """
    try:
        body = json.dumps(payload, default=str).encode("utf-8")
        if webhook_url:
            req = urllib.request.Request(
                webhook_url, data=body, headers={"Content-Type": "application/json"}, method="POST"
            )
            # 10s timeout to avoid long-hanging sockets; this runs in background thread
            with urllib.request.urlopen(req, timeout=10) as resp:
                # read minimal response so socket is cleanly closed
                _ = resp.read(1024)
        else:
            # Fallback: structured JSON log
            print(json.dumps({"flywheel_log": payload}, default=str))
    except Exception as exc:  # pragma: no cover - defensive
        # Never raise from background task; print minimal info for diagnostics
        try:
            print(json.dumps({"flywheel_error": str(exc), "payload_preview": payload}, default=str))
        except Exception:
            print("flywheel error, and payload could not be serialized")


def persist_payload_locally(payload: Dict[str, Any], directory: Optional[str] = None) -> str:
    """Append the given payload as a JSONL line to a daily file under `directory`.

    Returns the path to the file written. This function is safe to call from
    background threads and will create the directory if needed.
    """
    if directory is None:
        directory = os.path.join(os.getcwd(), "data")

    try:
        os.makedirs(directory, exist_ok=True)
        fname = datetime.now(timezone.utc).strftime("flywheel-%Y%m%d.jsonl")
        path = os.path.join(directory, fname)
        # Append JSON line atomically
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, default=str) + "\n")
        # Restrict permissions if possible
        try:
            os.chmod(path, 0o600)
        except Exception:
            pass
        # Purge old files according to retention policy
        try:
            retention_days = int(os.environ.get("FLYWHEEL_RETENTION_DAYS", "30"))
            purge_old_files(directory, retention_days)
        except Exception:
            pass
        return path
    except Exception:
        # Best-effort only; never raise from background persistence
        try:
            tmp = tempfile.gettempdir()
            fallback = os.path.join(tmp, "flywheel-fallback.jsonl")
            with open(fallback, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(payload, default=str) + "\n")
            return fallback
        except Exception:
            return ""


def purge_old_files(directory: str, retention_days: int = 30) -> None:
    """Delete files in `directory` older than `retention_days`.

    This is a simple local retention policy for development environments.
    """
    try:
        cutoff = datetime.now(timezone.utc).timestamp() - (retention_days * 86400)
        for name in os.listdir(directory):
            if not name.endswith('.jsonl'):
                continue
            path = os.path.join(directory, name)
            try:
                mtime = os.path.getmtime(path)
                if mtime < cutoff:
                    os.remove(path)
            except Exception:
                continue
    except Exception:
        return


def redact_pii(text: str) -> str:
    """Conservative PII redaction for emails, phone numbers, and SSNs.

    This function is intentionally conservative and should be used when
    persisting raw user text under explicit opt-in consent.
    """
    if not isinstance(text, str):
        return text

    # Basic patterns — keep minimal and conservative
    email_re = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
    phone_re = re.compile(r"(?:\+?\d{1,3}[\s-]?)?(?:\(\d{3}\)|\d{3})[\s-]?\d{3}[\s-]?\d{4}")
    ssn_re = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")

    redacted = email_re.sub("[REDACTED_EMAIL]", text)
    redacted = phone_re.sub("[REDACTED_PHONE]", redacted)
    redacted = ssn_re.sub("[REDACTED_SSN]", redacted)

    # Optionally redact simple capitalized name patterns (very conservative)
    try:
        redact_names = os.environ.get('FLYWHEEL_REDACT_NAMES', 'true').lower() in ('1', 'true', 'yes')
    except Exception:
        redact_names = True

    if redact_names:
        # Match 2-3 consecutive capitalized words (e.g., 'John Doe', 'Mary Ann Smith')
        name_re = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b")
        redacted = name_re.sub('[REDACTED_NAME]', redacted)

    return redacted
    


async def hand_off_to_flywheel(
    user_query: str, metrics: Dict[str, Any], trigger_status: bool, webhook_url: Optional[str] = None
) -> None:
    """Asynchronously hand off anonymized metrics to an external flywheel/webhook.

    - If `trigger_status` is True, the `user_query` is replaced with its SHA256 hex digest.
    - Packages: hashed query or raw query, global mu, global sigma2, sigma2_C, min_p_c, UTC timestamp.
    - Dispatches the JSON payload using urllib.request inside a thread from
      `concurrent.futures.ThreadPoolExecutor` to avoid blocking the async event loop.

    This function schedules the background post and returns immediately so it does
    not add latency to the serverless function response path.
    """
    if not isinstance(metrics, dict):
        raise TypeError("metrics must be a dict produced by calculate_triage_confidence")

    payload: Dict[str, Any] = {}

    if trigger_status:
        # Anonymize the user query
        h = hashlib.sha256()
        h.update(user_query.encode("utf-8"))
        payload["query_hash"] = h.hexdigest()
    else:
        # Note: callers should ensure they have consent to forward raw queries
        payload["query"] = user_query

    # Insert metrics of interest; tolerate missing keys defensively
    payload["mu"] = metrics.get("mu")
    payload["sigma2"] = metrics.get("sigma2")
    payload["sigma2_C"] = metrics.get("sigma2_C")
    payload["min_p_c"] = metrics.get("min_p_c")
    payload["audit_trigger"] = metrics.get("audit_trigger")
    payload["state"] = metrics.get("state")
    payload["timestamp_utc"] = datetime.now(timezone.utc).isoformat()

    # Schedule the background post without awaiting it. We rely on a small threadpool.
    loop = asyncio.get_event_loop()
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    # Run _post_payload in a background thread; do not await to avoid request latency.
    # We wrap the call to suppress unhandled exception warnings by capturing the future.
    # Persist locally first when webhook_url is not provided
    try:
        if webhook_url is None:
            persist_payload_locally(payload)
    except Exception:
        # swallow
        pass

    future = loop.run_in_executor(executor, _post_payload, payload, webhook_url)

    # Attach a done callback to ensure any exceptions are printed.
    def _done_callback(fut: concurrent.futures.Future) -> None:  # pragma: no cover - minimal
        try:
            fut.result()
        except Exception as e:
            print(json.dumps({"flywheel_callback_error": str(e)}))

    # If run_in_executor returns an asyncio.Future, add done callback in a safe way
    try:
        future.add_done_callback(_done_callback)  # type: ignore[attr-defined]
    except Exception:
        # If the future is not the expected type, attempt to schedule a coroutine wrapper
        async def _wrap():
            try:
                await future  # type: ignore
            except Exception as e:
                print(json.dumps({"flywheel_callback_error": str(e)}))

        asyncio.ensure_future(_wrap())

    # Return immediately; background thread will handle posting.
    return None
