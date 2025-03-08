
def str_to_bool(s: str) -> bool:
    assert s.lower() in ["true", "false"], "str_to_bool: s should be either true or false, got: " + s
    return s.lower() == "true"

def remove_code_blocks(s: str) -> str:
    return s.replace("```python", "").replace("```", "").strip()