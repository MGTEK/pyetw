.. include:: common.rst

Overview
========

**PyEtw** is a Python package that allows you to use Pythons standard logging facility
with **Event Tracing for Windows (ETW)**.

**PyEtw** implements `logging.Handler <https://docs.python.org/3/library/logging.handlers.html>`_
and overloads `emit()` to handle the `logging.LogRecord` objects.
The `logging.LogRecord` object is then converted to a Windows event record,
and written via the API `EventWriteTransfer <https://learn.microsoft.com/en-us/windows/win32/api/evntprov/nf-evntprov-eventwritetransfer>`_
as an ETW TraceLogging event.

Using ETW for Python logging allows you to leverage the many tools available
for the Windows ETW ecosystem, such as `MGTEK TraceView Plus <https://www.mgtek.com/traceview>`_.

Features
========

- Log Python `logging.LogRecord` via **Event Tracing for Windows**.
- Includes standard metadata in ETW records, such as ETW provider, time-stamp, process and thread ID, and log-level.
- Includes Python specific `logging.LogRecord` metadata in ETW records, such as Python module, function name, filename and line-number, and log message.
- Automatic provider ID (GUID) generation via provider name hash.
- Native WIN32 implementation with no dependecies.

Logging ETW events via Python
=============================

To log ETW events via the Python `logging` module you can write:

.. code-block::

   import logging
   import pyetw

   logging.basicConfig(level=logging.DEBUG, handlers=(pyetw.LoggerHandler(),))
   logging.info("Hello from PyEtw!")

Note the parameter `handlers` to `basicConfig()`. By specifing the `pyetw.LoggerHandler()`,
the log records are written as ETW TraceLogging events.

To record and view the traces, you can use any ETW tracing tool.

ETW Provider GUID hash
======================

**PyEtw** uses the standard TraceLogging hashing algorithm to
derive the provider GUID from the trace provider name,
which is set to the Python logger name by default.

If your tracing tool is not able to generate the provider GUID from the provider name,
you can use the `guid` property of the `EventProvider` class to obtain the GUID.
For instance, to get the provider GUID for the `root` logger,
enter the following command:

.. code-block::

   python -c "import pyetw;print(pyetw.EventProvider('root').guid)"

Recording ETW Traces
====================

Here is an example that records the events of the `root` logger to a trace file
using `Tracelog <https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/tracelog>`_,
which is included in the `Windows SDK <https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/>`_

.. code-block::

   C:\Temp> tracelog -start mytrace -guid *root

Note that the specified GUID must match the name of the Python logger.
Prefix the logger name with a **star** to have tracelog create a GUID hash of the logger name.

After you are done running the Python example from above, run

.. code-block::

   C:\Temp> tracelog -stop mytrace

When the trace is stopped, you will have a file `LogFile.Etl` that contains a single trace record.

To view the recorded trace, you can write

.. code-block::

   C:\Temp> tracefmt -displayonly LogFile.Etl

Installing PyEtw
================

You can install the |pyetw-package| from PyPI using pip:

.. code-block:: console

    pip install pyetw

In order to use the **PyEtw** package, you need **Python 3.6** or higher.

The source code for the **PyEtw** package can be found at GitHub at `<https://github.com/mgtek/pyetw>`_.

Documentation
=============

You can find the **PyEtw** user's guide at `<https://pyetw.readthedocs.io/>`_.

Examples
========

You can find Python examples using **PyEtw** in the pyetw GitHub repository at
`<https://github.com/mgtek/pyetw/tree/main/examples>`_.

Getting help
============

For issues with **PyEtw**, please visit the
`pyetw GitHub issue tracker <https://github.com/mgtek/pyetw/issues>`_.
