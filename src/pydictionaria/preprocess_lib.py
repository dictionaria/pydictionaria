from collections import OrderedDict


def _split_senses(entry):
    senses = []
    next_sense = entry.__class__()
    for marker, content in entry:
        if marker == 'sn':
            if next_sense:
                senses.append(next_sense)
            next_sense = entry.__class__()
        next_sense.append((marker, content))
    if next_sense:
        senses.append(next_sense)
    return senses


def marker_fallback_entry(sense, target, source):
    """When entry marker `target` is empty or missing, try and fall back to `source`."""
    has_target = bool(sense.get(target))
    if has_target:
        return sense

    new = sense.__class__()
    for marker, content in sense:
        if marker == target and not has_target:
            continue
        if marker == source and content and not has_target:
            new.append((target, content.replace('_', ' ')))
            has_target = True
        new.append((marker, content))
    return new


def marker_fallback_sense(entry, target, source):
    """When sense marker `target` is empty or missing, try and fall back to `source`."""
    new_senses = [
        marker_fallback_entry(s, target, source)
        for s in _split_senses(entry)]
    return entry.__class__(
        pair
        for sense in new_senses
        for pair in sense)


def merge_caption(marker_dict):
    """Treat first value as a caption to the rest."""
    values = list(marker_dict.values())
    if not values:
        return ''
    elif len(values) == 1:
        return values[0]
    else:
        return '{}: {}'.format(values[0], ' '.join(values[1:]))


def merge_markers(entry, old_markers, new_marker, format_fn=merge_caption):
    """Merge a number of adjacent SFM markers into one.

    The values for all `old_markers` are combined and assiged to `new_marker`.

    It is also possible to define a `format_fn` to manipulate the value assigned
    to `new_marker`.  This function receives an ordered dictionary of
    marker--value pairs as its argument and is expected to return a new value as
    a string.

    """
    # Note: this assumes that the markers are adjacent to each other
    new_entry = entry.__class__()
    current = OrderedDict()
    for marker, value in entry:
        if marker in old_markers:
            if marker in current:
                new_entry.append((new_marker, format_fn(current)))
                current = OrderedDict()
            current[marker] = value
        else:
            if current:
                new_entry.append((new_marker, format_fn(current)))
                current = OrderedDict()
            new_entry.append((marker, value))
    if current:
        new_entry.append((new_marker, format_fn(current)))
    return new_entry
