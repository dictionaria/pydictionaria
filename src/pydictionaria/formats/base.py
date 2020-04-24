from pybtex.database import parse_file


class Dictionary(object):
    def __init__(self, submission):
        self.submission = submission

    @property
    def format(self):
        return self.__module__.split('.')[-1]

    @property
    def bib(self):
        return self.submission.dir.joinpath('sources.bib')

    @property
    def bibentries(self):
        if self.bib.exists():
            return parse_file(str(self.bib)).entries
        return {}

    def stat(self):
        raise NotImplemented()  # pragma: no cover

    @classmethod
    def match(cls, submission):
        raise NotImplemented()  # pragma: no cover

    def check(self):
        raise NotImplemented()  # pragma: no cover

    def process(self):
        outdir = self.submission.dir.joinpath('processed')
        if not outdir.exists():
            outdir.mkdir()
        return self._process(outdir)

    def _process(self, outdir):
        raise NotImplemented()  # pragma: no cover
