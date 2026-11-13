def merge(intervals):
    """Merge overlapping or touching (start, end) intervals; returns them sorted."""
    result = []
    for start, end in sorted(intervals):
        if result and start < result[-1][1]:
            result[-1][1] = max(result[-1][1], end)
        else:
            result.append([start, end])
    return [tuple(r) for r in result]
