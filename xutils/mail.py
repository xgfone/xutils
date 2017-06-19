#!/usr/bin/env python
# encoding: utf-8
from __future__ import absolute_import

import os.path

import smtplib
import mimetypes
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
                 port=25, postfix=None):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.postfix = postfix
        self._from = _from

    def send(self, tos, msg, host=None, port=None, username=None, password=None,
             _from=None):
        host = host if host else self.host
        port = port if port else self.port
        username = username if username else self.username
        password = password if password else self.password
        _from = _from if _from else self._from

        if not host or not port or not _from or not tos or not msg:
            raise ValueError("invalid arguments")

        server = smtplib.SMTP()
        server.connect(host, port)
        server.login(username, password)
        server.sendmail(_from, tos, msg.as_string())
        server.close()
        # server.quit()

    def get_simple_msg(self, to_list, subject, content='', subtype="html", charset="utf8"):
        msg = MIMEText(content, subtype, charset)
        msg["Subject"] = subject
        msg["From"] = self._from
        msg["To"] = ";".join(to_list)
        return msg

    def get_message(self, to_list, subject, content='', subtype="html", charset="utf8",
                    attachmets=None, content_type="application/octet-stream"):
        msg = MIMEMultipart()
        msg["From"] = self._from
        msg["To"] = ';'.join((to_list))
        msg["Subject"] = subject

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


def test():
    host = "smtp.grandcloud.cn"
    port = 25
    username = "xgfone"
    passwd = "123456"
    _from = "xgfone@126.com"
    _tos = ["xgfone@126.com"]
    subject = "test"
    content = "test"

    # with open("img.gif", "r+b") as f:
    #     data1 = f.read()
    # with open("syncdb.tar.gz", 'r+b') as f:
    #     data2 = f.read()
    # with open("test.docx", 'r+b') as f:
    #     data3 = f.read()
    # with open("test.txt", encoding="utf8") as f:
    #     data4 = f.read()
    # attachmets = [
    #     {
    #         "content": data1,
    #         "filename": "img.gif",
    #         # "content-type": "image/gif"
    #     },
    #     {
    #         "content": data2,
    #         "filename": "syncdb.tar.gz",
    #         # "content-type": "application/x-tar"
    #     },
    #     {
    #         "content": data3,
    #         "filename": "test.doc",
    #         # "content-type": "application/msword",
    #     },
    #     {
    #         "content": data4,
    #         "filename": "test.txt",
    #         # "content-type": "text/plain",
    #         # "charset": "utf8",
    #     },
    # ]

    mail = EMail(username, passwd, _from, host, port)
    mail.send_message(_tos, subject, content=content)
    # mail.send_message(_tos, subject, content=content, attachmets=attachmets)


if __name__ == "__main__":
    test()
