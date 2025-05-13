# -*- coding: utf-8 -*-
"""Tests for the schedtel module, focusing on basic_scheduler."""

import pytest
import datetime
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import SkyCoord, EarthLocation
from astroplan import Observer, FixedTarget, ObservingBlock
from astroplan import constraints as aplan_constraints

# Import the function to test (adjust path if necessary)
from pyscope.telrun.schedtel import basic_scheduler

# --- Fixtures --- 

@pytest.fixture
def test_location():
    """Provides a test EarthLocation."""
    # Using Palomar Observatory coordinates as an example
    return EarthLocation(lat=33.3563*u.deg, lon=-116.8648*u.deg, height=1706*u.m)

@pytest.fixture
def test_observer(test_location):
    """Provides a test Observer."""
    return Observer(location=test_location, name="TestObservatory", timezone="US/Pacific")

@pytest.fixture
def dummy_reconfig():
    """Provides a dummy reconfig object/function for transition time calculation."""
    class DummyReconfig:
        def calc_reconfig_time_blocks(self, block1, block2, location, verbose=False):
            # Return a fixed transition time for simplicity in tests
            return 60 * u.second
    return DummyReconfig()

@pytest.fixture
def target1():
    """A test target."""
    return FixedTarget(coord=SkyCoord(ra=10*u.deg, dec=20*u.deg), name="Target1")

@pytest.fixture
def target2():
    """Another test target."""
    return FixedTarget(coord=SkyCoord(ra=30*u.deg, dec=40*u.deg), name="Target2")

@pytest.fixture
def basic_block1(target1):
    """A basic observing block."""
    # Use ObservingBlock constructor directly
    return ObservingBlock(target1, 30*u.second, priority=1)

@pytest.fixture
def basic_block2(target2):
    """Another basic observing block."""
    # Use ObservingBlock constructor directly
    return ObservingBlock(target2, 60*u.second, priority=1)

# --- Test Cases --- 

def test_placeholder():
    """Placeholder test."""
    assert True

def test_basic_scheduling_success(test_observer, test_location, dummy_reconfig, basic_block1, basic_block2):
    """Tests scheduling two valid blocks sequentially."""
    # Define a plausible night window (e.g., for Palomar on 2025-05-08 UT)
    # Use observer to get rough times, then fix them for repeatable tests
    # approx_start = test_observer.sun_set_time(Time("2025-05-07 12:00:00"), which="next", horizon=-12*u.deg)
    # approx_end = test_observer.sun_rise_time(approx_start, which="next", horizon=-12*u.deg)
    # Let's use fixed times for the test
    night_start_time = Time("2025-05-08 03:00:00", scale="utc") # Approx UT night start
    night_end_time = Time("2025-05-08 12:00:00", scale="utc") # Approx UT night end

    # Mimic the block structure used internally (list of dicts)
    block1_dict = basic_block1.to_dict()
    # Use the duration calculated by ObservingBlock itself
    block1_dict['duration'] = basic_block1.duration 
    block2_dict = basic_block2.to_dict()
    block2_dict['duration'] = basic_block2.duration
    block_group = [block1_dict, block2_dict]

    # Standard constraints
    elevation = 30.0
    airmass = 3.0
    moon_separation = 30.0

    valid_blocks, invalid_blocks = basic_scheduler(
        block_group,
        night_start_time,
        night_end_time,
        last_block_end_time=None, # First group
        observatory=test_observer,
        reconfig_file=dummy_reconfig,
        elevation=elevation,
        airmass=airmass,
        moon_separation=moon_separation,
        location=test_location
    )

    # Assertions
    assert len(valid_blocks) == 2, "Both blocks should be scheduled"
    assert len(invalid_blocks) == 0, "No blocks should be invalid"

    # Check timing
    block1 = valid_blocks[0]
    block2 = valid_blocks[1]

    # First block should start at night_start_time (no preceding block)
    assert block1['start_time'] == night_start_time
    # End time includes its duration
    expected_block1_end = night_start_time + block1['duration']
    assert block1['end_time'] == expected_block1_end

    # Second block should start after the first block's end + transition time
    expected_transition = dummy_reconfig.calc_reconfig_time_blocks(block1, block2, test_location)
    expected_block2_start = block1['end_time'] + expected_transition
    assert block2['start_time'] == expected_block2_start
    # End time includes its duration
    expected_block2_end = expected_block2_start + block2['duration']
    assert block2['end_time'] == expected_block2_end

    # Ensure blocks end before night end
    assert block2['end_time'] < night_end_time

def test_scheduling_failure_time_window(test_observer, test_location, dummy_reconfig, basic_block1):
    """Tests that a block is rejected if it falls outside the night window."""
    # Create a very short night window
    night_start_time = Time("2025-05-08 03:00:00", scale="utc")
    # Make the end time just after the start time, shorter than block duration
    night_end_time = night_start_time + 10 * u.second 

    block1_dict = basic_block1.to_dict()
    # Use the duration calculated by ObservingBlock itself
    block1_dict['duration'] = basic_block1.duration # Ensure duration is longer than window (30s > 10s)
    block_group = [block1_dict]

    # Standard constraints (won't be reached)
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

    assert len(valid_blocks) == 0, "No blocks should be scheduled"
    assert len(invalid_blocks) == 1, "The block should be invalid"
    assert invalid_blocks[0]['target'].name == basic_block1.target.name
    assert "Outside night window" in invalid_blocks[0]['schedule_failure_reason']

def test_scheduling_failure_elevation(test_observer, test_location, dummy_reconfig, basic_block1):
    """Tests that a block is rejected if it violates the elevation constraint."""
    night_start_time = Time("2025-05-08 03:00:00", scale="utc")
    night_end_time = Time("2025-05-08 12:00:00", scale="utc")

    # Use a target that is likely below horizon at the start time
    # (e.g., RA near 180deg from the meridian at night start)
    low_target = FixedTarget(coord=SkyCoord(ra=180*u.deg, dec=-30*u.deg), name="LowTarget")
    # Use ObservingBlock constructor directly
    low_block = ObservingBlock(low_target, 30*u.second, priority=1)

    block_dict = low_block.to_dict()
    # Use the duration calculated by ObservingBlock itself
    block_dict['duration'] = low_block.duration 
    block_group = [block_dict]

    # Set a high elevation constraint that this target will violate
    elevation = 85.0 
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

    assert len(valid_blocks) == 0, "No blocks should be scheduled"
    assert len(invalid_blocks) == 1, "The block should be invalid"
    assert invalid_blocks[0]['target'].name == low_target.name
    assert "AltitudeConstraint" in invalid_blocks[0]['schedule_failure_reason']
