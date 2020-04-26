import itertools

class BaseSetting:
    def __init_subclass__(cls, param_name, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._param_name = param_name

    @property
    def _alias(self):
        param = getattr(self, self.__class__._param_name)
        return param

    def __repr__(self):
        if self._alias is not None:
            return f'''[{self._param_name}:{self._fmt_param()}]'''
        return ""

    def _fmt_param(self):
        return self._alias


class Filter:
    def _fmt(self):
        raise NotImplementedError

    def __repr__(self):
        return self._fmt()

    def __add__(self, other):
        if isinstance(other, str):
            other = UserFilter(other)
        if isinstance(other, Filter):
            return CompoundFilter([self, other])
        if isinstance(other, CompoundFilter):
            filters = [f for f in other.filters]
            filters.append(self)
            return CompoundFilter(filters)
        else:
            raise NotImplementedError

    def __radd__(self, other):
        return self.__add__(other)

    def __iadd__(self, other):
        return self.__add__(other)


class CompoundFilter:
    def __init__(self, filters=[]):
        self._filters = filters

    @property
    def filters(self):
        return self._filters

    @filters.setter
    def filters(self, filters):
        if not self._filters:
            self._filters = filters
        else:
            raise AttributeError("Delete existing filters before assignment")

    @filters.deleter
    def filters(self):
        self._filters = []

    def __iter__(self):
        return iter(self.filters)

    def __repr__(self):
        return f'''{"".join(f._fmt() for f in self.filters)}'''

    def add_filter(self, other):
        if isinstance(other, str):
            other = UserFilter(other)
        if isinstance(other, Filter):
            self._filters.append(other)
            return
        if isinstance(other, CompoundFilter):
            self._filters.extend(other.filters)
            return
        else:
            raise NotImplementedError

    def __add__(self, other):
        if isinstance(other, str):
            other = UserFilter(other)
        if isinstance(other, Filter):
            filters = [f for f in self.filters]
            filters.append(other)
            return CompoundFilter(filters)
        if isinstance(other, CompoundFilter):
            filters = list(itertools.chain(self.filters, other.filters))
            return CompoundFilter(filters)
        else:
            raise NotImplementedError

    def __radd__(self, other):
        return self.__add__(other)

    def __iadd__(self, other):
        self.add_filter(other)
        return self


class AbstractQueryStatement:
    def _fmt_statement(self):
        raise NotImplementedError

    def __repr__(self):
        return f'''{self._fmt_statement()};'''

    def __add__(self, other):
        if isinstance(other, AbstractQueryStatement):
            return UnionQuerySet([self, other])
        raise NotImplementedError

    def __radd__(self, other):
        return self.__add__(other)

    def __iadd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, AbstractQueryStatement):
            # Check output type match
            return DifferenceQuerySet([self, other])
        raise NotImplementedError

    def __rsub__(self, other):
        return NotImplemented

    def __isub__(self, other):
        return self.__sub__(other)

    def union(self, other):
        return self + other

    def difference(self, other):
        return self - other

    def iunion(self, other):
        self += other

    def idifference(self, other):
        self -= other


class BaseQueryElement(AbstractQueryStatement):
    def __repr__(self):
        return f'''{self._fmt_statement()};'''


class BaseQuerySet(AbstractQueryStatement):
    def __repr__(self):
        return f'''({self._fmt_statement()});'''


class UnionQuerySet(BaseQuerySet):
    def __init__(self, query_statements=[]):
        self.query_statements = query_statements

    def _fmt_statement(self):
        return f'''{"".join(qf._fmt_statement() for qf in self.query_statements)}'''

    def __iter__(self):
        return iter(self.query_statements)


class DifferenceQuerySet(BaseQuerySet):
    def __init__(self, query_statements=[]):
        assert len(query_statements) == 2
        self.minued, self.subtrahend = query_statements

    def _fmt_statement(self):
        return f'''{self.minued} - {self.subtrahend}'''



