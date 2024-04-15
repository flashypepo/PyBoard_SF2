# Logging

import ulogger

handler_to_term = ulogger.Handler(
    level=ulogger.INFO,
    colorful=True,
    fmt="&(time)% - &(level)% - &(name)% - &(fnname)% - &(msg)%",
    clock=None,
    direction=ulogger.TO_TERM,
)

# only logging to file if level is ERROR or CRITICAL
handler_to_file = ulogger.Handler(
    level=ulogger.ERROR,
    fmt="&(time)% - &(level)% - &(name)% - &(fnname)% - &(msg)%",
    clock=None,
    direction=ulogger.TO_FILE,
    file_name="logging.log",
    max_file_size=1024 # max for 1k
)

logger = ulogger.Logger(
    name = __name__,
    handlers = (
        handler_to_term,
        handler_to_file,
    )
)

logger.info("Logging imported... use 'logger'", fn=__name__)

