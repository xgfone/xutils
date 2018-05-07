xutils
======

A fragmentary Python library, no any third-part dependencies but ``sqlalchemy`` and ``wsgi``.

* a simple argument parser based on CLI and file.
* a simple logging configuration
* circuit breaker
* const
* life manager
* network
* process manager
* resource lock
* resource pool
* rate limit based on token.
* retry call
* sending email
* sqlalchemy
* wsgi
* xml2json

Notice: Only the sub-module ``sqlalchemy`` and ``wsgi`` depend on the third-party packages of ``six``, ``sqlalchemy`` and ``falcon``. If you does't use them, it's no need to install them.

Install
=======

``$ pip install xutils`` or ``$ easy_install xutils`` or ``$ python setup.py install``
