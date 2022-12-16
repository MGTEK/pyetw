# Python logging via Event Tracing for Windows (ETW)

![build](https://github.com/mgtek/pyetw/actions/workflows/build.yml/badge.svg)
![docs](https://readthedocs.org/projects/pyetw/badge/?version=latest)

**PyEtw** is a Python package that allows you to use Pythons standard logging facility
with **Event Tracing for Windows (ETW)**.

**PyEtw** implements [`logging.Handler`](https://docs.python.org/3/library/logging.handlers.html)
and overloads `emit()` to handle the `logging.LogRecord` objects.
The `logging.LogRecord` object is then converted to a Windows event record,
and written via the API [`EventWriteTransfer`](https://learn.microsoft.com/en-us/windows/win32/api/evntprov/nf-evntprov-eventwritetransfer)
as an ETW TraceLogging event.

Using ETW for Python logging allows you to leverage the many tools available
for the Windows ETW ecosystem, such as [MGTEK TraceView Plus](https://www.mgtek.com/traceview).

## Features

- Log Python `logging.LogRecord` via **Event Tracing for Windows**.
- Includes standard metadata in ETW records, such as ETW provider, time-stamp, process and thread ID, and log-level.
- Includes Python specific `logging.LogRecord` metadata in ETW records, such as Python module, function name, filename and line-number, and log message.
- Automatic provider ID (GUID) generation via provider name hash.
- Native WIN32 implementation with no dependecies.

## Logging ETW events via Python

To log ETW events via the Python `logging` module you can write:

```python
import logging
import pyetw

logging.basicConfig(level=logging.DEBUG, handlers=(pyetw.LoggerHandler(),))
logging.info("Hello from PyEtw!")
```

Note the parameter `handlers` to `basicConfig()`. By specifing the `pyetw.LoggerHandler()`,
the log records are written as ETW TraceLogging events.

To record and view the traces, you can use any ETW tracing tool.

## Recording ETW Traces

Here is an example that records the events of the `root` logger to a trace file
using [`Tracelog`](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/tracelog),
which is included in the [Windows SDK](https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/)

```console
C:\Temp> tracelog -start mytrace -guid *root
```

Note that the specified GUID must match the name of the Python logger.
Prefix the logger name with a **star** to have tracelog create a GUID hash of the logger name.

After you are done running the Python example from above, run

```console
C:\Temp> tracelog -stop mytrace
```

When the trace is stopped, you will have a file `LogFile.Etl` that contains a single trace record.

To view the recorded trace, you can write

```console
C:\Temp> tracefmt -displayonly LogFile.Etl
```

## Installing PyEtw

You can install the [PyEtw package](https://pypi.org/project/pyetw/) from PyPI using pip:

```console
pip install pyetw
```

In order to use the **PyEtw** package, you need **Python 3.6** or higher.

The source code for the **PyEtw** package can be found at GitHub at <https://github.com/mgtek/pyetw>.

## Documentation

You can find the **PyEtw** user's guide at <https://pyetw.readthedocs.io/>.

## Examples

You can find Python examples using **PyEtw** in the pyetw GitHub repository at <https://github.com/mgtek/pyetw/tree/main/examples>.

## Getting help

For issues with **PyEtw**, please visit the
[pyetw issue tracker](https://github.com/mgtek/pyetw/issues).
