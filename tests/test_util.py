from cdstarcat.catalog import Object, Bitstream


def test_split_ids():
    from pydictionaria.util import split_ids

    assert split_ids('c, b; b, a.') == ['a.', 'b', 'c']


def test_MediaCatalog(tmpdir):
    from pydictionaria.util import MediaCatalog

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
