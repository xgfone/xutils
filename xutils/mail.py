# -*- coding: utf-8 -*-

import time
import os.path
import smtplib
import mimetypes
import logging

from threading import Lock, RLock
from email.utils import formatdate
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage

LOG = logging.getLogger(__name__)

_append_type_ext = {
    ".docx": "application/msword",
    ".pptx": "application/x-ppt",
    ".xlsx": "application/x-xls",
}

for _type, _ext in _append_type_ext.items():
    mimetypes.add_type(_type, _ext)


def get_attr(obj, name, default=None):
    if hasattr(obj, name):
        return getattr(obj, name)
    elif name in obj:
        return obj[name]
    return default


def get_type_by_filename(filename, default=None):
    fn, ext = os.path.splitext(filename)
    _type = default
    if ext:
        if ext in mimetypes.suffix_map:
            _type = mimetypes.types_map.get(".tar")
        elif ext in mimetypes.encodings_map:
            fn, ext = os.path.splitext(fn)
            if ext:
                _type = mimetypes.types_map.get(ext)
        else:
            _type = mimetypes.types_map.get(ext)
    return _type


class EMail(object):
    _default_type = MIMEApplication
    _type_map = {
        "application": MIMEApplication,
        "image": MIMEImage,
        "text": MIMEText,
        "audio": MIMEAudio,
    }

    def __init__(self, username=None, password=None, _from=None, host=None,
                 port=25, postfix=None, keepalived=0):
        """postfix is deprecated."""

        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self._from = _from
        self._keepalived = int(keepalived)
        self._server = (None, 0)
        self._lock = RLock()

    def check_server(self):
        if self._keepalived > 0:
            server, _time = self._server
            if server and int(time.time()) - _time > self._keepalived:
                self._set_server(server, close=True)
                return False
        return True

    def _set_server(self, server, now=None, close=False, save=True):
        if server and close:
            try:
                LOG.debug('close the mail connection')
                server.close()
            except Exception:
                pass
            server = None

        if save and self._keepalived > 0:
            with self._lock:
                self._server = (server, now or int(time.time()))

    def _get_server(self):
        if self._keepalived < 1:
            self.get_connect(self.host, self.port, self.username, self.password)

        with self._lock:
            server, _time = self._server
            if server:
                if int(time.time()) - _time < self._keepalived:
                    return server
                else:
                    self._set_server(server, close=True, save=False)
            return self.get_connect(self.host, self.port, self.username, self.password)

    def get_connect(self, host, port, username, password):
        if not host or not port:
            raise ValueError("invalid arguments")
        server = smtplib.SMTP()
        server.connect(host, port)
        server.login(username, password)
        LOG.debug('Open the mail connection')
        return server

    def _send(self, tos, msg):
        server = self._get_server()
        try:
            server.sendmail(self._from, tos, msg.as_string())
        except Exception:
            self._set_server(server, close=True)
            raise
        else:
            self._set_server(server)

    def send(self, tos, msg):
        if self._keepalived < 1:
            self._send(tos, msg)
            return

        with self._lock:
            self._send(tos, msg)

    def _pad_header(self, msg, subject, tos):
        msg["Subject"] = subject
        msg["From"] = self._from
        msg["To"] = ";".join(tos) if isinstance(tos, (list, tuple)) else tos
        msg["Date"] = formatdate()
        return msg

    def get_simple_msg(self, to_list, subject, content='', subtype="html", charset="utf8"):
        msg = MIMEText(content, subtype, charset)
        return self._pad_header(msg, subject, to_list)

    def get_message(self, to_list, subject, content='', subtype="html", charset="utf8",
                    attachmets=None, content_type="application/octet-stream"):
        msg = self._pad_header(MIMEMultipart(), subject, to_list)

        att = MIMEText(content, subtype, charset)
        msg.attach(att)

        attachmets = attachmets if attachmets else []
        for att in attachmets:
            _filename = att["filename"]
            _content = get_attr(att, "content")
            _type = get_attr(att, "content-type")
            _type = _type if _type else get_type_by_filename(_filename, content_type)

            _maintype, _subtype = _type.split('/')
            mime_class = self._type_map.get(_maintype, self._default_type)
            if mime_class is MIMEText:
                _charset = get_attr(att, "charset", charset)
                _att = MIMEText(_content, _subtype, _charset)
            else:
                _att = mime_class(_content, _subtype)

            _att["Content-Type"] = _type
            _att["Content-Disposition"] = 'attachmet;filename="%s"' % _filename
            msg.attach(_att)

    def send_simple_msg(self, to_list, subject, content='', subtype="html", charset="utf8"):
        msg = self.get_simple_msg(to_list, subject, content=content,
                                  subtype=subtype, charset=charset)
        self.send(to_list, msg)

    def send_message(self, to_list, subject, content='', subtype="html", charset="utf8",
                     attachmets=None, content_type="application/octet-stream"):
        msg = self.get_message(to_list, subject, content=content, subtype=subtype,
                               charset=charset, attachmets=attachmets,
                               content_type=content_type)
        self.send(to_list, msg)


class EMailCache(object):
    Mail = EMail

    def __init__(self, get_key=None):
        """Return a new EMailCache, which is the thread-safe.

        @get_key(function): a function returned the key of the email object,
                            which receives three arguments,
                            (mail_server_host, mail_server_port, mail_from).
        """

        self._caches = {}
        self._lock = Lock()
        self._get_key = get_key if get_key else self.__get_key

    def __get_key(self, host, port, _from):
        return "{0}_{1}_{2}".format(host, port, _from)

    def add_email(self, username=None, password=None, _from=None, host=None,
                  port=25, keepalived=0):
        key = self._get_key(host, port, _from)
        email = self.Mail(username=username, password=password, _from=_from,
                          host=host, port=port, keepalived=keepalived)
        with self._lock:
            self._caches[key] = email

    def get_email(self, host, port, _from, default=None):
        """Return the email object by host, port, from.

        If there is not the cached email object, it returns the default,
        not raises the exception.
        """

        key = self._get_key(host, port, _from)
        with self._lock:
            return self._caches.get(key, default)
