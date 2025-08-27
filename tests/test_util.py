from cdstarcat.catalog import Object, Bitstream
from pydictionaria.util import MediaCatalog, split_ids


def test_split_ids():
    assert split_ids('c, b; b, a.') == ['a.', 'b', 'c']


def test_mediacatalog_obj(tmpdir):
    with MediaCatalog(str(tmpdir)) as mcat:
        assert 'md5' not in mcat
        mcat.add(Object(
            'item',
            [
                Bitstream('web', '', '', '', '', ''),
                Bitstream('orig', '', '', 'md5', '', ''),
            ],
            {}))

    mcat = MediaCatalog(str(tmpdir))
    assert 'md5' in mcat
