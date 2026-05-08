class Hit(dict):
    def __init__(self, data, pk_name=""):
        super().__init__(data)
        self.pk_name = pk_name
        self.id = data.get("id")
        self.distance = data.get("distance", 0.0)
        self.score = data.get("score", self.distance)
        self.entity = data.get("entity", {})

    def get(self, key, default=None):
        val = super().get(key)
        if val is not None:
            return val
        return self.entity.get(key, default)

    def __getitem__(self, key):
        if key in self:
            return super().__getitem__(key)
        return self.entity.get(key)


class HybridHits(list):
    def __init__(self, start=0, end=0, all_pks=None, all_scores=None,
                 fields_data=None, output_fields=None, highlight_results=None, pk_name=""):
        super().__init__()
        self.start = start
        self.end = end
        self.all_pks = all_pks or []
        self.all_scores = all_scores or []
        self.fields_data = fields_data or []
        self.output_fields = output_fields or []
        self.highlight_results = highlight_results or []
        self.pk_name = pk_name
        num_slots = end - start
        for _ in range(num_slots):
            super().append(None)

    def _first(self):
        if self and self[0] is not None:
            return self[0]
        return {}

    @property
    def id(self):
        first = self._first()
        return first.get("id") if hasattr(first, "get") else getattr(first, "id", None)

    @property
    def score(self):
        first = self._first()
        if hasattr(first, "score"):
            return first.score
        return first.get("score", 0.0) if hasattr(first, "get") else 0.0

    @property
    def distance(self):
        first = self._first()
        if hasattr(first, "distance"):
            return first.distance
        return first.get("distance", 0.0) if hasattr(first, "get") else 0.0

    def get(self, key, default=None):
        first = self._first()
        if hasattr(first, "get"):
            return first.get(key, default)
        return getattr(first, key, default)

    def __getitem__(self, key):
        if isinstance(key, str):
            first = self._first()
            if hasattr(first, "__getitem__"):
                return first[key]
            return getattr(first, key, None)
        return super().__getitem__(key)

    def __contains__(self, key):
        if isinstance(key, str):
            first = self._first()
            if hasattr(first, "__contains__"):
                return key in first
            return hasattr(first, key)
        return super().__contains__(key)


class _IdsData:
    def __init__(self):
        self.data = []

class _Ids:
    def __init__(self):
        self.int_id = _IdsData()
        self.str_id = _IdsData()

class SearchResultData:
    def __init__(self):
        self.primary_field_name = "id"
        self.ids = _Ids()
        self.scores = []
        self.topks = []
        self.output_fields = []

class SearchResult(list):
    def __init__(self, search_result_data):
        super().__init__()
        self._data = search_result_data
        for _ in range(len(search_result_data.topks)):
            super().append(None)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return self
        if index < len(self):
            return super().__getitem__(index)
        return HybridHits()
