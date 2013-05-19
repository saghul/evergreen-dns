
================================================
evergreen-dns: Simple DNS resolver for Evergreen
================================================

Evergreen-DNS provides a simple way for doing asynchronous DNS resolutions
with a synchronous interface by combining `pycares <https://github.com/saghul/pycares>`_ and
`evergreen <https://github.com/saghul/evergreen>`_.


Usage
=====

Example:

::

    from evergreen.ext import dns

    resolver = dns.DNSResolver()
    print(resolver.query('google.com','A'))


The following query types are supported: A, AAA, CNAME, MX, NAPTR, NS, PTR, SOA, SRV, TXT.


Running the test suite
======================

To run the test suite: ``nosetests -v -w tests/``


Author
======

Saúl Ibarra Corretgé <saghul@gmail.com>


License
=======

Evergreen-DNS uses the MIT license, check LICENSE file.


Python versions
===============

Python >= 2.6 is supported. Yes, that includes Python 3 :-)


Contributing
============

If you'd like to contribute, fork the project, make a patch and send a pull
request. Have a look at the surrounding code and please, make yours look
alike :-)

