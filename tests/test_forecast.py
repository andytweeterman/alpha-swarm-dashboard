import pytest
from datetime import datetime, timedelta
from utils import generate_forecast

def test_forecast_structure():
    start_date = datetime(2023, 1, 1)
    last_price = 100.0
    last_std = 1.0
    days = 10

    dates, means, uppers, lowers = generate_forecast(start_date, last_price, last_std, days)

    assert len(dates) == days
    assert len(means) == days
    assert len(uppers) == days
    assert len(lowers) == days
    assert isinstance(dates[0], datetime) or isinstance(dates[0], type(start_date))

def test_forecast_logic():
    start_date = datetime(2023, 1, 1)
    last_price = 100.0
    last_std = 1.0
    days = 5

    dates, means, uppers, lowers = generate_forecast(start_date, last_price, last_std, days)

    # Check growth (drift is positive)
    for i in range(1, days):
        assert means[i] > means[i-1]

    # Check bands
    for i in range(days):
        assert uppers[i] > means[i]
        assert lowers[i] < means[i]

        # Check width expansion logic
        width = uppers[i] - means[i]
        # Allow slight floating point inaccuracy
        assert width > 0

        if i > 0:
            prev_width = uppers[i-1] - means[i-1]
            assert width > prev_width

def test_forecast_dates():
    start_date = datetime(2023, 1, 1)
    last_price = 100.0
    last_std = 1.0
    days = 5

    dates, _, _, _ = generate_forecast(start_date, last_price, last_std, days)

    for i in range(days):
        expected_date = start_date + timedelta(days=i+1)
        assert dates[i] == expected_date

def test_forecast_edge_cases():
    start_date = datetime(2023, 1, 1)
    last_price = 100.0
    last_std = 1.0

    # Test days=1
    dates, means, uppers, lowers = generate_forecast(start_date, last_price, last_std, days=1)
    assert len(dates) == 1
    assert len(means) == 1
    assert len(uppers) == 1
    assert len(lowers) == 1

    # Test days=0
    dates, means, uppers, lowers = generate_forecast(start_date, last_price, last_std, days=0)
    assert len(dates) == 0
    assert len(means) == 0
    assert len(uppers) == 0
    assert len(lowers) == 0
