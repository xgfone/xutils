# encoding: utf-8


### Attribute Wrapper
class AttrWrapper(object):
    attrs = []

    def __setattr__(self, name, value):
        if name not in self.attrs:
            raise AttributeError("'%s' is not supported" % name)
        object.__setattr__(self, name, value)

    def __repr__(self):
        attrs = []
        template = "%s=%s"
        for name in self.attrs:
            try:
                attrs.append(template % (name, getattr(self, name)))
            except AttributeError:
                pass

        return "%s(%s)" % (self.__class__.__name__, ", ".join(attrs))
