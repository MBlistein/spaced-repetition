
def validate_param(param: str, max_length: int, label: str = None,
                   empty_allowed=False) -> str:
    label = label or 'Input'
    if not isinstance(param, str):
        raise TypeError(
            f"{label} should by of type 'str', but is of type {type(param)}")

    if len(param) == 0 and not empty_allowed:
        raise ValueError(f"{label} cannot be empty.")
    if len(param) > max_length:
        raise ValueError(
            f"{label} too long, max length = {max_length} chars.")
    if len(param) > len(param.strip()):
        raise ValueError(
            f"Error: {label} '{param}' has whitespace on either end.")
    return param
