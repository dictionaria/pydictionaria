import sys
import re
from collections import OrderedDict

from clldutils import jsonlib
from clldutils.path import Path
import requests
from requests.packages.urllib3.exceptions import (
    InsecurePlatformWarning, SNIMissingWarning,
)
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
requests.packages.urllib3.disable_warnings(SNIMissingWarning)


PY3 = sys.version_info[0] == 3
ID_SEP_PATTERN = re.compile(r',|;')


def split_ids(s, sep=ID_SEP_PATTERN):
    return sorted(set(id_.strip() for id_ in sep.split(s) if id_.strip()))


class MediaCatalog(object):
    def __init__(self, repos):
        self.path = Path(repos).joinpath('cdstar.json')
        if self.path.exists():
            self.items = jsonlib.load(self.path, object_pairs_hook=OrderedDict)
        else:
            self.items = OrderedDict()

    def __contains__(self, item):
        return item in self.items

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        jsonlib.dump(self.items, self.path, indent=4)

    def add(self, obj, **kw):
        """
        :param obj: A `cdstarcat.catalog.Object` instance
        :return:
        """
        bitstreams = {bs.id.split('.')[0]: bs for bs in obj.bitstreams}
        res = OrderedDict([('objid', obj.id)])
        thumbnail = bitstreams.pop('thumbnail', None)
        web = bitstreams.pop('web', None)
        assert len(bitstreams) == 1
        original = list(bitstreams.values())[0]
        res['mimetype'] = original.mimetype
        res['original'] = original.id
        res['size'] = original.size
        res['thumbnail'] = thumbnail.id if thumbnail else None
        res['web'] = web.id if web else None
        for k in sorted(kw):
            res[k] = kw[k]
        self.items[original.md5] = res
