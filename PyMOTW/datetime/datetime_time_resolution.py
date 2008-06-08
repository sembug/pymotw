#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2008 Doug Hellmann All rights reserved.
#
"""Time resolution.
"""

__version__ = "$Id$"

import datetime

for m in [ 1, 0, 0.1, 0.6 ]:
    print '%02.1f :' % m, datetime.time(0, 0, 0, microsecond=m)