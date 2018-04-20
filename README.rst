xutils
======

A fragmentary Python library, no any third-part dependencies but ``sqlalchemy``.

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
* xml2json

Notice: Only the sub-module ``sqlalchemy`` depend on the third-party packages of ``six`` and ``sqlalchemy``. If you does't use it, it's no need to install them.

Install
=======

``$ pip install xutils`` or ``$ easy_install xutils`` or ``$ python setup.py install``
