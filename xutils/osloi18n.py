# coding: utf-8
import oslo_i18n

_translators = _ = _C = _P = _LI = _LW = _LE = _LC = None


def get_translator(domain="app", localedir=None, lazy=True):
    # Enable lazy translation
    if lazy:
        oslo_i18n.enable_lazy()

    return oslo_i18n.TranslatorFactory(domain=domain, localedir=localedir)


def reset_i18n(domain="app", localedir=None, lazy=True):
    global _translators, _, _C, _P, _LI, _LW, _LE, _LC

    _translators = get_translator(domain=domain, localedir=localedir, lazy=lazy)

    # The primary translation function using the well-known name "_"
    _ = _translators.primary

    # The contextual translation function using the name "_C"
    _C = _translators.contextual_form

    # The plural translation function using the name "_P"
    _P = _translators.plural_form

    # Translators for log levels.
    #
    # The abbreviated names are meant to reflect the usual use of a short
    # name like '_'. The "L" is for "log" and the other letter comes from
    # the level.
    _LI = _translators.log_info
    _LW = _translators.log_warning
    _LE = _translators.log_error
    _LC = _translators.log_critical


reset_i18n()
