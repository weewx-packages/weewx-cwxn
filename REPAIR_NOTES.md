# Repair validation

Version 0.6.0. Original repository and revision are in ORIGIN.md.

* https://github.com/matthewwall/weewx-cwxn/pull/3: Missing sensor/rain values remain blank; zero and negative temperature survive. Reimplemented without dropping real rain values.
* https://github.com/matthewwall/weewx-cwxn/issues/2: Two-character humidity with explicit 0/1/99/100, missing and invalid limits.
* https://github.com/matthewwall/weewx-cwxn/pull/1: Two-character humidity; 100%=00; missing values remain blank.

Tests run under WeeWX 4.10.2/5.1.0 on Python 3.10 and WeeWX 5.5.2 on Python 3.14. Local receivers and isolated install directories avoid live station changes. The tests do not establish individual external account permissions.
