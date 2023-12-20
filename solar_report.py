import os
from influxdb_client_3 import InfluxDBClient3, Point
import pandas as pd

DATA_MAP = {
    "Battery level SOC(%)": "battery_level",
    "Battery voltage(V)": "battery_voltage",
    "Battery current(A)": "battery_current",
    "Mains voltage(V)": "grid_voltage",
    "Grid current(A)": "grid_current",
    "PV voltage(V)": "solar_voltage",
    "PV charging current(A)": "solar_current",
    "PV charging power(W)": "solar_power",
    "Load active power(W)": "load_active",
    "PV daily power generation(kWh)": "solar_acumulated_energy",
    "Electricity consumption on the day of load(kWh)": "load_acumulated_energy",
    "Consumption of municipal electricity on the day of load(kWh)": "grid_acumulated_energy"
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

