
import json
from calc import STORAGE_TYPE
from argparse import ArgumentParser
from clickhouse_calc import ClickHouseCalc


def parse_args() -> ArgumentParser:
    """Parses the parameters when main.py is called

    Returns
    -------
    ArgumentParser
        An object containing all the parameter values or their defaults
    """
    description = ('Get FSIEM deployment requirements for a number of seats')
    parser = ArgumentParser(description=description)
    parser.add_argument('-s', '--seats', type=int, required=True, help=(
        'The number of licensed seats, e.g. 5. Valid range is [5 .. 1000].'))
    parser.add_argument('-t', '--storage-type', required=True,  help=(
        'Storage type: clickhouse or eventdb'), type=str.lower)
    parser.add_argument('-o', '--online-storage-size-gb', help=(
        'Total online storage in GB that user purchased, defaults to 500'),
        default=500, type=int, required=False)
    parser.add_argument('-m', '--max-disk-size-gb', help=(
        'Maximum disk size in GB we store on a disk, defaults to 10000'),
        default=10000, type=int, required=False)
    return parser.parse_args()


def get_json_output(n: int, type: STORAGE_TYPE,
                    online_size: int, max_per_disk: int) -> str:
    calc = ClickHouseCalc(n, online_size, max_per_disk)
    res = calc.get()
    return json.dumps(res, default=vars)


if __name__ == '__main__':
    # Usage examples:
    #     python3 main.py --storage-type clickhouse --seats 5
    #     python3 main.py --storage-type eventdb --seats 5
    #     python3 main.py -t clickhouse -s 5 -o 500 -m 10000
    config = parse_args()
    n = config.seats
    online_size = config.online_storage_size_gb
    max_per_disk = config.max_disk_size_gb
    type = STORAGE_TYPE(config.storage_type)
    print(get_json_output(n, type, online_size, max_per_disk))
