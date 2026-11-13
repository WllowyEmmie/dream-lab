def split_line(line: str) -> list:
    """Split one CSV line on commas.

    Fields may be wrapped in double quotes. Inside quotes, commas are part of
    the field and "" stands for one double-quote character.
    """
    fields, current, quoted, i = [], [], False, 0
    while i < len(line):
        ch = line[i]
        if quoted:
            if ch == '"':
                quoted = False
            else:
                current.append(ch)
        elif ch == '"':
            quoted = True
        elif ch == ",":
            fields.append("".join(current))
            current = []
        else:
            current.append(ch)
        i += 1
    fields.append("".join(current))
    return fields
