import pytest
from astropy import units as u
from astropy import time as astrotime
from astropy.coordinates import SkyCoord, EarthLocation
from astroplan import Observer, FixedTarget
import datetime
from astropy.coordinates import Angle

from pyscope.telrun.schedtel_vini import (
    basic_scheduler,
    DummyReconfig,
    max_altitude
)

# Common fixtures
@pytest.fixture
def test_location():
    """Returns a test observatory location"""
    return EarthLocation(lat=33.356*u.deg, lon=-116.863*u.deg, height=1712*u.m)

@pytest.fixture
def test_observer(test_location):
    """Returns an observer at the test location"""
    return Observer(location=test_location)

@pytest.fixture
def test_block():
    """Returns a basic test observation block"""
    target = FixedTarget(SkyCoord.from_name('M31'))
    return {
        "ID": astrotime.Time.now().mjd,
        "name": "test_observation",
        "target": target,
        "target_ra": target.ra.deg,
        "target_dec": target.dec.deg,
        "duration": 30 * u.minute,
        "filter": 'R',
        "exposure": 300,
        "nexp": 6,
        "priority": 1,
        "constraints": None,
        "start_time": None,
        "end_time": None,
        "status": "U",
        "message": "Unscheduled",
        "observer": ["observer1"],
        "code": "test",
        "title": "Test Observation",
        "filename": "",
        "pm_ra_cosdec": 0 * u.arcsec/u.hour,
        "pm_dec": 0 * u.arcsec/u.hour,
    }

def test_basic_scheduling_success(test_block):
    """Test that a single block can be scheduled successfully"""
    schedule = []
    block_group = [test_block]
    scheduled_blocks = basic_scheduler(block_group, schedule)
    
    assert len(scheduled_blocks) == 1
    assert scheduled_blocks[0]['status'] == 'S'
    assert scheduled_blocks[0]['message'] == 'Scheduled successfully'
    assert scheduled_blocks[0]['start_time'] is not None
    assert scheduled_blocks[0]['end_time'] is not None
    assert scheduled_blocks[0]['end_time'] > scheduled_blocks[0]['start_time']

def test_scheduling_with_existing_schedule(test_block):
    """Test scheduling when there's an existing schedule"""
    # Create an existing schedule with one block
    existing_block = test_block.copy()
    current_time = astrotime.Time.now()
    existing_block['start_time'] = current_time
    existing_block['end_time'] = current_time + 1*u.hour
    existing_schedule = [existing_block]
    
    # Create new block to schedule
    new_block = test_block.copy()
    new_block['name'] = 'second_observation'
    block_group = [new_block]
    
    scheduled_blocks = basic_scheduler(block_group, existing_schedule)
    
    assert len(scheduled_blocks) > 0
    assert scheduled_blocks[-1]['start_time'] > existing_block['end_time']

def test_scheduling_with_transition_time():
    """Test that transition time is properly added between blocks"""
    target1 = FixedTarget(SkyCoord.from_name('M31'))
    target2 = FixedTarget(SkyCoord.from_name('M51'))
    
    block1 = {
        "ID": astrotime.Time.now().mjd,
        "name": "first_observation",
        "target": target1,
        "target_ra": target1.ra.deg,
        "target_dec": target1.dec.deg,
        "duration": 15 * u.minute,
        "filter": 'R',
        "exposure": 300,
        "nexp": 3,
        "priority": 1,
        "constraints": None,
        "start_time": None,
        "end_time": None,
        "status": "U",
        "message": "Unscheduled",
        "observer": ["observer1"],
        "code": "test",
        "title": "First Test",
        "filename": "",
        "pm_ra_cosdec": 0 * u.arcsec/u.hour,
        "pm_dec": 0 * u.arcsec/u.hour,
    }
    
    block2 = block1.copy()
    block2.update({
        "name": "second_observation",
        "target": target2,
        "target_ra": target2.ra.deg,
        "target_dec": target2.dec.deg,
    })
    
    schedule = []
    block_group = [block1, block2]
    scheduled_blocks = basic_scheduler(block_group, schedule)
    
    assert len(scheduled_blocks) == 2
    # Check that there's at least the transition time between blocks
    time_between_blocks = scheduled_blocks[1]['start_time'] - scheduled_blocks[0]['end_time']
    assert time_between_blocks >= 30 * u.second

def test_night_time_boundaries():
    """Test that scheduling respects night time boundaries"""
    target = FixedTarget(SkyCoord.from_name('M31'))
    test_block = {
        "ID": astrotime.Time.now().mjd,
        "name": "night_boundary_test",
        "target": target,
        "target_ra": target.ra.deg,
        "target_dec": target.dec.deg,
        "duration": 2 * u.hour,  # Long duration to test boundaries
        "filter": 'R',
        "exposure": 300,
        "nexp": 6,
        "priority": 1,
        "constraints": None,
        "start_time": None,
        "end_time": None,
        "status": "U",
        "message": "Unscheduled",
        "observer": ["observer1"],
        "code": "test",
        "title": "Night Boundary Test",
        "filename": "",
        "pm_ra_cosdec": 0 * u.arcsec/u.hour,
        "pm_dec": 0 * u.arcsec/u.hour,
    }
    
    schedule = []
    block_group = [test_block]
    scheduled_blocks = basic_scheduler(block_group, schedule)
    
    # Get night boundaries for verification
    current_time = astrotime.Time(datetime.datetime.now(), format="datetime")
    observer = Observer(location=EarthLocation(lat=33.356*u.deg, lon=-116.863*u.deg, height=1712*u.m))
    sunset = observer.sun_set_time(current_time, which="next", horizon=max_altitude*u.deg)
    sunrise = observer.sun_rise_time(sunset, which="next", horizon=max_altitude*u.deg)
    
    assert len(scheduled_blocks) > 0
    assert scheduled_blocks[0]['start_time'] >= sunset
    assert scheduled_blocks[0]['end_time'] <= sunrise

def test_dummy_reconfig():
    """Test that DummyReconfig returns expected transition time"""
    reconfig = DummyReconfig()
    block1 = {"name": "test1"}
    block2 = {"name": "test2"}
    
    transition_time = reconfig.calc_reconfig_time_blocks(block1, block2, None)
    assert transition_time == 30 * u.second