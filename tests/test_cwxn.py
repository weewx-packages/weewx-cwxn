import re

import pytest
import weewx
import cwxn


class Archive:
    table_name = 'archive'

    def getSql(self, sql, params):
        return (None,)


def render(tmp_path, packet):
    service = cwxn.CumulusWXNow.__new__(cwxn.CumulusWXNow)
    service.filename = str(tmp_path / 'wxnow.txt')
    data = service.calculate(dict(dateTime=1700000000, usUnits=weewx.METRIC, **packet), Archive())
    service.write_data(data)
    return (tmp_path / 'wxnow.txt').read_text().splitlines()[1]


@pytest.mark.parametrize('humidity,expected', [(59,'59'),(100,'00'),(0,'01'),(1,'01'),(99,'99'),(None,'  '),(-1,'  '),(101,'  ')])
def test_humidity_width_and_limits(tmp_path, humidity, expected):
    output = render(tmp_path, {'outHumidity': humidity})
    assert re.search(r'h(.*?)b', output).group(1) == expected


def test_missing_values_and_zero_are_distinct(tmp_path):
    assert render(tmp_path, {}) == '   /   g   t   r   p   P   h  b     '
    output = render(tmp_path, {'windSpeed': 0, 'outTemp': 0, 'barometer': 0, 'dayRain': 0, 'rain24': 0})
    assert output == '   /000g   t032r   p000P000h  b00000'


def test_rain_and_negative_temperature_survive(tmp_path):
    output = render(tmp_path, {'outTemp': -20, 'dayRain': 2.54, 'rain24': 0.254, 'windSpeed': 16.09344})
    assert '/010g   t-04' in output
    assert 'p010P100' in output


@pytest.mark.parametrize('units,rain', [(weewx.METRICWX,25.4),(weewx.METRIC,2.54),(weewx.US,1)])
def test_archive_rain_uses_archive_units(units, rain):
    class RainArchive:
        table_name = 'archive'

        def getSql(self, sql, params=()):
            return (units,) if 'usUnits' in sql else (rain,)

    service = cwxn.CumulusWXNow.__new__(cwxn.CumulusWXNow)
    packet = {'dateTime':1700000000,'usUnits':weewx.US,'dayRain':2,'rain24':0}
    data = service.calculate(packet, RainArchive())
    assert data['hourRain'] == pytest.approx(1)
    assert data['dayRain'] == 2
    assert data['rain24'] == 0
    data = service.calculate({'dateTime':1700000000,'usUnits':weewx.US}, RainArchive())
    assert data['rain24'] == pytest.approx(1)
    assert data['dayRain'] == pytest.approx(1)
