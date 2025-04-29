import datetime
import logging
import re
import shlex

import astroplan
import numpy as np
from astropy import coordinates as coord
from astropy import time as astrotime
from astropy import units as u
from astroquery import mpc

from astroplan import Observer

apo = Observer.at_site('apo')

from astroplan import FixedTarget

# Initialize the targets
deneb = FixedTarget.from_name('Deneb')
m13 = FixedTarget.from_name('M13')

deneb

m13

from astropy.time import Time

noon_before = Time('2016-07-06 19:00')
noon_after = Time('2016-07-07 19:00')

from astroplan.constraints import AtNightConstraint, AirmassConstraint

# create the list of constraints that all targets must satisfy
global_constraints = [AirmassConstraint(max = 3, boolean_constraint = False),
                      AtNightConstraint.twilight_civil()]

from astroplan import ObservingBlock
from astroplan.constraints import TimeConstraint
from astropy import units as u

# Define the read-out time, exposure duration and number of exposures
read_out = 20 * u.second
deneb_exp = 60*u.second
m13_exp = 100*u.second
n = 16
blocks = []

half_night_start = Time('2016-07-07 02:00')
half_night_end = Time('2016-07-07 08:00')
first_half_night = TimeConstraint(half_night_start, half_night_end)
# Create ObservingBlocks for each filter and target with our time
# constraint, and durations determined by the exposures needed
for priority, bandpass in enumerate(['B', 'G', 'R']):
    # We want each filter to have separate priority (so that target
    # and reference are both scheduled)
    b = ObservingBlock.from_exposures(deneb, priority, deneb_exp, n, read_out,
                                        configuration = {'filter': bandpass},
                                        constraints = [first_half_night])
    blocks.append(b)
    b = ObservingBlock.from_exposures(m13, priority, m13_exp, n, read_out,
                                        configuration = {'filter': bandpass},
                                        constraints = [first_half_night])
    blocks.append(b)

for block in blocks: 
    print(block)