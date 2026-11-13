def wrap(text: str, width: int) -> list:
    """Greedy word wrap: no line is longer than width unless one word is."""
    lines, line = [], ""
    for word in text.split():
        if not line:
            line = word
        elif len(line) + len(word) <= width:
            line += " " + word
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines
