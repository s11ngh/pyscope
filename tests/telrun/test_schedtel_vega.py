import pytest
from astropy.time import Time
from astropy import units as u
from astroplan import Observer, FixedTarget
from pyscope.telrun.schedtel_vega import (
    setup_observer,
    setup_targets,  # setup_target을 setup_targets로 변경
    setup_time_constraints,
    create_blocks,
    create_scheduler,
    schedule_stars  # schedule_vega를 schedule_stars로 변경
)
from astropy.table import Table

def test_setup_observer():
    """Test observer creation"""
    observer = setup_observer()
    assert isinstance(observer, Observer)
    #assert observer.name == 'Apache Point Observatory'
    assert observer.name == 'apo'

def test_setup_target():
    """Test targets creation"""
    targets = setup_targets()  # Changed from setup_target to setup_targets
    assert isinstance(targets, list)
    assert all(isinstance(target, FixedTarget) for target in targets)
    assert 'Vega' in [target.name for target in targets]

def test_time_constraints():
    """Test time constraints are properly set"""
    noon_before, noon_after, half_night_start, half_night_end = setup_time_constraints()
    
    assert isinstance(noon_before, Time)
    assert isinstance(noon_after, Time)
    assert half_night_start > noon_before
    assert half_night_end < noon_after

def test_block_creation():
    """Test observation blocks are created correctly"""
    from astroplan.constraints import TimeConstraint
    
    target = setup_target()
    _, _, half_night_start, half_night_end = setup_time_constraints()
    time_constraint = TimeConstraint(half_night_start, half_night_end)
    
    blocks = create_blocks(target, time_constraint)
    
    assert len(blocks) == 3  # One block per filter
    assert blocks[0].configuration['filter'] == 'B'
    assert blocks[1].configuration['filter'] == 'V'
    assert blocks[2].configuration['filter'] == 'R'

def test_full_schedule():
    """Test full scheduling process"""
    scheduled_blocks = schedule_stars()  # Changed from schedule_vega to schedule_stars
    
    if scheduled_blocks is not None:
        # Verify we got a list of blocks
        assert isinstance(scheduled_blocks, list)
        assert len(scheduled_blocks) > 0
        
        # Check first block properties
        block = scheduled_blocks[0]
        assert hasattr(block, 'target')
        assert hasattr(block, 'start_time')
        assert hasattr(block, 'duration')
        assert hasattr(block, 'configuration')
        
        # Verify filter sequence
        filters = [block.configuration['filter'] for block in scheduled_blocks]
        assert all(f in ['B', 'V', 'R'] for f in filters)
        
        # Verify time sequence
        start_times = [block.start_time for block in scheduled_blocks]
        assert all(start_times[i] <= start_times[i+1] for i in range(len(start_times)-1))

def test_scheduler_creation():
    """Test scheduler creation with proper configuration"""
    observer = setup_observer()
    from astroplan.constraints import AirmassConstraint, AtNightConstraint
    
    global_constraints = [
        AirmassConstraint(max=3, boolean_constraint=False),
        AtNightConstraint.twilight_astronomical()
    ]
    
    scheduler = create_scheduler(global_constraints, observer)
    assert scheduler.constraints == global_constraints
    assert scheduler.observer == observer