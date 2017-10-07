"""
Example09: TLS
"""

import wysteria
import ssl


def main():
    client = wysteria.Client(tls=wysteria.TlsConfig(
        ca_certs="/path/to/foo.ca.cert",
        keyfile="/path/to/foo.key",
        certfile="/path/to/foo.cert",
        cert_reqs=ssl.CERT_REQUIRED,
    ))
    with client:
        tiles = client.get_collection("tiles")
        print tiles

    # Or a less secure route, with some homemade self-signed certs..
    wysteria.Client(tls=wysteria.TlsConfig(
        keyfile="/path/to/foo.key",
        certfile="/path/to/foo.cert",
        cert_reqs=ssl.CERT_NONE,
    ))


if __name__ == "__main__":
    main()
