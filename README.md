# Cumulus wxnow output

Write LOOP readings to a two-line `wxnow.txt` file for software that reads the
[Cumulus wxnow format](https://cumuluswiki.org/a/Wxnow.txt). The service writes
a local file only; it does not publish or transmit it.

Independent continuation of
[matthewwall/weewx-cwxn](https://github.com/matthewwall/weewx-cwxn).
[ORIGIN.md](ORIGIN.md) records the upstream revision and
[REPAIR_NOTES.md](REPAIR_NOTES.md) describes the maintenance changes.

## Requirements

- The `wx_binding` archive database. It supplies the rain totals.
- Write permission for the WeeWX user in the destination directory.
- No Python package beyond WeeWX and no external account.

## Installation

Install `cwxn` from the [WeeWX packages catalog](https://github.com/weewx-packages/catalog/blob/main/packages/cwxn.md).
The catalog page lists the current release, its WeeWX and Python
requirements, and the install, update and removal commands.

The installer adds `user.cwxn.CumulusWXNow` to the process services and
configures:

```ini
[CumulusWXNow]
    filename = /var/tmp/wxnow.txt
```

After a LOOP packet, inspect the file.

## Configuration

```ini
[CumulusWXNow]
    filename = /var/tmp/wxnow.txt
    binding = archive
```

| Option | Default | Meaning |
| --- | --- | --- |
| `filename` | `/var/tmp/wxnow.txt` | Path of the output file. |
| `binding` | `loop` | `loop` writes on every LOOP packet. Any other value, for example `archive`, writes on archive records. |

The first line holds the local time of the reading. The second line uses
Fahrenheit, mph, hundredths of an inch for rain and tenths of a millibar for
pressure, independently of your database units. Missing values occupy blank
fields. Humidity uses APRS encoding, with `h00` for 100% and `h01` for values
below 1%.

Rain in the last hour comes from the archive. The 24-hour and daily totals come
from the packet's `rain24` and `dayRain` when present, otherwise from the
archive.

## Limitations

- Partial LOOP packets leave the missing fields blank.

## Development

Run `python -m pytest -q` in an environment with WeeWX and pytest installed.

## License

Copyright 2014-2020 Matthew Wall.
Distributed under the terms of the [GNU GPLv3](license).
