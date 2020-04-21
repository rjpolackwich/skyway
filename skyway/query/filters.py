class QueryClause: pass


class IdFilter(QueryClause):
    def __init__(self, _id):
        self._id = _id

    def __repr__(self):
        return f'''(id:{self._id})'''


class BboxFilter(QueryClause):
    def __init__(self, bbox):
        self.bbox = bbox

    def __repr__(self):
        s, w, n, e = self.bbox
        return f'''{s:.2f},{w:.2f},{n:.2f},{e:.2f}'''


class KeySpec:
    def __init__(self, key, exists=True):
        if key.startswith("!"):
            if not exists:
                raise AttributeError("Input existence conflict")
            key = key.strip("!")
            exists = False
        self.key = key
        self.exists = exists

    def __bool__(self):
        return self.exists

    def __repr__(self):
        s = f'''{self.key}'''
        if not self.exists:
            return "!" + s
        return s



def format_values(vals):
    if isinstance(vals, str):
        return f'''={vals}'''
    if isinstance(vals, list):
        if len(vals) == 1:
            val = vals[0]
            return f'''={val}'''
        else:
            svals = "|".join(vals)
            return f'''~"^({svals})$"'''


class TagFilter(QueryClause):
    def __init__(self, key, vals=[], exists=True):
        if not vals:
            self.key = KeySpec(key, exists=exists)
        else:
            self.key = KeySpec(key)
        self.vals = vals
        self.exists = exists

    def __repr__(self):
        if not self.key.exists:
            return f'''[{self.key}]'''
        if not self.vals:
            return f'''[{self.key}]'''
        svals = format_values(self.vals)
        if self.exists:
            return f'''{self.key}{svals}'''
        return f'''[{self.key}][{self.key}!{svals}]'''





