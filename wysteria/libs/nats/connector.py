'''\
Class Connector:
    - connection between client and nats server;

Attributes;
    - conn_opts: connection options, including auth parameters;
    - sock :  socket
    - connected: conection status;
    - data_recv: data receive thread, waiting for data from nats server;
    - pending: pending messages record;

'''

from wysteria.libs.nats.error import NatsConnectException
from wysteria.libs.nats.common import Common
import socket
import threading


class Connector(object):
    "connector class"

    _DEFAULT_CONN_OPTS = {
        "user": "nats",
        "pswd": "nats",  # pass in nats server
        "verbose": True,
        "pedantic": True,
        "ssl_required": False,
    }

    def __init__(self, **options):
        self.conn_opts = {}
        for (kwd, default) in self._DEFAULT_CONN_OPTS.items():
            if kwd in options:
                value = options[kwd]
            else:
                value = default
            self.conn_opts[kwd] = value
        self.conn_opts['user'], self.conn_opts['pass'], self.host, self.port = \
                     Common.parse_address_info(options.get("uris"))

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.callback = options['callback']
        self._listen = False
        self.data_recv = threading.Thread(target=self._waiting_data)
        self.pending = []

    def open(self):
        '''\
        connect to nats server, the socket will use default gevent paramters :
            - family = AF_INET
            - type = SOCKE_STREAM
            - protocol = auto detect

        Params:
        =====
        host: nats server ip address;
        port: nats server listen port;

        Returns:
        =====
        client: nats connection;
        error: error destription if exists;
        '''
        self.sock.connect((self.host, self.port))
        self.connected = True
        self.data_recv.setDaemon(True)
        self.data_recv.start()

    def flush_pending(self):
        "flush pending data of current connection."

        if not self.connected or not self.pending:
            return
        try:
            self.sock.sendall("".join(self.pending))
            self.pending = []
        except Exception as ex:
            self._on_connection_lost(ex)

    def close(self):
        'close the connection'
        self._listen = False
        if self.pending:
            self.flush_pending()
        self._on_connection_lost(None)

    def _waiting_data(self):
        'waiting for data from nats server'
        self._listen = True  # set that I am listening

        while self.connected and self._listen:
            try:
                data = self.sock.recv(2048)
            except Exception as ex:
                self._on_connection_lost(ex)
                break

            if data:
                self.callback(data)
        print "EXIT"

    def _on_connection_lost(self, exception):
        '''\
        action if connection losted, actions including:
        1. cancel data receiver; (@2014-04-06)
        2. cancel ping timer; (@2014-04-06)
        '''
        self.connected = False
        self._listen = False
        self.sock.shutdown(1)

        if exception:
            raise exception

    def get_connection_options(self):
        'get the connection options'
        return self.conn_opts

    def send_command(self, command, priority=False):
        '''
        send command to nats server;

        Params:
        =====
        command: the command string;
        priority: command priority;
        '''
        if not priority:
            self.pending.append(command)
        if priority:
            self.pending.insert(0, command)
        self.flush_pending()
