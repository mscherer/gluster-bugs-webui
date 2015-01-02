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
# nova_bugs.py pulls out all the bugs from the nova project in
# launchpad and writes them to a file in JSON format.  This is based on
# infra_bugday.py from the CI team

import argparse
import datetime
import json
import os
import re
import sys

from launchpadlib.launchpad import Launchpad
import requests

LPCACHEDIR = os.path.expanduser(os.environ.get('LPCACHEDIR',
                                               '~/.launchpadlib/cache'))
LPPROJECT = os.environ.get('LPPROJECT',
                           'nova')
LPSTATUS = ('New', 'Confirmed', 'Triaged', 'In Progress')
LPIMPORTANCE = ('Critical', 'High', 'Medium', 'Undecided', 'Low', 'Wishlist')

BZSTATUS = ('NEW', 'ASSIGNED', 'POST', 'MODIFIED', 'ON_QA')
BZPRIORITY = ('urgent', 'high', 'medium', 'unspecified', 'low')

GERRIT_URL = "https://review.openstack.org"

RE_LINK = re.compile(' %s/(\d+)' % GERRIT_URL)


def get_reviews_from_bug(bug):
    """Return a list of gerrit reviews extracted from the bug's comments."""
    reviews = set()
    for comment in bug.comments:
        reviews |= set(RE_LINK.findall(comment.content))
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


def main():
    parser = argparse.ArgumentParser(description='pull all bugs from a '
                                                 'launchpad project')

    args = parser.parse_args()

    launchpad = Launchpad.login_anonymously('OpenStack Infra Bugday',
                                            'production',
                                            LPCACHEDIR)
    project = launchpad.projects[LPPROJECT]
    counter = 0

    nova_status = "Unknown"

    f = open('bugs-refresh.json', 'w')
    f.write('{"date": "%s", "bugs": [' % datetime.datetime.now())

#    for task in project.searchTasks(status=LPSTATUS, importance=LPIMPORTANCE,
#                                    omit_duplicates=True,
#                                    order_by='-importance'):
    bzq = bz.build_query(product=LPPROJECT, status=LPSTATUS)
    for task in bz.query(bzq):
        #if counter == 300:
        #    break
#        bug = launchpad.load(task.bug_link)
#
#        nova_status = 'Unknown'
#        nova_owner = 'Unknown'
#
#        for task in bug.bug_tasks:
#            if task.bug_target_name == LPPROJECT:
#                nova_status = task.status
#                nova_owner = task.assignee
#                break
        try:
            if counter != 0:
                bug_data = ','
            else:
                bug_data = ""
            title = task.summary.replace('"', "'")
            title = title.replace("\n", "")
            title = title.replace("\t", "")
            bug_data += ('{"index": %d, "id": %d, "importance": "%s", '
                         '"status": "%s", '
                         '"owner": "%s", '
                         '"title": "%s", '
                         '"link": "%s"' % (
                             counter,
                             task.id,
                             task.priority,
                             task.status,
                             task.assignee,
                             title,
                             task.weburl))

        except (TypeError, UnicodeEncodeError):
            # TODO: fix this
            print 'Error on bug %d', task.id
            counter += 1
            continue

        creation_time = datetime.datetime.strptime(task.creation_time, "%Y%m%dT%H:%M:%S")
        last_updated = datetime.datetime.strptime(task.last_change_time, "%Y%m%dT%H:%M:%S")
        age = delta(task.creation_time)
        updated = delta(bug.date_last_updated)
        stale = False
        if updated > 30 and age > 30:
            if nova_status == 'ASSIGNED':
                stale = True
        bug_data += (',"age": %d, "update": %d, "stale": %d, '
                     '"never_touched": %d' %
                     (age, updated, 1 if stale else 0, 1 if (age ==
                                                             updated) else 0))

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
        except ValueError, e:
            print e, bug_data
        counter += 1

    f.write(']}')
    f.close()


if __name__ == "__main__":
    main()
