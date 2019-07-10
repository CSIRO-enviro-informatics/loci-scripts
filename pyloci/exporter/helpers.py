# -*- coding: utf-8 -*-
#
def chunks(source, length):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(source), length):
        yield source[i:i + length]

def ld_find_subject(resource, subject_id):
    assert isinstance(resource, (list, tuple))
    for part in resource:
        try:
            identifier = part['@id']
        except (KeyError, AttributeError):
            continue
        if str(identifier) == str(subject_id):
            return part
    return None
