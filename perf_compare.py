#!/usr/bin/env python
import argparse
import datetime
import json
import logging
import logging.handlers
import os
import requests
from six.moves.urllib.parse import urljoin


LOG_FILE = "comparator.log"
DATA = {
    'oooq': 'ara.json',
    'undercloud': 'ara.oooq.root.json',
    'overcloud': 'ara.oooq.oc.json'
}

log = logging.getLogger('comparator')
log.setLevel(logging.DEBUG)
log_handler = logging.handlers.WatchedFileHandler(
    os.path.expanduser(LOG_FILE))
log_formatter = logging.Formatter('%(asctime)s %(process)d '
                                  '%(levelname)-8s %(name)s %(message)s')
log_handler.setFormatter(log_formatter)
log.addHandler(log_handler)


def normalize(data):

    def time_delta(ts):
        t = datetime.datetime.strptime(ts, "%H:%M:%S")
        return int(datetime.timedelta(hours=t.hour, minutes=t.minute,
                                  seconds=t.second).total_seconds())

    norm = [{'name': i['Name'], 'time': time_delta(i['Duration'])}
            for i in data]
    dictized = {}
    for i in norm:
        if i['name'] in dictized:
            dictized[i['name']] += i['time']
        else:
            dictized[i['name']] = i['time']
    total_norm = []
    for i in norm:
        if i['name'] in dictized:
            total_norm.append(
                {'name': i['name'], 'time': dictized.pop(i['name'])}
                )
    norm_names = [i['name'] for i in total_norm]
    import time
    with open("/tmp/devb_%s" % time.time(), "w") as f:
        f.write(str(total_norm))
    time.sleep(1)
    return norm_names, total_norm


def combine(data1, data2):
    data = []
    norm1_names, norm1 = normalize(data1)
    norm2_names, norm2 = normalize(data2)
    for task in norm1:
        if task['name'] in norm2_names:
            task2 = [i for i in norm2 if i['name'] == task['name']][0]
            data += [[task['name'], task['time'], task2['time']]]
            norm2.remove(task2)
        else:
            data += [[task['name'], task['time'], 0]]
    for task in norm2:
        data += [[task['name'], 0, task['time']]]
    return data


def filter_data(data):
    f1 = (i for i in data if not (i[1] == 0 and i[2] == 0))
    f2 = (i for i in f1 if abs(i[1] - i[2]) > 10)
    return list(f2)


def get_file(link, filepath):
    url = urljoin(link, "logs/" + filepath)
    www = requests.get(url)
    if not www or www.status_code not in (200, 404):
        log.debug("Web request for %s failed with status code %s",
                  url, www.status_code)
        return None
    elif www.status_code == 404:
        log.debug("Web request for %s got 404", url)
        return "not found"
    try:
        jsoned = www.json()
        return jsoned
    except Exception:
        log.error("Couldn't parse JSON from %s", url)
        return None


def extract_dummy(link1, link2, filepath):
    with open("/home/sshnaidm/tmp/percomp/good/" + filepath) as f:
        try:
            good = json.load(f)
        except:
            return None
        if not good: return None
    with open("/home/sshnaidm/tmp/percomp/bad/" + filepath) as f:
        try:
            bad = json.load(f)
        except:
            return None
        if not bad: return None
    return good, bad


def extract(link1, link2, filepath):
    data1 = get_file(link1, filepath)
    if data1 == "not found":
        return None
    data2 = get_file(link2, filepath)
    if data1 == "not found":
        return None
    if data1 and data2:
        return data1, data2
    return None


def compare(good, bad):
    ready = {}
    for part, filepath in DATA.items():
        extracted_data = extract(good, bad, filepath)
        if extracted_data is None:
            ready[part] = None
            continue
        combined_data = combine(*extracted_data)
        filtered_data = filter_data(combined_data)
        ready[part] = filtered_data
    return ready


def main():
    parser = argparse.ArgumentParser(__doc__)

    parser.add_argument('-g', '--good-job', dest="good",
                        default="https://logs.rdoproject.org/96/15896/35/check/legacy-tripleo-ci-centos-7-ovb-3ctlr_1comp-featureset001-master/3cf4a97/",
                        help='Link to good job')
    parser.add_argument('-b', '--bad-job', dest="bad",
                        default = "https://logs.rdoproject.org/96/15896/35/check/legacy-tripleo-ci-centos-7-ovb-3ctlr_1comp-featureset001-master-vexxhost/2b2cbf3/",
                        help='Link to bad job')
    args = parser.parse_args()
    data = compare(args.good, args.bad)
    with open("/tmp/compare_data", "w") as f:
        for k in data:
            f.write("\n" + k + ":\n\n")
            print(data[k])
            if data[k]:
                for z in data[k]:
                    f.write(" | ".join([str(l) for l in z]) + "\n")


if __name__ == '__main__':
    main()
