# SolarParser main application file
import argparse
import sys
import os
from api import DessAPI
import tempfile, shutil
from solar_report import SolarReport
from datetime import datetime, timedelta

print(f"SolarParser v{open(os.path.join(os.path.dirname(__file__), 'VERSION'), 'r').readline()}")

# Just download data and store them in given +path+
def download(dates, path="./"):
    for date in dates:
        data = __download_file(date)
        destination_path = f'{path}/{data["name"]}'

        with open(data["file"].name, 'rb') as src_file:
            shutil.copyfileobj(src_file, open(destination_path, 'wb'))

# Report will send data into influxDB
def report(dates):
    for date in dates:
        data = __download_file(date)
        app = SolarReport(data["file"].name)
        data = app.parsed_data()
        app.write_data(data)

def main():
    parser = argparse.ArgumentParser(description="SolarReport from DESS to influxDB")
    subparsers = parser.add_subparsers(dest='command')

    # Download command
    download_parser = subparsers.add_parser('download', help='Download report for a date')
    def daterange(start_date, end_date):
        for n in range(int((end_date - start_date).days) + 1):
            yield start_date + timedelta(n)

    def date_range_type(args):
        if ".." in args[0]:
            try:
                start_date, end_date = args[0].split('..')
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                dates = [str(date) for date in daterange(start_date, end_date)]
                return dates
            except ValueError:
                raise argparse.ArgumentTypeError("Invalid date range format. Please use YYYY-MM-DD..YYYY-MM-DD.")
        else:
            return args

    download_parser.add_argument('dates', type=str, nargs='+', help='Date range for download (YYYY-MM-DD or YYYY-MM-DD..YYYY-MM-DD)')
    download_parser.add_argument('--path', type=str, required=False, default="./", help='Path to save the file')

    # Report command
    upload_parser = subparsers.add_parser('report', help='Upload a report to influxDB')
    upload_parser.add_argument('dates', nargs='+', type=str, help='Date(s) for reporting')

    args = parser.parse_args()
    dates_list = date_range_type(args.dates)
    if args.command == 'download':
        download(dates_list, path=args.path)
    elif args.command == 'report':
        report(dates_list)
    else:
        parser.print_help()

# Download single XLSX report based on given date
def __download_file(date):
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
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(response.content)
    file_name = response.headers['Content-disposition'].split('=')[1]
    temp_file.flush()
    temp_file.close()
    
    return { "file": temp_file, "name": file_name }

if __name__ == "__main__":
    main()
