# Python logging via Event Tracing for Windows (ETW)

**PyEtw** is a Python package that allows you to use Pythons standard logging facility
with **Event Tracing for Windows (ETW)**.

**PyEtw** implements [`logging.Handler`](https://docs.python.org/3/library/logging.handlers.html)
and overloads `emit()` to handle the `logging.LogRecord` objects.
The `logging.LogRecord` object is then converted to a Windows event record,
and written via the API `EventWriteTransfer` as an ETW TraceLogging event.

Using ETW for Python logging allows you to leverage the many tools available
for the Windows ETW ecosystem, such as [MGTEK TraceView Plus](https://www.mgtek.com/traceview).

## Features

- Log Python `logging.LogRecord` via **Event Tracing for Windows**.
- Includes standard metadata in ETW records, such as ETW provider, time-stamp, process and thread ID, and log-level.
- Includes Python specific `logging.LogRecord` metadata in ETW records, such as Python module, function name, filename and line-number, and log message.
- Automatic provider ID (GUID) generation via provider name hash.
- Native WIN32 implementation with no dependecies.

## Writing ETW events via Python

To write ETW events via the Python `logging` module you can write:

```python
import logging
import pyetw

logging.basicConfig(level=logging.DEBUG, handlers=(pyetw.LoggerHandler(),))
logging.info("Hello from PyEtw!")
```

Note the parameter `handlers` to `basicConfig()`. By specifing the `pyetw.LoggerHandler()`,
the log records are written as ETW TraceLogging events.

To record and view the traces, you can use any ETW tracing tool.

## Installing PyEtw

You can install the [PyEtw package](https://pypi.org/project/pyetw/) from PyPI using pip:

```console
pip install pyetw
```

In order to use the **PyEtw** package, you need **Python 3.6** or higher.

The source code for the **PyEtw** package can be found at GitHub at <https://github.com/mgtek/pyetw>.

## Examples

You can find Python examples using **PyEtw** in the pyetw GitHub repository at <https://github.com/mgtek/pyetw/tree/main/examples>.

## Getting help

For issues with **PyEtw**, please visit the
[pyetw issue tracker](https://github.com/mgtek/pyetw/issues).
