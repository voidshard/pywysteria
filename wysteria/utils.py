import os
import ssl
import configparser

from wysteria.client import Client


_DEFAULT_FILENAME = "wysteria-client.ini"
_DEFAULT_ENV_VAR = "WYSTERIA_CLIENT_INI"

_KEY_MWARE = "middleware"
_KEY_MWARE_DRIVER = "driver"
_KEY_MWARE_CONF = "config"
_KEY_MWARE_SSL_CERT = "sslcert"
_KEY_MWARE_SSL_KEY = "sslkey"
_KEY_MWARE_SSL_VERIFY = "SSLVerify"
_KEY_MWARE_SSL_ENABLE = "sslenabletls"


def _wysteria_config() -> str:
    """Return path to default config, if found

    Returns:
        str or None
    """
    for f in [_DEFAULT_FILENAME, os.environ.get(_DEFAULT_ENV_VAR)]:
        if not f:
            continue
        if os.path.exists(f):
            return f
    return None


def _read_config(configpath: str) -> dict:
    """Read in config file & return as dict

    Args:
        configpath (str):

    Returns:
        dict
    """
    config = configparser.ConfigParser()
    config.read(configpath)

    data = {}
    for section in config.sections():
        data[section.lower()] = {}
        for opt in config.options(section):
            data[section.lower()][opt.lower()] = config.get(section, opt)
    return data


def _load_ssl_context(key, cert, verify=False):
    """Util func to load an ssl context.

    Args:
        key (str): path to file
        cert (str): path to file
        verify (bool): if true, we'll verify the server's certs

    Returns:
        ssl_context
    """
    purpose = ssl.Purpose.SERVER_AUTH if verify else ssl.Purpose.CLIENT_AUTH
    tls = ssl.create_default_context(purpose=purpose)
    tls.protocol = ssl.PROTOCOL_TLSv1_2
    tls.load_cert_chain(certfile=cert, keyfile=key)
    return tls


def from_config(configpath: str) -> Client:
    """Build a wysteria Client from a given config file.

    Args:
        configpath (str): path to a config file

    Returns:
        wysteria.Client
    """
    data = _read_config(configpath)
    middleware = data.get(_KEY_MWARE, {})

    tls = None

    if middleware.get(_KEY_MWARE_SSL_ENABLE, False):
        tls = _load_ssl_context(
            middleware.get(_KEY_MWARE_SSL_KEY),
            middleware.get(_KEY_MWARE_SSL_CERT),
            middleware.get(_KEY_MWARE_SSL_VERIFY, False)
        )

    return Client(
        url=middleware.get(_KEY_MWARE_CONF),
        middleware=middleware.get(_KEY_MWARE_DRIVER, "nats"),
        tls=tls,
    )


def default_client() -> Client:
    """Build a wysteria client, checking default config locations (in order)
        - wysteria-client.ini
        - WYSTERIA_CLIENT_INI (env var)

    And falling back to a default config (no ssl & nats on the localhost).

    For security purposes, it is generally recommended you build the client
    youself, using your own certs & requiring signed certs to be presented by
    the server.

    Returns:
        wysteria.Client
    """
    config_file = _wysteria_config()
    if not config_file:
        return Client()  # default with no extra config
    return from_config(config_file)
