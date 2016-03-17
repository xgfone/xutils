xutils
======

A fragmentary Python library.

* const
* daemon
* escape
* functions
* hash_ring
* dictConfig of logging
* mail
* network
* objects
* oslodb
* osloi18n
* password
* server
* string
* url
* version
* xml2json

Install
=======

``$ pip install xutils``

Notice
------

These packages below are not installed automatically, and you need to add them into requirements.txt in you application, if you want to use the functions related to them in this package.

* oslo.i18n
* oslo.utils
* oslo.service
* oslo.db

Dependency Relationship
-----------------------

================  ============
    Dependent       Depended
================  ============
 xutils.oslodb     oslo.db
 xutils.server     oslo.service
 xutils.osloi18n   oslo.i18n
 xutils.string     oslo.utils
================  ============

These packages are independent of one another. If you do not use one of them, it is needless to install the package that it depends on.
