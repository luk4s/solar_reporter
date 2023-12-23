# PyTest
import pytest
from unittest.mock import patch
import solar_report as app
from influxdb_client_3 import InfluxDBClient3, Point


@pytest.fixture
def test_file_path():
    return "fixtures/dess_example_2023-12-11.xlsx"


@pytest.fixture
def test_data_row(test_file_path):
    return app.SolarReport(test_file_path).read_xlsx_file()[0]


def test_parsing(test_file_path):
    instance = app.SolarReport(test_file_path)
    instance.read_xlsx_file()

    assert instance.file_name == test_file_path


class TestParsedData:
    @pytest.fixture
    def subject_data(self, test_file_path):
        return app.SolarReport(test_file_path).parsed_data()

    @pytest.fixture
    def subject_data_row(self, subject_data):
        return subject_data[0]

    # Check parsed data are array of objects
    def test_parsed_data(self, test_file_path):
        instance = app.SolarReport(test_file_path)
        # result = instance.read_xlsx_file()
        parsed_result = instance.parsed_data()
        assert type(parsed_result) == list
        assert type(parsed_result[0]) == dict

    def test_bat_soc_is_int(self, subject_data_row):
        row = subject_data_row

        assert type(row["battery_level"]) == int

    def test_battery_volt_is_float(self, subject_data_row):
        row = subject_data_row

        assert type(row["battery_voltage"]) == float

    # def test_calculate_energy(self, test_file_path):
    #     instance = app.SolarReport(test_file_path)
    #     data = instance.parsed_data()
    #     row = data[0]
    #     assert type(row) == dict
    #     assert row["load_active"] == 56.0
    #     assert row["load_energy"] == 0.92
    #     assert row["solar_energy"] == 0.
    #     assert row.get("time_diff") == None


def test_influxClienttest_file_path():
    with patch.dict('os.environ', {'INFLUXDB_TOKEN': 'token', 'INFLUXDB_ORG': 'my', 'INFLUXDB_HOST': 'https://influx.cloud'}):
        instance = app.SolarReport(test_file_path)
        assert type(instance.influx_client) == InfluxDBClient3
