# -*- coding: utf-8 -*-

import pytest
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import SkyCoord, EarthLocation
from astroplan import Observer, FixedTarget, ObservingBlock
from astropy.time import Time
from pyscope.telrun.schedcore import basic_scheduler

# Import your scheduling function

# --- Fixtures --- 

@pytest.fixture
def test_location():
    """Test location: Palomar Observatory."""
    return EarthLocation(lat=33.3563*u.deg, lon=-116.8648*u.deg, height=1706*u.m)

@pytest.fixture
def test_observer(test_location):
    """Returns an Observer object for the test."""
    return Observer(location=test_location, name="TestObservatory", timezone="US/Pacific")

@pytest.fixture
def dummy_reconfig():
    """Dummy reconfiguration time calculator."""
    class DummyReconfig:
        def calc_reconfig_time_blocks(self, block1, block2, location, verbose=False):
            return 30 * u.second  # constant transition time
    return DummyReconfig()

@pytest.fixture
def sirius_target():
    """Returns Sirius as a FixedTarget."""
    return FixedTarget.from_name("Sirius")

@pytest.fixture
def sirius_block(sirius_target):
    """Returns a basic observing block for Sirius."""
    exposure_time = 60 * u.second
    return ObservingBlock(sirius_target, exposure_time, priority=1)

# --- Test Case ---

def test_sirius_basic_scheduling_success(test_observer, test_location, dummy_reconfig):
    """Tests scheduling a Sirius block successfully within constraints."""
    night_start_time = Time("2025-05-08 03:00:00", scale="utc")
    night_end_time = Time("2025-05-08 12:00:00", scale="utc")

    # Define Sirius target
    sirius = FixedTarget.from_name("Sirius")
    exposure_time = 60 * u.second
    sirius_block = ObservingBlock(sirius, exposure_time, priority=1)

    # Convert to dict and inject duration
    block_dict = sirius_block.to_dict()
    block_dict['duration'] = sirius_block.duration
    block_group = [block_dict]

    elevation = 30.0
    airmass = 3.0
    moon_separation = 30.0

    valid_blocks, invalid_blocks = basic_scheduler(
        block_group,
        night_start_time,
        night_end_time,
        last_block_end_time=None,
        observatory=test_observer,
        reconfig_file=dummy_reconfig,
        elevation=elevation,
        airmass=airmass,
        moon_separation=moon_separation,
        location=test_location
    )

    assert len(valid_blocks) == 1, "Sirius block should be scheduled successfully"
    assert len(invalid_blocks) == 0, "No blocks should be invalid"

    scheduled_block = valid_blocks[0]
    assert scheduled_block['target'].name == "Sirius"
    assert scheduled_block['start_time'] == night_start_time
    assert scheduled_block['end_time'] == night_start_time + scheduled_block['duration']
