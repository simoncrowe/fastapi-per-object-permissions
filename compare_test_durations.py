import os
from collections import defaultdict

import junitparser


def main():
    dirpath, _, filenames = next(os.walk("./test_output"))
    results_by_backend = {}
    for filename in filenames:
        backend_name, _ = os.path.splitext(filename)
        results = junitparser.JUnitXml.fromfile(os.path.join(dirpath, filename))
        test_suite = next(iter(results))
        results_by_backend[backend_name] = test_suite

    results_by_test = defaultdict(list)
    for backend_name, results in results_by_backend.items():
        for result in results:
            results_by_test[f'{result.classname}::{result.name}'].append((result.time, backend_name))

    print('FASTEST DURATIONS FOR EACH TEST')
    for test_name, results in sorted(results_by_test.items()):
        print(f'\n{test_name}')
        for time, backend in sorted(results):
            print(f'  {backend}: {time:0.3f}')

    durations = sorted((sum(test.time for test in tests), name)
                       for name, tests in results_by_backend.items())
    print('\n\nBACKEND_NAME         TOTAL_DURATION')
    for duration, backend_name in durations:
        print(f'{backend_name: <20} {duration:0.3f}')


if __name__ == '__main__':
    main()
