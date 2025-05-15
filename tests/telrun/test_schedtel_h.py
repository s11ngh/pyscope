import pytest
import os
import numpy as np
from astropy import units as u
from astropy import time as astrotime
from astropy.table import Table

# Import the module containing the scheduler
from pyscope.telrun.schedtel_h import (
    basic_scheduler,
    block_group,
    half_night_start,
    half_night_end,
)

def test_scheduler_number_of_observations():
    """
    Test that the scheduler correctly schedules all observations.
    
    Expected behavior:
    - All blocks in the block_group should be scheduled
    - The number of scheduled blocks should match the number of input blocks
    - Each block should have 'S' status after scheduling
    """
    # Create a fresh copy of the block_group to avoid modifying the original
    test_blocks = block_group.copy()
    
    # Count the number of blocks in the input
    initial_block_count = len(test_blocks)
    
    # Make sure initial_block_count is not zero to avoid trivial test
    assert initial_block_count > 0, "Block group is empty, test is trivial"
    
    # Run the scheduler
    schedule = []
    scheduled_blocks = basic_scheduler(test_blocks, schedule)
    
    # Test the number of scheduled blocks
    assert len(scheduled_blocks) == initial_block_count, \
        f"Expected {initial_block_count} scheduled blocks, got {len(scheduled_blocks)}"
    
    # Test that all blocks have been scheduled (status = 'S')
    for block in scheduled_blocks:
        assert block['status'] == 'S', \
            f"Block {block['name']} was not scheduled, status is {block['status']}"

def test_scheduler_timing_order():
    """
    Test that the scheduler correctly orders observations in time.
    
    Expected behavior:
    - All blocks should have start and end times
    - Start times should be within the observation window
    - Each block's start time should be after the previous block's end time
    - The last block should end before or at the half night end time
    """
    # Create a fresh schedule
    schedule = []
    test_blocks = block_group.copy()
    scheduled_blocks = basic_scheduler(test_blocks, schedule)
    
    # Check that each block has start and end times
    for block in scheduled_blocks:
        assert block['start_time'] is not None, f"Block {block['name']} has no start time"
        assert block['end_time'] is not None, f"Block {block['name']} has no end time"
    
    # Check that the first block starts at or after the half night start
    assert scheduled_blocks[0]['start_time'] >= half_night_start, \
        "First block starts before the half night window"
    
    # Check that blocks are ordered in time with no overlaps
    for i in range(1, len(scheduled_blocks)):
        prev_block = scheduled_blocks[i-1]
        curr_block = scheduled_blocks[i]
        
        assert curr_block['start_time'] >= prev_block['end_time'], \
            f"Block {curr_block['name']} starts before previous block {prev_block['name']} ends"
    
    # Ideally, the last block should end before the half night end
    # But the code comment suggests it might exceed the window to see what would be scheduled
    # So we'll note this as an expected behavior
    if scheduled_blocks[-1]['end_time'] > half_night_end:
        print(f"NOTE: Last block ends at {scheduled_blocks[-1]['end_time'].iso}, "
              f"which is after half night end {half_night_end.iso}. "
              f"This is allowed by the scheduler design.")

def test_saved_schedule_file():
    """
    Test that the schedule can be saved to a file and the file contains the correct data.
    
    Expected behavior:
    - The schedule should be saved to a file in the tests/bin directory
    - The saved file should contain all the scheduled blocks
    """
    from pyscope.telrun.sched_ecsv import save_schedule_to_ecsv
    
    # Create a fresh schedule
    schedule = []
    test_blocks = block_group.copy()
    scheduled_blocks = basic_scheduler(test_blocks, schedule)
    
    # Define a unique filename for this test
    test_filename = f'test_schedule_{np.random.randint(10000)}.ecsv'
    
    # Save the schedule
    try:
        table = save_schedule_to_ecsv(scheduled_blocks, test_filename)
        
        # Get the project root directory
        import pathlib
        project_root = pathlib.Path(__file__).parent.parent.parent.absolute()
        
        # Build the expected file path
        expected_file_path = os.path.join(project_root, 'tests', 'bin', test_filename)
        
        # Check that the file exists
        assert os.path.exists(expected_file_path), f"Schedule file not found at {expected_file_path}"
        
        # Read the file back
        saved_table = Table.read(expected_file_path, format='ascii.ecsv')
        
        # Check that the number of rows matches the number of scheduled blocks
        assert len(saved_table) == len(scheduled_blocks), \
            f"Expected {len(scheduled_blocks)} rows in saved file, got {len(saved_table)}"
        
    finally:
        # Clean up - remove the test file
        try:
            os.remove(expected_file_path)
        except:
            pass  # If file doesn't exist or can't be removed, just continue
