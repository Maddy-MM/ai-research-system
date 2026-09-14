import re


def strip_thinking(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def sum_tokens(messages) -> int:
    total = 0
    for m in messages:
        usage = getattr(m, "usage_metadata", None)
        if usage:
            total += usage.get("total_tokens", 0)
    return total
