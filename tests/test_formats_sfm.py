from clldutils.sfm import SFM, Entry


def test_normalize():
    from pydictionaria.sfm_lib import normalize

    sfm = SFM([Entry([('sd', 'a__b')])])
    sfm.visit(normalize)
    assert sfm[0].get('sd') == 'a b'
