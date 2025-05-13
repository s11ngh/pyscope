import logging
from pathlib import Path

import pytest
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
from astroplan import Observer, FixedTarget
import datetime
import zoneinfo

from pyscope.telrun import plot_schedule_gantt, plot_schedule_sky, schedtel
from pyscope.telrun.schedtel import basic_scheduler


def test_schedtel(tmp_path):
    logging.basicConfig(level=logging.INFO)

    catalog = "./tests/bin/test_utstart.cat"
    observatory = "./tests/bin/simulator_observatory.cfg"

    schedule = schedtel(
        catalog=catalog,
        observatory=observatory,
        filename=str(tmp_path) + "test_schedtel.ecsv",
    )

    # schedule = "./tests/bin/test_schedtel.ecsv"

    fig, ax = plot_schedule_gantt(schedule, observatory)
    fig.savefig(str(tmp_path) + "test_schedtel_gantt.png", bbox_inches="tight")

    fig, ax = plot_schedule_sky(schedule, observatory)
    fig.savefig(str(tmp_path) + "test_schedtel_sky.png", bbox_inches="tight")


@pytest.fixture
def sample_observatory():
    """Create a sample observatory for testing"""
    location = EarthLocation(lat=34.0*u.deg, lon=-118.0*u.deg, height=300*u.m)
    return Observer(location=location)

@pytest.fixture
def sample_block():
    """Create a sample observing block"""
    target = FixedTarget(SkyCoord(ra='02h00m00s', dec='+30d00m00s'))
    return {
        'target': target,
        'start_time': None,
        'end_time': None,
        'duration': 30 * u.minute,
        'constraints': None,
        'filter': 'r',
        'exposure': 60 * u.second,
        'nexp': 1
    }

def test_basic_block_scheduling(sample_observatory, sample_block):
    """Test scheduling a single block"""
    block_group = [sample_block]
    schedule = []
    
    # Use current date for testing
    test_date = datetime.datetime.now(zoneinfo.ZoneInfo('UTC'))
    
    scheduled_blocks = basic_scheduler(block_group, schedule)
    
    assert len(scheduled_blocks) == 1
    assert scheduled_blocks[0]['start_time'] is not None
    assert scheduled_blocks[0]['end_time'] is not None
    assert scheduled_blocks[0]['end_time'] > scheduled_blocks[0]['start_time']

def test_multiple_block_scheduling(sample_observatory, sample_block):
    """Test scheduling multiple blocks in sequence"""
    # Create two blocks with same target
    block1 = sample_block.copy()
    block2 = sample_block.copy()
    block_group = [block1, block2]
    schedule = []
    
    scheduled_blocks = basic_scheduler(block_group, schedule)
    
    assert len(scheduled_blocks) == 2
    # Check that second block starts after first block ends
    assert scheduled_blocks[1]['start_time'] >= scheduled_blocks[0]['end_time']

def test_constraint_handling(sample_observatory, sample_block):
    """Test handling of time constraints"""
    # Add a time constraint to the block
    test_time = Time.now()
    constraint_time = test_time + 1*u.hour
    sample_block['constraints'] = [{
        'min': constraint_time
    }]
    block_group = [sample_block]
    schedule = []
    
    scheduled_blocks = basic_scheduler(block_group, schedule)
    
    assert len(scheduled_blocks) == 1
    assert scheduled_blocks[0]['start_time'] >= constraint_time

def test_night_boundary_handling(sample_observatory, sample_block):
    """Test handling of night boundaries (sunset/sunrise)"""
    block_group = [sample_block]
    schedule = []
    
    # Schedule near sunrise to test boundary condition
    test_date = datetime.datetime.now(zoneinfo.ZoneInfo('UTC'))
    scheduled_blocks = basic_scheduler(block_group, schedule)
    
    # Get sunrise time for comparison
    sunrise_time = sample_observatory.sun_rise_time(Time(test_date), 
                                                  which='next', 
                                                  horizon=-12*u.deg)
    
    # Block should not end after sunrise
    assert scheduled_blocks[0]['end_time'] <= Time(sunrise_time)

def test_transition_handling(sample_observatory):
    """Test handling of transitions between different targets"""
    # Create two blocks with different targets
    target1 = FixedTarget(SkyCoord(ra='02h00m00s', dec='+30d00m00s'))
    target2 = FixedTarget(SkyCoord(ra='14h00m00s', dec='-30d00m00s'))
    
    block1 = {
        'target': target1,
        'start_time': None,
        'end_time': None,
        'duration': 30 * u.minute,
        'constraints': None,
        'filter': 'r',
        'exposure': 60 * u.second,
        'nexp': 1
    }
    
    block2 = {
        'target': target2,
        'start_time': None,
        'end_time': None,
        'duration': 30 * u.minute,
        'constraints': None,
        'filter': 'r',
        'exposure': 60 * u.second,
        'nexp': 1
    }
    
    block_group = [block1, block2]
    schedule = []
    
    scheduled_blocks = basic_scheduler(block_group, schedule)
    
    assert len(scheduled_blocks) == 2
    # Check that there's enough time between blocks for transition
    time_gap = (scheduled_blocks[1]['start_time'] - scheduled_blocks[0]['end_time']).to(u.second)
    assert time_gap > 0 * u.second  # Should include transition time

def test_empty_schedule(sample_observatory):
    """Test handling of empty block groups"""
    block_group = []
    schedule = []
    
    scheduled_blocks = basic_scheduler(block_group, schedule)
    
    assert len(scheduled_blocks) == 0

# Add error handling tests
def test_invalid_constraint_handling(sample_observatory, sample_block):
    """Test handling of invalid constraints"""
    # Set an impossible constraint (start time in the past)
    past_time = Time.now() - 1*u.day
    sample_block['constraints'] = [{
        'min': past_time
    }]
    block_group = [sample_block]
    schedule = []
    
    with pytest.raises(Exception):  # Should raise an appropriate exception
        scheduled_blocks = basic_scheduler(block_group, schedule)

def test_filter_change_transition(sample_observatory):
    """Test handling of filter changes between observations"""
    target = FixedTarget(SkyCoord(ra='02h00m00s', dec='+30d00m00s'))
    
    block1 = {
        'target': target,
        'start_time': None,
        'end_time': None,
        'duration': 30 * u.minute,
        'constraints': None,
        'filter': 'r',
        'exposure': 60 * u.second,
        'nexp': 1
    }
    
    block2 = block1.copy()
    block2['filter'] = 'g'  # Different filter
    
    block_group = [block1, block2]
    schedule = []
    
    scheduled_blocks = basic_scheduler(block_group, schedule)
    
    assert len(scheduled_blocks) == 2
    # Verify filter change transition time is included
    time_gap = (scheduled_blocks[1]['start_time'] - scheduled_blocks[0]['end_time']).to(u.second)
    assert time_gap >= 5 * u.second  # Default filter change time

def test_long_duration_block(sample_observatory, sample_block):
    """Test handling of blocks that would extend past sunrise"""
    sample_block['duration'] = 8 * u.hour  # Deliberately too long
    block_group = [sample_block]
    schedule = []
    
    scheduled_blocks = basic_scheduler(block_group, schedule)
    
    # Should either reject the block or truncate it at sunrise
    if len(scheduled_blocks) > 0:
        sunrise_time = sample_observatory.sun_rise_time(
            Time(datetime.datetime.now(zoneinfo.ZoneInfo('UTC'))), 
            which='next',
            horizon=-12*u.deg
        )
        assert scheduled_blocks[0]['end_time'] <= Time(sunrise_time)

def test_overlapping_constraints(sample_observatory, sample_block):
    """Test handling of blocks with overlapping time constraints"""
    test_time = Time.now()
    
    block1 = sample_block.copy()
    block2 = sample_block.copy()
    
    # Set overlapping time constraints
    block1['constraints'] = [{
        'min': test_time + 1*u.hour,
        'max': test_time + 2*u.hour
    }]
    
    block2['constraints'] = [{
        'min': test_time + 1.5*u.hour,
        'max': test_time + 2.5*u.hour
    }]
    
    block_group = [block1, block2]
    schedule = []
    
    scheduled_blocks = basic_scheduler(block_group, schedule)
    
    assert len(scheduled_blocks) == 2
    # Verify blocks don't overlap
    assert scheduled_blocks[1]['start_time'] >= scheduled_blocks[0]['end_time']
    # Verify constraints are respected
    assert scheduled_blocks[0]['start_time'] >= test_time + 1*u.hour
    assert scheduled_blocks[1]['start_time'] >= test_time + 1.5*u.hour

def test_priority_order_preservation(sample_observatory, sample_block):
    """Test that block order (priority) is preserved when possible"""
    block_group = [sample_block.copy() for _ in range(3)]
    schedule = []
    
    # Add different identifiers to track order
    for i, block in enumerate(block_group):
        block['priority'] = i
    
    scheduled_blocks = basic_scheduler(block_group, schedule)
    
    assert len(scheduled_blocks) == 3
    # Verify blocks are scheduled in original order
    for i in range(len(scheduled_blocks)-1):
        assert scheduled_blocks[i]['priority'] < scheduled_blocks[i+1]['priority']

if __name__ == "__main__":
    test_schedtel("./tests/bin/")
