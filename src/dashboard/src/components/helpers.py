# This file is part of Archivematica.
#
# Copyright 2010-2012 Artefactual Systems Inc. <http://artefactual.com>
#
# Archivematica is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Archivematica is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Archivematica.  If not, see <http://www.gnu.org/licenses/>.

from django.utils.dateformat import format
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from main import models
import sys

# Used for raw SQL queries to return data in dictionaries instead of lists
def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def pager(objects, items_per_page, current_page_number):
    page = {}

    p                    = Paginator(objects, items_per_page)

    page['current']      = 1 if current_page_number == None else int(current_page_number)
    pager                = p.page(page['current'])
    page['has_next']     = pager.has_next()
    page['next']         = page['current'] + 1
    page['has_previous'] = pager.has_previous()
    page['previous']     = page['current'] - 1
    page['has_other']    = pager.has_other_pages()

    page['objects']      = pager.object_list

    return page

def task_duration_in_seconds(task):
    duration = int(format(task.endtime, 'U')) - int(format(task.starttime, 'U'))
    if duration == 0:
        duration = '< 1'
    return duration

def get_jobs_by_sipuuid(uuid):
    jobs = models.Job.objects.filter(sipuuid=uuid).order_by('-createdtime', 'subjobof')
    priorities = {
        'completedUnsuccessfully': 0,
        'requiresAprroval': 1,
        'requiresApproval': 1,
        'exeCommand': 2,
        'verificationCommand': 3,
        'completedSuccessfully': 4,
        'cleanupSuccessfulCommand': 5,
    }
    def get_priority(job):
        try: return priorities[job.currentstep]
        except Exception: return 0
    return sorted(jobs, key = get_priority) # key = lambda job: priorities[job.currentstep]
