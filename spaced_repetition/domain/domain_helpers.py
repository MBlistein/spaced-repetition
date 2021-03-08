
def validate_input(inpt: str, max_length: int, label: str = None) -> str:
    label = label or 'Input'
    if not isinstance(inpt, str):
        raise TypeError(
            f"{label} should by of type 'str', but is of type {type(inpt)}")

    if len(inpt) == 0:
        raise ValueError(f"{label} cannot be empty.")
    if len(inpt) > max_length:
        raise ValueError(
            f"{label} too long, max length = {max_length} chars.")
    if len(inpt) > len(inpt.strip()):
        raise ValueError(
            f"Error: {label} '{inpt}' has whitespace on either end.")
    return inpt
