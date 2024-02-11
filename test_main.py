import pytest
from unittest.mock import patch
import main

def test_download(mocker):
    mocker.patch('main.download')

    test_args = ['download', '2023-11-20', '2023-11-21']
    with patch('sys.argv', ['main.py'] + test_args):
        main.main()

    main.download.assert_called_once_with(['2023-11-20', '2023-11-21'], path="./")

def test_download_for_single_date(mocker):
    mocker.patch('main.download')

    test_args = ['download', '2023-11-21']
    with patch('sys.argv', ['main.py'] + test_args):
        main.main()

    main.download.assert_called_once_with(['2023-11-21'], path="./")

def test_download_for_date_range(mocker):
    mocker.patch('main.download')

    test_args = ['download', '2023-11-17..2023-11-21']
    with patch('sys.argv', ['main.py'] + test_args):
        main.main()

    main.download.assert_called_once_with(['2023-11-17', '2023-11-18', '2023-11-19', '2023-11-20', '2023-11-21'], path="./")

def test_report(mocker):
    mocker.patch('main.report')

    test_args = ['report', '2023-11-20', '2023-11-21']
    with patch('sys.argv', ['main.py'] + test_args):
        main.main()

    main.report.assert_called_once_with(['2023-11-20', '2023-11-21'])
