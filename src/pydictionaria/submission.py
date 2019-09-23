from pathlib import Path

from clldutils import jsonlib
from clldutils.misc import lazyproperty
from clldutils.path import import_module
import attr

from pydictionaria.formats import FORMATS
from pydictionaria.util import MediaCatalog


@attr.s
class Language(object):
    name = attr.ib()
    glottocode = attr.ib()
    isocode = attr.ib(default=None)


@attr.s
class Metadata(object):
    authors = attr.ib()
    language = attr.ib()
    date_published = attr.ib()
    number = attr.ib(default=None)
    doi = attr.ib(default=None)
    properties = attr.ib(default=attr.Factory(dict))

    @classmethod
    def fromdict(cls, d):
        d['language'] = Language(**d['language'])
        return cls(**d)

    def asdict(self):
        return attr.asdict(self)

    @property
    def author_names(self):
        return ', '.join(a['name'] if isinstance(a, dict) else a for a in self.authors)


class Submission(object):
    def __init__(self, d, repos):
        self.dir = Path(d)
        self.repos = repos
        assert self.dir.exists()

    @lazyproperty
    def cdstar(self):
        return MediaCatalog(self.repos)

    @property
    def media_sids(self):
        res = self.md.properties.get('media_lookup', self.id)
        if not isinstance(res, list):
            res = [res]
        return res

    @lazyproperty
    def module(self):
        try:
            return import_module(self.dir)
        except (ImportError, AttributeError, TypeError):
            return

    @lazyproperty
    def dictionary(self):
        for impl in FORMATS:
            if impl.match(self):
                return impl(self)

    @lazyproperty
    def media(self):
        res = {}
        for mtype in ['audio', 'image', 'docs']:
            d = self.dir.joinpath(mtype)
            res[mtype] = list(d.iterdir()) if d.exists() else []
        return res

    @property
    def md(self):
        md_path = self.dir.joinpath('md.json')
        if md_path.exists():
            return Metadata.fromdict(jsonlib.load(self.dir.joinpath('md.json')))

    @md.setter
    def md(self, value):
        if isinstance(value, dict):
            value = Metadata.fromdict(value)
        jsonlib.dump(value.asdict(), self.dir.joinpath('md.json'), indent=4)

    @property
    def id(self):
        return self.dir.name
