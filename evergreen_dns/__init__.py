
import evergreen
import pycares

from evergreen_dns import error
from evergreen.futures import Future

__all__ = ('DNSResolver', 'error')


READ = 1
WRITE = 2
query_type_map = {'A'     : pycares.QUERY_TYPE_A,
                  'AAAA'  : pycares.QUERY_TYPE_AAAA,
                  'CNAME' : pycares.QUERY_TYPE_CNAME,
                  'MX'    : pycares.QUERY_TYPE_MX,
                  'NAPTR' : pycares.QUERY_TYPE_NAPTR,
                  'NS'    : pycares.QUERY_TYPE_NS,
                  'PTR'   : pycares.QUERY_TYPE_PTR,
                  'SOA'   : pycares.QUERY_TYPE_SOA,
                  'SRV'   : pycares.QUERY_TYPE_SRV,
                  'TXT'   : pycares.QUERY_TYPE_TXT
        }

class DNSResolver(object):

    def __init__(self, nameservers=None, **kwargs):
        self._channel = pycares.Channel(sock_state_cb=self._sock_state_cb, **kwargs)
        if nameservers:
            self._channel.servers = nameservers
        self._loop = evergreen.current.loop
        self._read_fds = set()
        self._write_fds = set()
        self._timer = None

    @property
    def nameservers(self):
        return self._channel.servers

    @nameservers.setter
    def nameservers(self, value):
        self._channel.servers = value

    def query(self, host, qtype):
        try:
            qtype = query_type_map[qtype]
        except KeyError:
            raise error.DNSError('invalid query type: {}'.format(qtype))
        fut = Future()
        def cb(result, errorno):
            if errorno is not None:
                fut.set_exception(error.DNSError(errorno, pycares.errno.strerror(errorno)))
            else:
                fut.set_result(result)
        self._channel.query(host, qtype, cb)
        return fut.get()

    def close(self):
        self._channel.destroy()

    def _sock_state_cb(self, fd, readable, writable):
        if readable or writable:
            if readable and fd not in self._read_fds:
                self._loop.add_reader(fd, self._handle_event, fd, READ)
                self._read_fds.add(fd)
            if writable and fd not in self._write_fds:
                self._loop.add_writer(fd, self._handle_event, fd, WRITE)
                self._write_fds.add(fd)
            if not self._timer:
                self._timer = self._loop.call_later(1, self._timer_cb)
        else:
            # socket is now closed
            self._read_fds.discard(fd)
            self._write_fds.discard(fd)
            self._loop.remove_reader(fd)
            self._loop.remove_writer(fd)
            if not self._read_fds and not self._write_fds:
                self._timer.cancel()
                self._timer = None

    def _handle_event(self, fd, event):
        read_fd = pycares.ARES_SOCKET_BAD
        write_fd = pycares.ARES_SOCKET_BAD
        if event == READ:
            read_fd = fd
        elif event == WRITE:
            write_fd = fd
        self._channel.process_fd(read_fd, write_fd)

    def _timer_cb(self):
        self._channel.process_fd(pycares.ARES_SOCKET_BAD, pycares.ARES_SOCKET_BAD)
        self._timer = self._loop.call_later(1, self._timer_cb)

