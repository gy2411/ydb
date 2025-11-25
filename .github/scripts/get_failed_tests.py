#! /usr/bin/python3 -u

from __future__ import annotations
import argparse
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'tests'))
import mute_utils


def get_failed_test_names(muted_path: str, report_path: str) -> set[str]:
    print('Load failed tests..')
    result = set()
    mute_check = mute_utils.MuteTestCheck(muted_path) if muted_path else None
    with open(report_path) as report_file:
        report = json.load(report_file).get('results', [])
    for record in report:
        if record.get('status', 'OK') == 'OK' or record.get('suite', False):
            continue
        test_name = record.get("name", "")
        subtest_name = record.get("subtest_name", "")
        test_path = record.get("path", "")
        if mute_check is not None and mute_check(f'{test_path} {test_name}.{subtest_name}'):
            continue
        result.add(f'{test_name}::{subtest_name}')
    print(f'{len(result)} tests loaded')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', '-o', type=str, dest='out', required=True, help='Path to result tests filter')
    parser.add_argument('--report', '-r', type=str, dest='report', required=True, help='Path to json build report')
    parser.add_argument('--muted', '-m', type=str, help='Path to muted tests', dest='muted')
    opts = parser.parse_args()
    failed_tests = get_failed_test_names(muted_path=opts.muted, report_path=opts.report)
    with open(opts.out, 'w') as result_file:
        result_file.write(' '.join([f'-F {t}' for t in failed_tests]))
