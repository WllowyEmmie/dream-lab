VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def to_int(numeral: str) -> int:
    """Convert a Roman numeral like "MCMXCIV" to an int."""
    total = 0
    for i, ch in enumerate(numeral):
        value = VALUES[ch]
        if i + 1 < len(numeral) - 1 and VALUES[numeral[i + 1]] > value:
            total -= value
        else:
            total += value
    return total
