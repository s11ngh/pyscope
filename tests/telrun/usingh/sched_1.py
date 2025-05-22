import pytest
from pyscope.telrun import schedtel_astroplan

def run_schedule_test(
    observer_site='apo',
    targets=['Deneb', 'Sirius'],
    start_time='2016-07-06 19:00',
    end_time='2016-07-07 19:00',
    constraint_window=None,
    exposure_times=None,
    num_exposures=16,
    read_out_time=20,
    filters=['B', 'G', 'R'],
    max_airmass=3,
    slew_rate=0.8,
    filter_change_times=None,
    scheduler_type='priority'
):
    priority_schedule, sequential_schedule = schedtel_astroplan.create_schedule(
        observer_site=observer_site,
        targets=targets,
        start_time=start_time,
        end_time=end_time,
        constraint_window=constraint_window,
        exposure_times=exposure_times,
        num_exposures=num_exposures,
        read_out_time=read_out_time,
        filters=filters,
        max_airmass=max_airmass,
        slew_rate=slew_rate,
        filter_change_times=filter_change_times,
        scheduler_type=scheduler_type
    )
    # Return both for flexibility
    return priority_schedule, sequential_schedule

def test_single_target():
    pri_sched, _ = run_schedule_test(targets=['Deneb'])
    table = pri_sched.to_table()
    assert len(table) > 0
    assert 'Deneb' in table['target']

def test_two_targets_overlap():
    pri_sched, _ = run_schedule_test(
        targets=['Deneb', 'Sirius'],
        constraint_window=('2016-07-07 02:00', '2016-07-07 08:00')
    )
    table = pri_sched.to_table()
    assert len(table) > 0
    assert 'Deneb' in table['target']
    assert 'Sirius' in table['target']

def test_two_targets_conflict():
    # Very tight window, may cause one or both to be unschedulable
    pri_sched, _ = run_schedule_test(
        targets=['Deneb', 'Sirius'],
        constraint_window=('2016-07-07 07:00', '2016-07-07 07:10')
    )
    table = pri_sched.to_table()
    # At least the table exists, but may be empty if nothing can be scheduled
    assert table is not None
    # Optionally, check if at least one target is present
    assert any(t in table['target'] for t in ['Deneb', 'Sirius']) or len(table) == 0

def test_sequential_single_target_subaru():
    _, seq_sched = run_schedule_test(
        observer_site='subaru',
        targets=['Vega'],
        scheduler_type='sequential'
    )
    table = seq_sched.to_table()
    assert len(table) > 0
    assert 'Vega' in table['target']

def test_priority_multiple_targets_haleakala():
    pri_sched, _ = run_schedule_test(
        observer_site='haleakala',
        targets=['Polaris', 'Rigel', 'Regulus'],
        scheduler_type='priority'
    )
    table = pri_sched.to_table()
    assert len(table) > 0
    for t in ['Polaris', 'Rigel', 'Regulus']:
        assert t in table['target']

def test_sequential_conflicting_targets():
    # Algol and Albireo with a very short window, likely to conflict
    _, seq_sched = run_schedule_test(
        observer_site='subaru',
        targets=['Algol', 'Albireo'],
        constraint_window=('2016-07-07 03:00', '2016-07-07 03:10'),
        scheduler_type='sequential'
    )
    table = seq_sched.to_table()
    assert table is not None
    # At least one target may be scheduled, or none if impossible
    assert any(t in table['target'] for t in ['Algol', 'Albireo']) or len(table) == 0

def test_priority_target_priority_order():
    # Test if the first target gets scheduled before the second due to priority
    pri_sched, _ = run_schedule_test(
        observer_site='haleakala',
        targets=['Altair', 'Sirius'],
        scheduler_type='priority'
    )
    table = pri_sched.to_table()
    # Check that Altair (priority 0) is scheduled before Sirius (priority 1) if both are present
    targets_in_order = [row['target'] for row in table if row['target'] in ['Altair', 'Sirius']]
    if 'Altair' in targets_in_order and 'Sirius' in targets_in_order:
        assert targets_in_order.index('Altair') < targets_in_order.index('Sirius')

def test_sequential_many_targets_varied_filters():
    # Many targets, different filters, sequential scheduler
    _, seq_sched = run_schedule_test(
        observer_site='subaru',
        targets=['Vega', 'Altair', 'Albireo', 'Regulus'],
        filters=['B', 'V'],
        scheduler_type='sequential'
    )
    table = seq_sched.to_table()
    assert len(table) > 0
    for t in ['Vega', 'Altair', 'Albireo', 'Regulus']:
        assert t in table['target']
