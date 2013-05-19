
from common import unittest2

import pycares
from evergreen.ext import dns


class DNSTest(unittest2.TestCase):

    def setUp(self):
        self.resolver = dns.DNSResolver()

    def tearDown(self):
        self.resolver = None

    def test_query_a(self):
        result = self.resolver.query('google.com', 'A')
        self.assertTrue(result)

    def test_query_a_bad(self):
        try:
            self.resolver.query('hgf8g2od29hdohid.com', 'A')
        except dns.error.DNSError as e:
            self.assertEqual(e.args[0], dns.error.ARES_ENOTFOUND)

    def test_query_aaaa(self):
        result = self.resolver.query('ipv6.google.com', 'AAAA')
        self.assertTrue(result)

    #def test_query_cname(self):
    #    result = self.resolver.query('www.google.com', 'CNAME')
    #    self.assertTrue(result)

    def test_query_mx(self):
        result = self.resolver.query('google.com', 'MX')
        self.assertTrue(result)

    def test_query_ns(self):
        result = self.resolver.query('google.com', 'NS')
        self.assertTrue(result)

    def test_query_txt(self):
        result = self.resolver.query('google.com', 'TXT')
        self.assertTrue(result)

    def test_query_soa(self):
        result = self.resolver.query('google.com', 'SOA')
        self.assertTrue(result)

    def test_query_srv(self):
        result = self.resolver.query('_xmpp-server._tcp.google.com', 'SRV')
        self.assertTrue(result)

    def test_query_naptr(self):
        result = self.resolver.query('sip2sip.info', 'NAPTR')
        self.assertTrue(result)

    def test_query_ptr(self):
        ip = '173.194.69.102'
        result = self.resolver.query(pycares.reverse_address(ip), 'PTR')
        self.assertTrue(result)

    def test_resolver_closed(self):
        self.resolver.close()
        self.assertRaises(pycares.AresError, self.resolver.query, 'google.com', 'A')

    def test_query_bad_type(self):
        self.assertRaises(dns.error.DNSError, self.resolver.query, 'google.com', 'XXX')

    def test_query_timeout(self):
        self.resolver = dns.DNSResolver(timeout=0.1)
        self.resolver.nameservers = ['1.2.3.4']
        try:
            self.resolver.query('google.com', 'A')
        except dns.error.DNSError as e:
            self.assertEqual(e.args[0], dns.error.ARES_ETIMEOUT)


if __name__ == '__main__':
    unittest2.main(verbosity=2)

