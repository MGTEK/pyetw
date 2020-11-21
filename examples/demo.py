#
# Copyright (C) 2020 Marius Greuel
#
# SPDX-License-Identifier: MIT
#
# https://github.com/mgtek/pyetw
#

import logging
import pyetw

logging.basicConfig(level=logging.DEBUG, handlers=(pyetw.LoggerHandler(),))
logging.info("Hello from PyEtw!")
