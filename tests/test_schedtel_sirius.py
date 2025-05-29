# -*- coding: utf-8 -*-

import pytest
from astropy.time import Time
from astropy import units as u
from astroplan import Observer, FixedTarget, ObservingBlock
from astroplan.constraints import AirmassConstraint, AtNightConstraint, TimeConstraint
from astroplan.scheduling import Transitioner, SequentialScheduler, PriorityScheduler, Schedule

@pytest.fixture
def apo_observer():
    """Apache Point Observatory."""
    return Observer.at_site('apo')

@pytest.fixture
def observing_targets():
    """Returns FixedTarget objects for Deneb, M13, Sirius."""
    return {
        'Deneb': FixedTarget.from_name('Deneb'),
        'M13': FixedTarget.from_name('M13'),
        'Sirius': FixedTarget.from_name('Sirius')
    }

@pytest.fixture
def observing_blocks(observing_targets):
    """Create test observing blocks with different filters and exposures."""
    read_out = 20 * u.second
    n = 16
    deneb_exp = 60 * u.second
    m13_exp = 100 * u.second
    sirius_exp = 80 * u.second

    half_night_start = Time('2016-12-15 02:00')
    half_night_end = Time('2016-12-16 11:00')
    time_constraint = TimeConstraint(half_night_start, half_night_end)

    blocks = []
    for priority, bandpass in enumerate(['B', 'G', 'R']):
        blocks.append(ObservingBlock.from_exposures(
            observing_targets['Deneb'], priority, deneb_exp, n, read_out,
            configuration={'filter': bandpass},
            constraints=[time_constraint]
        ))
        blocks.append(ObservingBlock.from_exposures(
            observing_targets['M13'], priority, m13_exp, n, read_out,
            configuration={'filter': bandpass},
            constraints=[time_constraint]
        ))
        blocks.append(ObservingBlock.from_exposures(
            observing_targets['Sirius'], priority, sirius_exp, n, read_out,
            configuration={'filter': bandpass},
            constraints=[time_constraint]
        ))

    return blocks

@pytest.fixture
def transitioner():
    """Returns a fixed transitioner object."""
    return Transitioner(
        slew_rate=0.8 * u.deg / u.second,
        instrument_reconfig_times={'filter': {
            ('B', 'G'): 10 * u.second,
            ('G', 'R'): 10 * u.second,
            'default': 30 * u.second
        }}
    )

@pytest.fixture
def global_constraints():
    """Returns global constraints."""
    return [
        AirmassConstraint(max=3, boolean_constraint=False),
        AtNightConstraint.twilight_civil()
    ]

@pytest.fixture
def scheduling_window():
    """Returns the scheduling window times."""
    return Time('2016-12-15 19:00'), Time('2016-12-16 19:00')

def test_sequential_scheduler_sirius(observing_blocks, apo_observer, transitioner, global_constraints, scheduling_window):
    """Tests that Sirius is scheduled in sequential scheduler output."""
    start, end = scheduling_window
    scheduler = SequentialScheduler(constraints=global_constraints, observer=apo_observer, transitioner=transitioner)
    schedule = Schedule(start, end)
    scheduler(observing_blocks, schedule)

    table = schedule.to_table()
    sirius_rows = [row for row in table if "Sirius" in row['target']]
    assert sirius_rows, "Sirius should appear in the sequential schedule"

def test_priority_scheduler_sirius(observing_blocks, apo_observer, transitioner, global_constraints, scheduling_window):
    """Tests that Sirius is scheduled in priority scheduler output."""
    start, end = scheduling_window
    scheduler = PriorityScheduler(constraints=global_constraints, observer=apo_observer, transitioner=transitioner)
    schedule = Schedule(start, end)
    scheduler(observing_blocks, schedule)

    table = schedule.to_table()
    sirius_rows = [row for row in table if "Sirius" in row['target']]
    assert sirius_rows, "Sirius should appear in the priority schedule"
