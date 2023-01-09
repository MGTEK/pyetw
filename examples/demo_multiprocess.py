#
# Copyright (C) 2020 Marius Greuel
#
# SPDX-License-Identifier: MIT
#
# https://github.com/mgtek/pyetw
#

import logging
import multiprocessing
import pyetw

logging.basicConfig(level=logging.DEBUG, handlers=(pyetw.LoggerHandler(),))


def some_fun():
    demo_logger = logging.getLogger("demo")
    demo_logger.debug("Hello from demo logger!")


def some_loop():
    loop_logger = logging.getLogger("loop")
    for i in range(1000000):
        loop_logger.debug(f"Hello from loop logger: {i}")


if __name__ == "__main__":
    logging.info("Hello from PyEtw!")

    multiprocessing.set_start_method("spawn")
    process = multiprocessing.Process(target=some_loop)
    process.start()

    some_fun()
    some_loop()

    process.join()
