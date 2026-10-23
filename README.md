# Cumulus wxnow output for WeeWX

Write LOOP readings to a two-line `wxnow.txt` file for software that reads the
[Cumulus wxnow format](https://cumuluswiki.org/a/Wxnow.txt). Rain totals come from
the WeeWX archive when the packet does not provide them.

This is the weewx-packages continuation, release **0.6.1**.
[Origin](ORIGIN.md) records the upstream revision; [repair notes](REPAIR_NOTES.md)
describe the maintenance changes.

The catalog archive targets WeeWX `>=5.5.2,<5.7` and Python `>=3.10,<3.15`.

## Install

Use `weectl` from the Python environment running WeeWX. With stock WeeWX 5,
install the published archive:

```sh
weectl extension install https://github.com/weewx-packages/weewx-cwxn/releases/download/v0.6.1/weewx-cwxn-0.6.1.tar.gz --config /path/to/weewx.conf
```

Replace `/path/to/weewx.conf` with your station configuration. You can also
download that URL and pass the local archive to the same command. Use elevated
permissions only when your station files require them.

## Write the file

No extra Python packages or external account are required. The installer adds
`user.cwxn.CumulusWXNow` to the process services and configures:

```ini
[CumulusWXNow]
    filename = /var/tmp/wxnow.txt
```

The WeeWX service user must be able to write the destination directory. Restart
WeeWX yourself, then inspect the file after a LOOP packet. To write once per
archive record instead, add `binding = archive` to this section.

The output uses local time, Fahrenheit, mph, hundredths of an inch for rain,
and tenths of a millibar for pressure, independently of your database units.
Missing values occupy blank fields. Humidity uses APRS encoding, with `h00`
for 100% and `h01` for values below 1%.

## Limits

The service reads the `wx_binding` archive for hourly, daily and 24-hour rain.
A writable destination and a working archive binding are required. Partial
LOOP packets can leave fields blank. Publishing the file or passing it to an
APRS application is a separate task; this service does not transmit it.

Copyright 2014-2020 Matthew Wall. [GNU GPLv3](license).
