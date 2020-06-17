from exportplan import helpers


def test_country_code_iso3_to_iso2():
    assert helpers.country_code_iso3_to_iso2('CHN') == 'CN'


def test_country_code_iso3_to_iso2_not_found():
    assert helpers.country_code_iso3_to_iso2('XNY') is None


def test_get_timezone():
    assert helpers.get_timezone('CHN') == 'Asia/Shanghai'


def test_get_local_time_not_found():
    assert helpers.get_timezone('XS') is None


def test_get_iso3_by_country_name():
    assert helpers.get_iso3_by_country_name('Australia') == 'AUS'


def test_get_iso3_by_country_name_upper():
    assert helpers.get_iso3_by_country_name('AUSTRALIA') == 'AUS'


def test_get_iso3_by_country_name_lower():
    assert helpers.get_iso3_by_country_name('australia') == 'AUS'


def test_get_iso3_by_country_name_none():
    assert helpers.get_iso3_by_country_name(None) is None
