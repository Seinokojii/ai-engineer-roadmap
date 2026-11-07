"""Project exceptions.

One base class lets callers catch everything "ours" with a single except, while the
subclasses say what actually broke and whether a retry makes sense.

    Exception
     └─ AiengError
         ├─ ProviderError      model unreachable, timeout: retrying may help
         └─ ValidationFailed   data or model output does not match the schema
"""


class AiengError(Exception):
    """Base class for every error raised by aieng."""


class ProviderError(AiengError):
    """The model provider failed: connection, timeout, 5xx."""


class ValidationFailed(AiengError):
    """Input or model output did not pass validation."""
