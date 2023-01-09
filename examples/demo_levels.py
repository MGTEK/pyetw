#
# Copyright (C) 2020 Marius Greuel
#
# SPDX-License-Identifier: MIT
#
# https://github.com/mgtek/pyetw
#

import logging
import pyetw


def some_fun():
    logging.basicConfig(level=logging.DEBUG, handlers=(pyetw.LoggerHandler(),))
    logging.debug("This is a 'debug' message")
    logging.info("This is a 'info' message")
    logging.warning("This is a 'warning' message")
    logging.error("This is a 'error' message")
    logging.critical("This is a 'critical' message")


if __name__ == "__main__":
    some_fun()
