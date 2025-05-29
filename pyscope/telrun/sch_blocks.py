def xpgtest_observing_blocks():
    """
    Create a list of ObservingBlock objects for testing BBScheduler.
    
    Returns
    -------
    list of ObservingBlock
        Test observhe oning blocks based on the provided .sch file
    """
    from astroplan import ObservingBlock, FixedTarget
    from astropy import units as u
    from astropy.coordinates import SkyCoord
    
    # Define test targets with approximate coordinates (for fast testing)
    test_targets = {
        'OJ 287': SkyCoord(ra=133.0, dec=20.1, unit='deg'),
        'Mrk 421': SkyCoord(ra=166.1, dec=38.2, unit='deg'), 
        '3C 273': SkyCoord(ra=187.3, dec=2.05, unit='deg'),
        '3C 279': SkyCoord(ra=194.0, dec=-5.8, unit='deg')
    }
    
    blocks = []
    
    # OJ 287 observations
    target_oj287 = FixedTarget(coord=test_targets['OJ 287'], name='OJ 287')
    
    # OJ 287 g filter, 60s exposure
    blocks.append(ObservingBlock(
        target=target_oj287,
        duration=2 * (60 + 0) * u.second,  # nexp=2, exposure=60s, readout=0s
        priority=1,
        configuration={'filter': 'g', 'binning': (2, 2), 'exposure': 60, 'nexp': 2},
        name='OJ287_g_60s'
    ))
    
    # OJ 287 g filter, 300s exposure  
    blocks.append(ObservingBlock(
        target=target_oj287,
        duration=2 * (300 + 0) * u.second,
        priority=1,
        configuration={'filter': 'g', 'binning': (2, 2), 'exposure': 300, 'nexp': 2},
        name='OJ287_g_300s'
    ))
    
    # OJ 287 lrg filter, 300s exposure
    blocks.append(ObservingBlock(
        target=target_oj287,
        duration=2 * (300 + 0) * u.second,
        priority=2,
        configuration={'filter': 'lrg', 'binning': (2, 2), 'exposure': 300, 'nexp': 2},
        name='OJ287_lrg_300s'
    ))
    
    # Mrk 421 observations
    target_mrk421 = FixedTarget(coord=test_targets['Mrk 421'], name='Mrk 421')
    
    blocks.append(ObservingBlock(
        target=target_mrk421,
        duration=2 * (60 + 0) * u.second,
        priority=3,
        configuration={'filter': 'g', 'binning': (2, 2), 'exposure': 60, 'nexp': 2},
        name='Mrk421_g_60s'
    ))
    
    blocks.append(ObservingBlock(
        target=target_mrk421,
        duration=2 * (300 + 0) * u.second,
        priority=3,
        configuration={'filter': 'g', 'binning': (2, 2), 'exposure': 300, 'nexp': 2},
        name='Mrk421_g_300s'
    ))
    
    blocks.append(ObservingBlock(
        target=target_mrk421,
        duration=2 * (300 + 0) * u.second,
        priority=4,
        configuration={'filter': 'lrg', 'binning': (2, 2), 'exposure': 300, 'nexp': 2},
        name='Mrk421_lrg_300s'
    ))
    
    # 3C 273 observations
    target_3c273 = FixedTarget(coord=test_targets['3C 273'], name='3C 273')
    
    blocks.append(ObservingBlock(
        target=target_3c273,
        duration=2 * (60 + 0) * u.second,
        priority=5,
        configuration={'filter': 'g', 'binning': (2, 2), 'exposure': 60, 'nexp': 2},
        name='3C273_g_60s'
    ))
    
    blocks.append(ObservingBlock(
        target=target_3c273,
        duration=2 * (300 + 0) * u.second,
        priority=5,
        configuration={'filter': 'g', 'binning': (2, 2), 'exposure': 300, 'nexp': 2},
        name='3C273_g_300s'
    ))
    
    # 3C 273 with multiple filters (lrg, hrg)
    blocks.append(ObservingBlock(
        target=target_3c273,
        duration=2 * (300 + 0) * u.second,
        priority=6,
        configuration={'filter': 'lrg', 'binning': (2, 2), 'exposure': 300, 'nexp': 2},
        name='3C273_lrg_300s'
    ))
    
    blocks.append(ObservingBlock(
        target=target_3c273,
        duration=2 * (300 + 0) * u.second,
        priority=6,
        configuration={'filter': 'hrg', 'binning': (2, 2), 'exposure': 300, 'nexp': 2},
        name='3C273_hrg_300s'
    ))
    
    # 3C 279 observations
    target_3c279 = FixedTarget(coord=test_targets['3C 279'], name='3C 279')
    
    blocks.append(ObservingBlock(
        target=target_3c279,
        duration=2 * (60 + 0) * u.second,
        priority=7,
        configuration={'filter': 'g', 'binning': (2, 2), 'exposure': 60, 'nexp': 2},
        name='3C279_g_60s'
    ))
    
    blocks.append(ObservingBlock(
        target=target_3c279,
        duration=2 * (300 + 0) * u.second,
        priority=7,
        configuration={'filter': 'g', 'binning': (2, 2), 'exposure': 300, 'nexp': 2},
        name='3C279_g_300s'
    ))
    
    blocks.append(ObservingBlock(
        target=target_3c279,
        duration=2 * (300 + 0) * u.second,
        priority=8,
        configuration={'filter': 'lrg', 'binning': (2, 2), 'exposure': 300, 'nexp': 2},
        name='3C279_lrg_300s'
    ))
    
    return blocks


def alc_observing_blocks():
    """
    Create a list of ObservingBlock objects based on alc.sch file.
    
    M57 observations in g, r, i filters with 30s and 60s exposures.
    
    Returns
    -------
    list of ObservingBlock
        Test observing blocks for M57 observations
    """
    from astroplan import ObservingBlock, FixedTarget
    from astropy import units as u
    from astropy.coordinates import SkyCoord
    
    # M57 (Ring Nebula) coordinates
    m57_coord = SkyCoord(ra=283.396333, dec=33.029278, unit='deg')  # J2000 coordinates
    target_m57 = FixedTarget(coord=m57_coord, name='M57')
    
    blocks = []
    priority = 1  # All blocks have same priority in this case
    
    # M57 g filter, 30s exposure (nexp defaults to 1)
    blocks.append(ObservingBlock(
        target=target_m57,
        duration=1 * (30 + 0) * u.second,  # nexp=1, exposure=30s, readout=0s
        priority=priority,
        configuration={'filter': 'g', 'binning': (2, 2), 'exposure': 30, 'nexp': 1, 'readout': 0},
        name='M57_g_30s'
    ))
    
    # M57 g filter, 60s exposure
    blocks.append(ObservingBlock(
        target=target_m57,
        duration=1 * (60 + 0) * u.second,
        priority=priority,
        configuration={'filter': 'g', 'binning': (2, 2), 'exposure': 60, 'nexp': 1, 'readout': 0},
        name='M57_g_60s'
    ))
    
    # M57 r filter, 30s exposure
    blocks.append(ObservingBlock(
        target=target_m57,
        duration=1 * (30 + 0) * u.second,
        priority=priority,
        configuration={'filter': 'r', 'binning': (2, 2), 'exposure': 30, 'nexp': 1, 'readout': 0},
        name='M57_r_30s'
    ))
    
    # M57 r filter, 60s exposure
    blocks.append(ObservingBlock(
        target=target_m57,
        duration=1 * (60 + 0) * u.second,
        priority=priority,
        configuration={'filter': 'r', 'binning': (2, 2), 'exposure': 60, 'nexp': 1, 'readout': 0},
        name='M57_r_60s'
    ))
    
    # M57 i filter, 30s exposure
    blocks.append(ObservingBlock(
        target=target_m57,
        duration=1 * (30 + 0) * u.second,
        priority=priority,
        configuration={'filter': 'i', 'binning': (2, 2), 'exposure': 30, 'nexp': 1, 'readout': 0},
        name='M57_i_30s'
    ))
    
    # M57 i filter, 60s exposure
    blocks.append(ObservingBlock(
        target=target_m57,
        duration=1 * (60 + 0) * u.second,
        priority=priority,
        configuration={'filter': 'i', 'binning': (2, 2), 'exposure': 60, 'nexp': 1, 'readout': 0},
        name='M57_i_60s'
    ))
    
    return blocks


def xpg1_observing_blocks():
    """
    Create a list of ObservingBlock objects based on xpg1.sch file.
    
    QSO observations for multiple targets with various filters and exposures.
    
    Returns
    -------
    list of ObservingBlock
        Test observing blocks for QSO observations
    """
    from astroplan import ObservingBlock, FixedTarget
    from astropy import units as u
    from astropy.coordinates import SkyCoord
    
    # Define test targets with approximate coordinates
    test_targets = {
        '1E 0754+39.3': SkyCoord(ra=119.25, dec=39.3, unit='deg'),
        'TON951': SkyCoord(ra=139.18, dec=34.61, unit='deg'),
        'HE1029-1401': SkyCoord(ra=157.75, dec=-14.27, unit='deg'),
        'Mrk 205': SkyCoord(ra=184.36, dec=75.31, unit='deg'),
        '3C 273': SkyCoord(ra=187.28, dec=2.05, unit='deg'),
        'PG1351': SkyCoord(ra=208.31596, dec=63.76269, unit='deg')  # Custom coordinates from file
    }
    
    blocks = []
    
    # 1E 0754+39.3 observations
    target_1e0754 = FixedTarget(coord=test_targets['1E 0754+39.3'], name='1E 0754+39.3')
    
    # 1E 0754+39.3 g filter, 60s exposure
    blocks.append(ObservingBlock(
        target=target_1e0754,
        duration=2 * (60 + 0) * u.second,  # nexp=2, exposure=60s, readout=0s
        priority=1,
        configuration={'filter': 'g', 'binning': (2, 2), 'exposure': 60, 'nexp': 2, 'repositioning': (2394, 1597)},
        name='1E0754_g_60s'
    ))
    
    # 1E 0754+39.3 g filter, 300s exposure
    blocks.append(ObservingBlock(
        target=target_1e0754,
        duration=2 * (300 + 0) * u.second,
        priority=1,
        configuration={'filter': 'g', 'binning': (2, 2), 'exposure': 300, 'nexp': 2, 'repositioning': (2394, 1597)},
        name='1E0754_g_300s'
    ))
    
    # 1E 0754+39.3 lrg filter, 300s exposure
    blocks.append(ObservingBlock(
        target=target_1e0754,
        duration=3 * (300 + 0) * u.second,  # nexp=3
        priority=2,
        configuration={'filter': 'lrg', 'binning': (2, 2), 'exposure': 300, 'nexp': 3, 'repositioning': (2394, 1597)},
        name='1E0754_lrg_300s'
    ))
    
    # TON951 observations
    target_ton951 = FixedTarget(coord=test_targets['TON951'], name='TON951')
    
    blocks.append(ObservingBlock(
        target=target_ton951,
        duration=2 * (60 + 0) * u.second,
        priority=3,
        configuration={'filter': 'g', 'binning': (2, 2), 'exposure': 60, 'nexp': 2, 'repositioning': (2394, 1597)},
        name='TON951_g_60s'
    ))
    
    blocks.append(ObservingBlock(
        target=target_ton951,
        duration=2 * (300 + 0) * u.second,
        priority=3,
        configuration={'filter': 'g', 'binning': (2, 2), 'exposure': 300, 'nexp': 2, 'repositioning': (2394, 1597)},
        name='TON951_g_300s'
    ))
    
    blocks.append(ObservingBlock(
        target=target_ton951,
        duration=3 * (300 + 0) * u.second,
        priority=4,
        configuration={'filter': 'lrg', 'binning': (2, 2), 'exposure': 300, 'nexp': 3, 'repositioning': (2394, 1597)},
        name='TON951_lrg_300s'
    ))
    
    # HE1029-1401 observations
    target_he1029 = FixedTarget(coord=test_targets['HE1029-1401'], name='HE1029-1401')
    
    blocks.append(ObservingBlock(
        target=target_he1029,
        duration=2 * (60 + 0) * u.second,
        priority=5,
        configuration={'filter': 'g', 'binning': (2, 2), 'exposure': 60, 'nexp': 2, 'repositioning': (2394, 1597)},
        name='HE1029_g_60s'
    ))
    
    blocks.append(ObservingBlock(
        target=target_he1029,
        duration=2 * (300 + 0) * u.second,
        priority=5,
        configuration={'filter': 'g', 'binning': (2, 2), 'exposure': 300, 'nexp': 2, 'repositioning': (2394, 1597)},
        name='HE1029_g_300s'
    ))
    
    blocks.append(ObservingBlock(
        target=target_he1029,
        duration=3 * (300 + 0) * u.second,
        priority=6,
        configuration={'filter': 'lrg', 'binning': (2, 2), 'exposure': 300, 'nexp': 3, 'repositioning': (2394, 1597)},
        name='HE1029_lrg_300s'
    ))
    
    # Mrk 205 observations
    target_mrk205 = FixedTarget(coord=test_targets['Mrk 205'], name='Mrk 205')
    
    blocks.append(ObservingBlock(
        target=target_mrk205,
        duration=2 * (60 + 0) * u.second,
        priority=7,
        configuration={'filter': 'g', 'binning': (2, 2), 'exposure': 60, 'nexp': 2, 'repositioning': (2394, 1597)},
        name='Mrk205_g_60s'
    ))
    
    blocks.append(ObservingBlock(
        target=target_mrk205,
        duration=2 * (300 + 0) * u.second,
        priority=7,
        configuration={'filter': 'g', 'binning': (2, 2), 'exposure': 300, 'nexp': 2, 'repositioning': (2394, 1597)},
        name='Mrk205_g_300s'
    ))
    
    # Mrk 205 lrg filter
    blocks.append(ObservingBlock(
        target=target_mrk205,
        duration=2 * (300 + 0) * u.second,
        priority=8,
        configuration={'filter': 'lrg', 'binning': (2, 2), 'exposure': 300, 'nexp': 2, 'repositioning': (2394, 1597)},
        name='Mrk205_lrg_300s'
    ))
    
    # Mrk 205 hrg filter
    blocks.append(ObservingBlock(
        target=target_mrk205,
        duration=2 * (300 + 0) * u.second,
        priority=8,
        configuration={'filter': 'hrg', 'binning': (2, 2), 'exposure': 300, 'nexp': 2, 'repositioning': (2394, 1597)},
        name='Mrk205_hrg_300s'
    ))
    
    # 3C 273 observations
    target_3c273 = FixedTarget(coord=test_targets['3C 273'], name='3C 273')
    
    blocks.append(ObservingBlock(
        target=target_3c273,
        duration=2 * (60 + 0) * u.second,
        priority=9,
        configuration={'filter': 'g', 'binning': (2, 2), 'exposure': 60, 'nexp': 2, 'repositioning': (2394, 1597)},
        name='3C273_g_60s'
    ))
    
    blocks.append(ObservingBlock(
        target=target_3c273,
        duration=2 * (300 + 0) * u.second,
        priority=9,
        configuration={'filter': 'g', 'binning': (2, 2), 'exposure': 300, 'nexp': 2, 'repositioning': (2394, 1597)},
        name='3C273_g_300s'
    ))
    
    blocks.append(ObservingBlock(
        target=target_3c273,
        duration=2 * (300 + 0) * u.second,
        priority=10,
        configuration={'filter': 'lrg', 'binning': (2, 2), 'exposure': 300, 'nexp': 2, 'repositioning': (2394, 1597)},
        name='3C273_lrg_300s'
    ))
    
    # PG1351 observations (with custom coordinates)
    target_pg1351 = FixedTarget(coord=test_targets['PG1351'], name='PG1351')
    
    blocks.append(ObservingBlock(
        target=target_pg1351,
        duration=2 * (60 + 0) * u.second,
        priority=11,
        configuration={'filter': 'g', 'binning': (2, 2), 'exposure': 60, 'nexp': 2, 'repositioning': (2394, 1597)},
        name='PG1351_g_60s'
    ))
    
    blocks.append(ObservingBlock(
        target=target_pg1351,
        duration=2 * (300 + 0) * u.second,
        priority=11,
        configuration={'filter': 'g', 'binning': (2, 2), 'exposure': 300, 'nexp': 2, 'repositioning': (2394, 1597)},
        name='PG1351_g_300s'
    ))
    
    # PG1351 lrg filter with both 60s and 300s exposures
    blocks.append(ObservingBlock(
        target=target_pg1351,
        duration=3 * (60 + 0) * u.second,  # nexp=3
        priority=12,
        configuration={'filter': 'lrg', 'binning': (2, 2), 'exposure': 60, 'nexp': 3, 'repositioning': (2394, 1597)},
        name='PG1351_lrg_60s'
    ))
    
    blocks.append(ObservingBlock(
        target=target_pg1351,
        duration=3 * (300 + 0) * u.second,
        priority=12,
        configuration={'filter': 'lrg', 'binning': (2, 2), 'exposure': 300, 'nexp': 3, 'repositioning': (2394, 1597)},
        name='PG1351_lrg_300s'
    ))
    
    return blocks


def get_all_test_blocks():
    """
    Get all test observing blocks from all available .sch file functions.
    
    Returns
    -------
    dict
        Dictionary with keys 'alc', 'xpg1', 'xpgtest' containing lists of blocks
    """
    return {
        'alc': alc_observing_blocks(),
        'xpg1': xpg1_observing_blocks(), 
        'xpgtest': xpgtest_observing_blocks()
    }


