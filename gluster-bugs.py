#! /usr/bin/env python
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# gluster-bugs.py pulls out all the bugs from the glusterfs project in
# bugzilla and writes them to a file in JSON format.

import argparse
import datetime
import json
import os
import re
import sys

from bugzilla import Bugzilla
import requests

LPPROJECT = os.environ.get('LPPROJECT', 'GlusterFS')
LPSTATUS = ('New', 'Confirmed', 'Triaged', 'In Progress')
LPIMPORTANCE = ('Critical', 'High', 'Medium', 'Undecided', 'Low', 'Wishlist')

BZURL = "https://bugzilla.redhat.com/xmlrpc.cgi"
BZSTATUS = ('NEW', 'ASSIGNED', 'POST', 'MODIFIED', 'ON_QA')
BZPRIORITY = ('urgent', 'high', 'medium', 'unspecified', 'low')

GERRIT_URL = "http://review.gluster.org"

RE_LINK = re.compile(' %s/(\d+)' % GERRIT_URL)


def get_reviews_from_bug(bug):
    """Return a list of gerrit reviews extracted from the bug's comments."""
    reviews = set()
    for comment in bug.comments[1:]:
        reviews |= set(RE_LINK.findall(comment['text']))
    return reviews


def get_review_status(review_number):
    """Return status of a given review number."""
    r = requests.get("%s/changes/%s"
                     % (GERRIT_URL, review_number))
    # strip off first few chars because 'the JSON response body starts with a
    # magic prefix line that must be stripped before feeding the rest of the
    # response body to a JSON parser'
    # https://review.openstack.org/Documentation/rest-api.html
    status = None
    try:
        status = json.loads(r.text[4:])['status']
    except ValueError:
        status = r.text
    return status


def delta(date_value):
    delta = datetime.date.today() - date_value.date()
    return delta.days


def getBugPriority(bug):
    prio = bug.priority
    if 'FutureFeature' in bug.keywords:
        prio = 'Wishlist'

    return prio


def getBugStatus(bug):
    status = bug.status
    if status == 'NEW' and 'Triaged' in bug.keywords:
        status = 'Triaged'

    return status


def main():
    parser = argparse.ArgumentParser(description='pull all bugs from a '
                                                 'bugzilla project')

    args = parser.parse_args()

    bz = Bugzilla(url=BZURL)

    counter = 0

    f = open('bugs-refresh.json', 'w')
    f.write('{"date": "%s", "bugs": [' % datetime.datetime.now())

    bzq = bz.build_query(product=LPPROJECT, status=BZSTATUS)
    bugs = bz.query(bzq)
    for task in bugs:
        try:
            if counter != 0:
                bug_data = ','
            else:
                bug_data = u""
            title = task.summary.replace('"', "'")
            title = title.replace("\n", "")
            title = title.replace("\t", "")
            bug_data += ('{"index": %d, "id": %d, "importance": "%s", '
                         '"status": "%s", '
                         '"owner": "%s", '
                         '"title": "%s", '
                         '"link": "%s", '
                         '"component": "%s"' % (
                             counter,
                             task.id,
                             getBugPriority(task),
                             getBugStatus(task),
                             task.assigned_to,
                             title.encode('ascii', 'ignore'),
                             task.weburl,
                             task.component))

        except (TypeError, UnicodeEncodeError):
            # TODO: fix this
            print 'Error on bug %d', task.id
            counter += 1
            continue

        age = delta(datetime.datetime.strptime("%s" % task.creation_time, "%Y%m%dT%H:%M:%S"))
        updated = delta(datetime.datetime.strptime("%s" % task.last_change_time, "%Y%m%dT%H:%M:%S"))
        stale = False
        if updated > 30 and age > 30:
            if task.status == 'ASSIGNED':
                stale = True
        bug_data += (',"age": %d, "update": %d, "stale": %d, '
                     '"never_touched": %d' %
                     (age, updated, 1 if stale else 0, 1 if len(task.comments) == 1 else 0))

        i = 0
        bug_data += ( ',"projects": [')
        bug_data += '{"target": "%s", "status": "%s"}' % (task.target_release, task.status)
        bug_data += ('] ,"reviews": [')

        i = 0
        for review in get_reviews_from_bug(task):
            review_status = get_review_status(review)
            if i != 0:
                bug_data += (",")
            i += 1
            review_status = review_status.replace("\n", "")
            bug_data += ('{"review": '
                         '"%s/%s",'
                         '"status": "%s"}'
                         % (GERRIT_URL, review, review_status))
        bug_data += (']}')

        try:
            if counter == 0:
                json.loads(bug_data)
            else:
                json.loads(bug_data[1:])
            f.write(bug_data)
        except (ValueError, UnicodeEncodeError), e:
            print e, '[Bug: %s]' % task.id

        counter += 1

    f.write(']}')
    f.close()


if __name__ == "__main__":
    main()
