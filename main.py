# SolarParser main application file
import sys
import os
from influxdb_client_3 import InfluxDBClient3, Point
import pandas as pd
from api import DessAPI
import tempfile

DATA_MAP = {
    "BatSoc(%)": "battery_level",
    "BatVolt(V)": "battery_voltage",
    "ChargeCurr(A)": "battery_current",
    "Mains voltage(V)": "grid_voltage",
    "Grid current(A)": "grid_current",
    "PV voltage(V)": "solar_voltage",
    "PV charging current(A)": "solar_current",
    "PV charging power(W)": "solar_power",
    "Load active(W)": "load_active",
    "PV power generation on the day(kWh)": "solar_acumulated_energy",
    "Load power consumption on the day(kWh)": "load_acumulated_energy",
    "Power consumption from the mains on the day of the load(kWh)": "grid_acumulated_energy"
}


class SolarReport:
    def __init__(self, file_name):
        self._file_name = file_name
        self._influxClient = None

    @property
    def file_name(self):
        return self._file_name

    # Read given file(s) and return a list entries
    # @param file_name: Name of the file to read
    # @return data: pandas.core.frame.DataFrame
    def read_xlsx_file(self):
        df = pd.read_excel(self.file_name)
        df.sort_values(by='Timestamp', inplace=True)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])

        return df

    # Parse data from xlsx accroding map with correct types
    # @return parsed_data: List of parsed entries
    def parsed_data(self):
        df = self.read_xlsx_file()
        df = df[["Timestamp"] + list(DATA_MAP.keys())]
        df = df.rename(columns=DATA_MAP)
        pd.to_numeric(df['load_active'], downcast="float")
        # data = self.calculate_energy(df)

        return df.to_dict(orient='records')

    # @return parsed_data: List of parsed entries with extra energy columns
    # def calculate_energy(self, df):
    #     df['time_diff'] = df['Timestamp'].diff().dt.total_seconds() / 3600  # Convert to hours
    #
    #     # Calculate the difference of the first timestamp from its midnight
    #     first_diff = (df.iloc[0]['Timestamp'] - df.iloc[0]['Timestamp'].replace(hour=0, minute=0,
    #                                                                             second=0)).total_seconds() / 3600
    #     # Set the first entry's time_diff to first_diff
    #     df.iloc[0, df.columns.get_loc('time_diff')] = first_diff
    #     df['load_energy'] = (df['load_active'] * df['time_diff']).round(2)
    #     df['solar_energy'] = (df['solar_power'] * df['time_diff']).round(2)
    #     df['grid_energy'] = (df['grid_current'] * df['grid_voltage'] * df['time_diff']).round(2)
    #     df.drop(columns=['time_diff'], inplace=True)
    #
    #     return df.to_dict(orient='records')

    def write_data(self, data):
        points = []
        for row in data:
            point = Point("ea_sun")
            point.time(row["Timestamp"].to_pydatetime())
            del row["Timestamp"]

            for name, value in row.items():
                point.field(name, value)
            points.append(point)

        self.influx_client.write(database=os.environ["INFLUXDB_BUCKET"], record=points)

    @property
    def influx_client(self):
        if self._influxClient is None:
            token = os.environ["INFLUXDB_TOKEN"]
            org = os.environ["INFLUXDB_ORG"]
            host = os.environ["INFLUXDB_HOST"]
            self._influxClient = InfluxDBClient3(host=host, token=token, org=org)

        return self._influxClient


print(f"SolarParser v{open(os.path.join(os.path.dirname(__file__), 'VERSION'), 'r').readline()}")


def main():
    if len(sys.argv) == 1:
        raise ValueError("No dates for download provided as arguments.")

    dates = sys.argv[1:]

    for date in dates:
        api = DessAPI("exportDeviceDataDetail")
        params = {
            'source': '1',
            'page': '0',
            'pagesize': '15',
            'i18n': 'en_US',
            'pn': os.environ['DESS_PN'],
            'devcode': os.environ['DESS_DEVCODE'],
            'devaddr': os.environ['DESS_DEVADDR'],
            'sn': os.environ['DESS_SN'],
            'date': date,
        }
        response = api.get(**params)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Write the response content to the temporary file
            temp_file.write(response.content)
            # Get the name of the file
            app = SolarReport(temp_file.name)
            data = app.parsed_data()
            app.write_data(data)
        

if __name__ == "__main__":
    main()
