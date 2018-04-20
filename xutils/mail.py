# -*- coding: utf-8 -*-

import os.path
import smtplib
import mimetypes

from email.utils import formatdate
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage

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
                 port=25, postfix=None, keepalived=False):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.postfix = postfix
        self._from = _from
        self._keepalived = keepalived
        self._server = None

    def get_connect(self, host, port, username, password, reset=False):
        if not host or not port:
            raise ValueError("invalid arguments")

        server = smtplib.SMTP()
        server.connect(host, port)
        server.login(username, password)
        if reset:
            self._server = server
        return server

    def send(self, tos, msg):
        if self._server:
            server = self._server
        else:
            server = self.get_connect(self.host, self.port, self.username,
                                      self.password)

        try:
            server.sendmail(self._from, tos, msg.as_string())
        except Exception:
            self._server = None
            server.close()
            raise
        else:
            if self._keepalived:
                self._server = server
            else:
                server.close()

    def _pad_header(self, msg, subject, tos):
        msg["Subject"] = subject
        msg["From"] = self._from
        msg["To"] = ";".join(tos)
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
