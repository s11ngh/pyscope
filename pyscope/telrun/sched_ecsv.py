from astropy.coordinates import SkyCoord
import numpy as np
from astropy.table import Table
from astropy import time as astrotime
from astropy import units as u
import os
import pathlib

def create_ecsv_table(schedule_list: list[dict]):
    """Convert schedule list to ECSV-compatible Table"""
    
    # Create a new table with only the columns we want to preserve
    # and in formats that ECSV can handle
    data = {
        'ID': [],
        'name': [],
        'priority': [],
        'observer': [],  # Will be converted to string
        'code': [],
        'title': [],
        'filename': [],
        'filter': [],
        'exposure': [],  # In seconds
        'nexp': [],
        'target_ra': [],  # In degrees
        'target_dec': [], # In degrees
        'start_time': [], # ISO format string
        'end_time': [],   # ISO format string
        'duration': [],   # In seconds
        'pm_ra_cosdec': [], # Proper motion in RA
        'pm_dec': [],      # Proper motion in Dec
        'status': [],
        'message': []
        # Note: constraints are not included as they can't be directly serialized to ECSV
    }
    
    for block in schedule_list:
        data['ID'].append(float(block['ID']))
        data['name'].append(str(block['name']))
        data['priority'].append(int(block['priority']))
        # Convert list of observers to comma-separated string
        data['observer'].append(','.join(block['observer']) if isinstance(block['observer'], list) else str(block['observer']))
        data['code'].append(str(block['code']))
        data['title'].append(str(block['title']))
        data['filename'].append(str(block['filename']))
        data['filter'].append(str(block['filter']))
        data['exposure'].append(float(block['exposure']))
        data['nexp'].append(int(block['nexp']))
        data['target_ra'].append(float(block['target_ra']))
        data['target_dec'].append(float(block['target_dec']))
        # Handle potentially None start/end times
        data['start_time'].append(block['start_time'].isot if block['start_time'] is not None else '')
        data['end_time'].append(block['end_time'].isot if block['end_time'] is not None else '')
        data['duration'].append(float(block['duration'].to(u.second).value) if hasattr(block['duration'], 'to') else float(block['duration']))
        # Handle proper motion values
        data['pm_ra_cosdec'].append(float(block['pm_ra_cosdec'].to(u.arcsec/u.hour).value) if hasattr(block['pm_ra_cosdec'], 'to') else float(block['pm_ra_cosdec']))
        data['pm_dec'].append(float(block['pm_dec'].to(u.arcsec/u.hour).value) if hasattr(block['pm_dec'], 'to') else float(block['pm_dec']))
        data['status'].append(str(block['status']))
        data['message'].append(str(block['message']))

    # Create the table
    table = Table(data)
    
    # Add units where appropriate
    table['target_ra'].unit = u.deg
    table['target_dec'].unit = u.deg
    table['duration'].unit = u.second
    table['exposure'].unit = u.second
    table['pm_ra_cosdec'].unit = u.arcsec/u.hour
    table['pm_dec'].unit = u.arcsec/u.hour
    
    # Add metadata
    table.meta['DESCRIPTION'] = 'Observation Schedule'
    table.meta['VERSION'] = '1.0'
    
    return table

def prepare_blocks_for_ecsv(schedule_list):
    """
    Prepare blocks for saving to ECSV by converting complex objects to serializable formats.
    
    Parameters
    ----------
    schedule_list : list of dict
        List of observation blocks from the scheduler
        
    Returns
    -------
    list of dict
        List of blocks with serializable values
    """
    prepared_blocks = []
    
    for block in schedule_list:
        # Create a copy of the block to avoid modifying the original
        prepared_block = block.copy()
        
        # Convert target object to coordinates
        if 'target' in prepared_block and hasattr(prepared_block['target'], 'ra'):
            # If it's an astroplan FixedTarget
            if hasattr(prepared_block['target'], 'skycoord'):
                prepared_block['target_ra'] = prepared_block['target'].skycoord.ra.deg
                prepared_block['target_dec'] = prepared_block['target'].skycoord.dec.deg
            # If it's an astropy SkyCoord
            else:
                prepared_block['target_ra'] = prepared_block['target'].ra.deg
                prepared_block['target_dec'] = prepared_block['target'].dec.deg
                
        # Remove constraints as they can't be directly serialized
        if 'constraints' in prepared_block:
            prepared_block.pop('constraints')
            
        # Remove target as it can't be directly serialized
        if 'target' in prepared_block:
            prepared_block.pop('target')
            
        prepared_blocks.append(prepared_block)
        
    return prepared_blocks

def save_schedule_to_ecsv(schedule_list, output_file):
    """
    Save schedule to ECSV file in the tests/bin directory
    
    Parameters
    ----------
    schedule_list : list of dict
        List of observation blocks from the scheduler
    output_file : str
        Filename for output (will be saved in the tests/bin directory)
    
    Returns
    -------
    astropy.table.Table
        The table that was saved
        
    Raises
    ------
    FileExistsError
        If a file with the same name already exists in the target directory
    """
    
    # Prepare blocks for serialization
    prepared_blocks = prepare_blocks_for_ecsv(schedule_list)
    
    # Create table
    table = create_ecsv_table(prepared_blocks)
    
    # Get the project root directory - this is 2 levels up from this file
    # since this file is in pyscope/telrun/
    project_root = pathlib.Path(__file__).parent.parent.parent.absolute()
    
    # Create the bin directory path
    bin_dir = os.path.join(project_root, 'tests', 'bin')
    
    # Ensure the bin directory exists
    os.makedirs(bin_dir, exist_ok=True)
    
    # Create the full output path
    full_output_path = os.path.join(bin_dir, os.path.basename(output_file))
    
    # Check if file already exists
    if os.path.exists(full_output_path):
        raise FileExistsError(f"A file named '{os.path.basename(output_file)}' already exists in the target directory. Please choose another name.")
    
    # Save the table
    table.write(full_output_path, format='ascii.ecsv', overwrite=True)
    
    return table
