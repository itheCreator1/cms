import logging


security_logger = logging.getLogger("cms.security.auth")


def configure_security_logging():
    if not any(getattr(handler, "_cms_auth_handler", False) for handler in security_logger.handlers):
        handler = logging.StreamHandler()
        handler._cms_auth_handler = True
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s superadmin_login ip=%(client_ip)s outcome=%(outcome)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        security_logger.addHandler(handler)
    security_logger.setLevel(logging.INFO)
    security_logger.propagate = False
    security_logger.disabled = False


def log_superadmin_attempt(client_ip, outcome):
    # Alembic may reconfigure logging in CLI/test processes; restore this
    # dedicated sanitized logger before every security event.
    configure_security_logging()
    security_logger.info(
        "",
        extra={"client_ip": client_ip or "unknown", "outcome": outcome},
    )
