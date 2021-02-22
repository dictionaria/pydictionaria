from clldutils.sfm import SFM, Entry


def test_Stats():
    from pydictionaria.sfm_lib import Stats

    sfm = SFM()
    sfm.append(Entry([]))
    sfm.visit(Stats())
    sfm.append(Entry([('lx', 'lemma ; plus'), ('cf', 'x'), ('cf', 'y')]))
    stats = Stats()
    sfm.visit(stats)
    assert stats.count['lx'] == 1


def test_normalize():
    from pydictionaria.sfm_lib import normalize

    sfm = SFM([Entry([('sd', 'a__b')])])
    sfm.visit(normalize)
    assert sfm[0].get('sd') == 'a b'
