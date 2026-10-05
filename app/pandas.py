import csv

def _safe_float_val(x):
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        s = x.strip()
        s_check = s[1:] if s.startswith('-') else s
        if s_check.replace('.', '', 1).isdigit():
            try:
                return float(s)
            except ValueError:
                pass
    return x

class Series(list):
    def __init__(self, data=None):
        if data is None: data = []
        super().__init__([_safe_float_val(x) for x in data])
        
    def replace(self, to_rep, val):
        return Series([val if x == to_rep else x for x in self])
        
    def clip(self, lower=None, upper=None):
        res = []
        for x in self:
            try:
                v = float(x)
                if lower is not None and v < lower: v = lower
                if upper is not None and v > upper: v = upper
                res.append(v)
            except:
                res.append(x)
        return Series(res)

    def apply(self, func):
        return Series([func(x) for x in self])

    def astype(self, dtype):
        return self

    def notna(self):
        return Series([x is not None and str(x) != '' and str(x) != 'nan' for x in self])

    def isna(self):
        return Series([x is None or str(x) == '' or str(x) == 'nan' for x in self])

    @property
    def iloc(self):
        return self

    def tolist(self):
        return list(self)

    def unique(self):
        seen = []
        for x in self:
            if x not in seen: seen.append(x)
        return seen
        
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Series([float(x) / other if other != 0 else 0.0 for x in self])
        return Series([float(x) / float(y) if float(y) != 0 else 0.0 for x, y in zip(self, other)])

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Series([float(x) * other for x in self])
        return Series([float(x) * float(y) for x, y in zip(self, other)])

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return Series([float(x) + other for x in self])
        return Series([float(x) + float(y) for x, y in zip(self, other)])

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return Series([float(x) - other for x in self])
        return Series([float(x) - float(y) for x, y in zip(self, other)])

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            return Series([other - float(x) for x in self])
        return Series([float(y) - float(x) for x, y in zip(self, other)])

    def abs(self):
        return Series([abs(float(x)) for x in self])

    def __abs__(self):
        return Series([abs(float(x)) for x in self])

    def fillna(self, val):
        return Series([val if (x is None or x == "" or x == "nan" or (isinstance(x, float) and str(x) == "nan")) else x for x in self])

    def map(self, mapper):
        res = []
        for x in self:
            key = x[0] if isinstance(x, list) and x else x
            res.append(mapper.get(key, None))
        return Series(res)

    @property
    def str(self):
        class _Str:
            def __init__(self, parent): self.parent = parent
            def split(self, pat=','):
                return Series([str(x).split(pat) for x in self.parent])
            def replace(self, pat, repl):
                return Series([str(x).replace(pat, repl) for x in self.parent])
            def strip(self):
                return Series([str(x).strip() for x in self.parent])
            def contains(self, pat):
                import re
                return Series([bool(re.search(pat, str(x))) for x in self.parent])
            def __getitem__(self, idx):
                res = []
                for x in self.parent:
                    if isinstance(x, list):
                        res.append(x[idx] if 0 <= idx < len(x) else '')
                    else:
                        res.append(str(x)[idx] if 0 <= idx < len(str(x)) else '')
                return Series(res)
        return _Str(self)

    def round(self, decimals=0):
        return Series([round(float(x), decimals) for x in self])

    def __eq__(self, other):
        return Series([x == other for x in self])

    def __ne__(self, other):
        return Series([x != other for x in self])

    def __gt__(self, other):
        return Series([x > other for x in self])

    def __ge__(self, other):
        return Series([x >= other for x in self])

    def __lt__(self, other):
        return Series([x < other for x in self])

    def __le__(self, other):
        return Series([x <= other for x in self])

    def __and__(self, other):
        if isinstance(other, Series):
            return Series([bool(a) and bool(b) for a, b in zip(self, other)])
        return Series([bool(x) and bool(other) for x in self])

    def __or__(self, other):
        if isinstance(other, Series):
            return Series([bool(a) or bool(b) for a, b in zip(self, other)])
        return Series([bool(x) or bool(other) for x in self])

class DataFrame:
    def __init__(self, data=None, columns=None):
        if data is None:
            self._data = []
            self.columns = []
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            self._data = data
            self.columns = list(data[0].keys())
        elif isinstance(data, list) and data and isinstance(data[0], list):
            self.columns = columns if columns else [f"col_{i}" for i in range(len(data[0]))]
            self._data = [dict(zip(self.columns, row)) for row in data]
        else:
            self._data = []
            self.columns = columns if columns else []

    @property
    def empty(self):
        return len(self._data) == 0

    def __len__(self):
        return len(self._data)

    def __getitem__(self, item):
        if isinstance(item, str):
            return Series([row.get(item, '') for row in self._data])
        elif isinstance(item, Series):
            new_data = [row for row, flag in zip(self._data, item) if bool(flag)]
            return DataFrame(new_data)
        elif isinstance(item, list):
            new_data = [{k: row.get(k, '') for k in item if k in row} for row in self._data]
            return DataFrame(new_data)
        return self

    def __setitem__(self, key, value):
        if isinstance(value, Series):
            value = list(value)
        if isinstance(value, list):
            for i, row in enumerate(self._data):
                if i < len(value):
                    row[key] = value[i]
        else:
            for row in self._data:
                row[key] = value
        if key not in self.columns:
            self.columns.append(key)

    def merge(self, right, on=None, how='left'):
        if not isinstance(right, DataFrame):
            return self
        right_map = {}
        for r in right._data:
            k = tuple(r.get(col) for col in on) if isinstance(on, list) else r.get(on)
            right_map[k] = r
            
        merged_data = []
        for l in self._data:
            k = tuple(l.get(col) for col in on) if isinstance(on, list) else l.get(on)
            r_info = right_map.get(k, {})
            new_row = dict(l)
            for r_k, r_v in r_info.items():
                if r_k not in new_row:
                    new_row[r_k] = r_v
            merged_data.append(new_row)
        return DataFrame(merged_data)

    def sort_values(self, by=None, ascending=True):
        if not by: return self
        sorted_data = sorted(self._data, key=lambda x: _safe_float_val(x.get(by, 0)), reverse=not ascending)
        return DataFrame(sorted_data)

    def head(self, n=5):
        return DataFrame(self._data[:n])

    def copy(self):
        return DataFrame([dict(r) for r in self._data])

    def rename(self, columns=None):
        if not columns: return self
        new_data = []
        for row in self._data:
            new_row = {}
            for k, v in row.items():
                new_k = columns.get(k, k)
                new_row[new_k] = v
            new_data.append(new_row)
        return DataFrame(new_data)

    def to_dict(self, orient='records'):
        if orient == 'records':
            return self._data
        return {col: [r.get(col) for r in self._data] for col in self.columns}

    def iterrows(self):
        for i, row in enumerate(self._data):
            yield i, row

    @property
    def iloc(self):
        class _ILoc:
            def __init__(self, parent): self.parent = parent
            def __getitem__(self, idx): return self.parent._data[idx]
        return _ILoc(self)

def read_csv(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    return DataFrame(data)

def to_numeric(series, errors='coerce'):
    if isinstance(series, Series):
        res = []
        for x in series:
            try: res.append(float(x))
            except: res.append(0.0)
        return Series(res)
    return series
