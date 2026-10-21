# Modified 2026-10-22 by weewx-packages: compatibility and tracker repairs.
# Copyright 2014-2020 Matthew Wall
# Distributed under terms of the GPLv3
"""
Emit loop data to wxnow.txt file with Cumulus format

The Cumulus wxnow.txt file format is detailed in the Cumulus Wiki:
    https://cumuluswiki.org/a/Wxnow.txt

Put this file in the weewx 'user' directory, then add the following to the
weewx configuration file:

[CumulusWXNow]
    filename = /path/to/wxnow.txt

[Engine]
    [[Services]]
        process_services = ..., user.cwxn.CumulusWXNow
"""

import time

import weewx
import weewx.wxformulas
import weeutil.weeutil
import weeutil.Sun
from weewx.engine import StdService

try:
    # WeeWX4 logging
    import logging
    from weeutil.logger import log_traceback

    log = logging.getLogger(__name__)

    def logdbg(msg):
        log.debug(msg)

    def loginf(msg):
        log.info(msg)

    def logerr(msg):
        log.error(msg)

    def log_traceback_error(prefix=''):
        log_traceback(log.error, prefix=prefix)

except ImportError:
    # WeeWX legacy (v3) logging via syslog
    import syslog
    from weeutil.weeutil import log_traceback

    def logmsg(level, msg):
        syslog.syslog(level, 'cwxn: %s' % msg)

    def logdbg(msg):
        logmsg(syslog.LOG_DEBUG, msg)

    def loginf(msg):
        logmsg(syslog.LOG_INFO, msg)

    def logerr(msg):
        logmsg(syslog.LOG_ERR, msg)

    def log_traceback_error(prefix=''):
        log_traceback(prefix=prefix, loglevel=syslog.LOG_ERR)

VERSION = "0.6.0"

if weewx.__version__ < "3":
    raise weewx.UnsupportedFeature("WeeWX 3 is required, found %s" %
                                   weewx.__version__)


def convert(v, metric, group, from_unit_system, to_units):
    ut = weewx.units.getStandardUnitType(from_unit_system, metric)
    vt = (v, ut[0], group)
    v = weewx.units.convert(vt, to_units)[0]
    return v


def nullproof(key, data):
    if key in data and data[key] is not None:
        return data[key]
    return None


def calcRainHour(dbm, ts):
    sts = ts - 3600
    val = dbm.getSql("SELECT SUM(rain) FROM %s "
                     "WHERE dateTime>? AND dateTime<=?" % dbm.table_name,
                     (sts, ts))
    if val is None:
        return None
    return val[0]


def calcRain24(dbm, ts):
    sts = ts - 86400
    val = dbm.getSql("SELECT SUM(rain) FROM %s "
                     "WHERE dateTime>? AND dateTime<=?" % dbm.table_name,
                     (sts, ts))
    if val is None:
        return None
    return val[0]


def calcDayRain(dbm, ts):
    sts = weeutil.weeutil.startOfDay(ts)
    val = dbm.getSql("SELECT SUM(rain) FROM %s "
                     "WHERE dateTime>? AND dateTime<=?" % dbm.table_name,
                     (sts, ts))
    if val is None:
        return None
    return val[0]


class CumulusWXNow(StdService):

    def __init__(self, engine, config_dict):
        super(CumulusWXNow, self).__init__(engine, config_dict)
        loginf("service version is %s" % VERSION)
        d = config_dict.get('CumulusWXNow', {})
        self.filename = d.get('filename', '/var/tmp/wxnow.txt')
        binding = d.get('binding', 'loop').lower()
        if binding == 'loop':
            self.bind(weewx.NEW_LOOP_PACKET, self.handle_new_loop)
        else:
            self.bind(weewx.NEW_ARCHIVE_RECORD, self.handle_new_archive)

        loginf("binding is %s" % binding)
        loginf("output goes to %s" % self.filename)

    def handle_new_loop(self, event):
        self.handle_data(event.packet)

    def handle_new_archive(self, event):
        self.handle_data(event.record)

    def handle_data(self, event_data):
        try:
            dbm = self.engine.db_binder.get_manager('wx_binding')
            data = self.calculate(event_data, dbm)
            self.write_data(data)
        except Exception as e:
            log_traceback_error('cwxn: **** ')

    def calculate(self, packet, archive):
        pu = packet.get('usUnits')
        data = dict()
        data['dateTime'] = packet['dateTime']
        data['windDir'] = nullproof('windDir', packet)
        v = nullproof('windSpeed', packet)
        data['windSpeed'] = convert(v, 'windSpeed', 'group_speed', pu, 'mile_per_hour')
        v = nullproof('windGust', packet)
        data['windGust'] = convert(v, 'windGust', 'group_speed', pu, 'mile_per_hour')
        v = nullproof('outTemp', packet)
        data['outTemp'] = convert(v, 'outTemp', 'group_temperature', pu, 'degree_F')
        v = calcRainHour(archive, data['dateTime'])
        data['hourRain'] = convert(v, 'rain', 'group_rain', pu, 'inch')
        if 'rain24' in packet:
            v = nullproof('rain24', packet)
        else:
            v = calcRain24(archive, data['dateTime'])
        data['rain24'] = convert(v, 'rain', 'group_rain', pu, 'inch')
        if 'dayRain' in packet:
            v = nullproof('dayRain', packet)
        else:
            v = calcDayRain(archive, data['dateTime'])
        data['dayRain'] = convert(v, 'rain', 'group_rain', pu, 'inch')
        data['outHumidity'] = nullproof('outHumidity', packet)
        v = nullproof('barometer', packet)
        data['barometer'] = convert(v, 'pressure', 'group_pressure', pu, 'mbar')
        return data

    def write_data(self, data):
        def field(key, width, prefix='', scale=1):
            value = data.get(key)
            text = ' ' * width if value is None else '%0*d' % (width, int(value * scale))
            return prefix + text

        fields = [field('windDir', 3), field('windSpeed', 3, '/'),
                  field('windGust', 3, 'g'), field('outTemp', 3, 't'),
                  field('hourRain', 3, 'r', 100), field('rain24', 3, 'p', 100),
                  field('dayRain', 3, 'P', 100)]
        humidity = data.get('outHumidity')
        if humidity is None or not 0 <= humidity <= 100:
            fields.append('h  ')
        else:
            # APRS reserves 00 for saturation; its lowest representable value is 1%.
            fields.append('h%02d' % (0 if humidity == 100 else max(1, int(humidity))))
        fields.append(field('barometer', 5, 'b', 10))
        with open(self.filename, 'w') as f:
            f.write(time.strftime("%b %d %Y %H:%M\n",
                                  time.localtime(data['dateTime'])))
            f.write(''.join(fields))
            f.write("\n")
