"""Python logging via Event Tracing for Windows."""

#
# Copyright (C) 2020 Marius Greuel
#
# SPDX-License-Identifier: MIT
#
# https://github.com/mgtek/pyetw
#

import hashlib
import logging
import struct
from uuid import UUID
from ctypes import (
    WINFUNCTYPE,
    POINTER,
    Structure,
    c_bool,
    c_byte,
    c_int,
    c_ushort,
    c_ulong,
    c_ulonglong,
    c_void_p,
    windll,
    addressof,
)

# pylint: disable=attribute-defined-outside-init

_IN = 1
_OUT = 2

REGHANDLE = c_ulonglong

ERROR_SUCCESS = 0


def _etw_function(name: str, *args):
    def errcheck(result, _, args):
        if result != ERROR_SUCCESS:
            raise OSError(f"{function.name} failed with error code {result}.")

        return args

    argtypes = (arg[1] for arg in args)
    paramflags = tuple((arg[0], arg[2]) for arg in args)
    prototype = WINFUNCTYPE(c_ulong, *argtypes)
    function = prototype((name, windll.advapi32), paramflags)
    function.errcheck = errcheck
    setattr(function, "name", name)
    return function


def _etw_function_bool(name: str, *args):
    argtypes = (arg[1] for arg in args)
    paramflags = tuple((arg[0], arg[2]) for arg in args)
    prototype = WINFUNCTYPE(c_bool, *argtypes)
    return prototype((name, windll.advapi32), paramflags)


# pylint: disable-next=too-few-public-methods
class _EventDescriptor(Structure):
    _fields_ = [
        ("id", c_ushort),
        ("version", c_byte),
        ("channel", c_byte),
        ("level", c_byte),
        ("opcode", c_byte),
        ("task", c_ushort),
        ("keyword", c_ulonglong),
    ]


# pylint: disable-next=too-few-public-methods
class _EventDataDescriptor(Structure):
    _fields_ = [("ptr", c_ulonglong), ("size", c_ulong), ("reserved", c_ulong)]


class Event:
    """Represents an ETW tracelogging event."""

    def __init__(self, name: str, level: int = 0, keyword: int = 0):
        self._name = name
        self._level = level
        self._keyword = keyword
        self._fields = b""
        self._data = b""

    @property
    def name(self) -> str:
        """Gets the name of the event."""
        return self._name

    @property
    def level(self) -> int:
        """Gets the event level."""
        return self._level

    @property
    def keyword(self) -> int:
        """Gets the event keyword."""
        return self._keyword

    @property
    def metadata(self):
        """Gets the encoded TDH event metadata."""
        name_utf8 = self._name.encode("utf_8") + b"\x00"
        metadata = struct.pack("=HB", 2 + 1 + len(name_utf8) + len(self._fields), 0)
        metadata += struct.pack(f"={len(name_utf8)}s", name_utf8)
        metadata += self._fields
        return (c_byte * len(metadata)).from_buffer_copy(metadata)

    @property
    def data(self):
        """Gets the encoded TDH event data."""
        return (c_byte * len(self._data)).from_buffer_copy(self._data)

    def add_int(self, field_name: str, value: int):
        """
        Adds an integer field to the event.

        Parameters
        ----------
        field_name : str
            The name of the field.
        value : int
            The value of the field.
        """
        self._add_field(field_name, 7, 0)  # TDH_INTYPE_INT32/TDH_OUTTYPE_NULL
        self._data += struct.pack("=i", value)

    def add_str(self, field_name: str, value: str):
        """
        Adds a string field to the event.

        Parameters
        ----------
        field_name : str
            The name of the field.
        value : str
            The value of the field.
        """
        self._add_field(field_name, 2, 35)  # TDH_INTYPE_ANSISTRING/TDH_OUTTYPE_UTF8
        self._data += value.encode("utf_8") + b"\x00"

    def _add_field(self, field_name: str, in_type: int, out_type: int):
        field_name_utf8 = field_name.encode("utf_8") + b"\x00"
        self._fields += struct.pack(
            f"={len(field_name_utf8)}sBB", field_name_utf8, 0x80 | in_type, out_type
        )


class EventProvider:
    """Represents an ETW tracelogging provider."""

    _EventRegister = _etw_function(
        "EventRegister",
        (_IN, c_void_p, "ProviderId"),
        (_IN, c_void_p, "EnableCallback"),
        (_IN, c_void_p, "CallbackContext"),
        (_OUT, POINTER(REGHANDLE), "RegHandle"),
    )

    _EventUnregister = _etw_function(
        "EventUnregister",
        (_IN, REGHANDLE, "RegHandle"),
    )

    _EventSetInformation = _etw_function(
        "EventSetInformation",
        (_IN, REGHANDLE, "RegHandle"),
        (_IN, c_int, "InformationClass"),
        (_IN, c_void_p, "EventInformation"),
        (_IN, c_ulong, "InformationLength"),
    )

    _EventWriteTransfer = _etw_function(
        "EventWriteTransfer",
        (_IN, REGHANDLE, "RegHandle"),
        (_IN, POINTER(_EventDescriptor), "EventDescriptor"),
        (_IN, c_void_p, "ActivityId"),
        (_IN, c_void_p, "RelatedActivityId"),
        (_IN, c_ulong, "UserDataCount"),
        (_IN, c_void_p, "UserData"),
    )

    _EventProviderEnabled = _etw_function_bool(
        "EventProviderEnabled",
        (_IN, REGHANDLE, "RegHandle"),
        (_IN, c_byte, "Level"),
        (_IN, c_ulonglong, "Keyword"),
    )

    def __init__(self, name: str, register_provider=True):
        """
        :param name: The event provider name.
        :param register_provider: Set to false to register the provider manually.
        """
        self._name = name
        self._id = self._get_uuid_from_provider_name(name)
        self._activity_id = self._get_uuid_from_provider_name("pyetw")
        self._handle = None

        name_utf8 = self._name.encode("utf_8") + b"\x00"
        traits = struct.pack(f"=H{len(name_utf8)}s", 2 + len(name_utf8), name_utf8)
        self._provider_traits = (c_byte * len(traits)).from_buffer_copy(traits)

        if register_provider:
            self.open()

    def __del__(self):
        self.close()

    def open(self) -> None:
        """Registers the event provider with Windows."""
        self._handle = EventProvider._EventRegister(self._id.bytes_le, None, None)

        EventProvider._EventSetInformation(
            self._handle, 2, self._provider_traits, len(self._provider_traits)
        )

    def close(self) -> None:
        """Unregisters the event provider."""
        if not self._handle is None:
            EventProvider._EventUnregister(self._handle)
            self._handle = None

    @property
    def is_open(self) -> bool:
        """Returns True if the provider has been registered with Windows."""
        return not self._handle is None

    def is_enabled(self, level: int, keyword: int = 0) -> bool:
        """Returns True if the event based on the specified level and keyword should be written."""
        return EventProvider._EventProviderEnabled(self._handle, level, keyword)

    def write(self, event: Event) -> None:
        """Writes an event to the connected trace sessions.

        Parameters
        ----------
        event : Event
            The event to write.
        """
        assert self.is_open

        event_metadata = event.metadata
        event_data = event.data

        event_descriptor = _EventDescriptor()
        # pylint: disable-next=invalid-name
        event_descriptor.id = 0
        event_descriptor.version = 0
        event_descriptor.channel = 0
        event_descriptor.level = event.level
        event_descriptor.opcode = 0
        event_descriptor.task = 0
        event_descriptor.keyword = 0

        event_data_descriptors = (_EventDataDescriptor * 3)()
        event_data_descriptors[0].ptr = addressof(self._provider_traits)
        event_data_descriptors[0].size = len(self._provider_traits)
        event_data_descriptors[0].reserved = 2
        event_data_descriptors[1].ptr = addressof(event_metadata)
        event_data_descriptors[1].size = len(event_metadata)
        event_data_descriptors[1].reserved = 1
        event_data_descriptors[2].ptr = addressof(event_data)
        event_data_descriptors[2].size = len(event_data)
        event_data_descriptors[2].reserved = 0

        EventProvider._EventWriteTransfer(
            self._handle,
            event_descriptor,
            self._activity_id.bytes_le,
            None,
            len(event_data_descriptors),
            event_data_descriptors,
        )

    # pylint: disable-next=no-self-argument
    def _get_uuid_from_provider_name(self, name: str) -> UUID:
        namespace = UUID("482c2db2-c390-47c8-87f8-1a15bfc130fb")
        buffer = namespace.bytes + name.upper().encode("utf_16_be")
        digest = hashlib.sha1(buffer).digest()
        guid = bytearray(digest[:16])
        guid[7] = (guid[7] & 0x0F) | 0x50
        return UUID(bytes_le=bytes(guid))


class LoggerHandler(logging.Handler):
    """Represents a logging.Handler that redirects records to ETW."""

    _providers: dict = {}

    def __init__(self):
        super().__init__()

    def emit(self, record):
        try:
            provider = LoggerHandler._providers.get(record.name, None)
            if provider is None:
                provider = EventProvider(record.name)
                LoggerHandler._providers[record.name] = provider

            level = self._map_level(record.levelname)
            if provider.is_enabled(level):
                event = Event("pyetw", level)
                event.add_str("module", record.module)
                event.add_str("funcName", record.funcName)
                event.add_str("pathname", record.pathname)
                event.add_str("filename", record.filename)
                event.add_int("lineno", record.lineno)
                event.add_str("levelname", record.levelname)
                event.add_str("msg", record.getMessage())
                provider.write(event)

        except (KeyboardInterrupt, SystemExit):
            raise
        # pylint: disable-next=bare-except
        except:
            self.handleError(record)

    def _map_level(self, level):
        if level in ("CRITICAL", "FATAL"):
            return 1
        if level == "ERROR":
            return 2
        if level in ("WARN", "WARNING"):
            return 3
        if level == "INFO":
            return 4
        if level == "DEBUG":
            return 5
        return 0
