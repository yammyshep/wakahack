import json
import argparse
from collections import defaultdict
import re
import datetime

def matchProject(project):
    if args.search != None:
        if args.s.lower() in project['name'].lower():
            projects.append({'name': project['name'], 'time': project['grand_total']['total_seconds']})
            return True
        else:
            return False

    if args.project != None:
        return args.p == project['name']

    if args.regex != None:
        if re.match(args.r, project['name']):
            projects.append({'name': project['name'], 'time': project['grand_total']['total_seconds']})
            return True
        else:
            return False


    if args.all != None:
        projects.append({'name': project['name'], 'time': project['grand_total']['total_seconds']})
        return True

def matchDate(day):
    project_date = datetime.datetime.strptime(day['date'], '%Y-%m-%d')
    if args.before != None:
        before_date = datetime.datetime.strptime(args.before, '%Y-%m-%d')
        if before_date < project_date:
            return False

    if args.after != None:
        after_date = datetime.datetime.strptime(args.after, '%Y-%m-%d')
        if after_date > project_date:
            return False

    return True

intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
    )

def display_time(seconds, granularity=2):
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])

def foundry(seconds):
    hours, minutes= divmod(int(seconds/60), 60)
    return str(hours) + "h " + str(minutes) + "m"

parser = argparse.ArgumentParser(description='Count hours in a wakatime data dump')
parser.add_argument('-f', '--file', metavar='file', type=open, required=True)
search = parser.add_mutually_exclusive_group(required=True)
search.add_argument('-a', '--all', action='store_true')
search.add_argument('-s', '--search', metavar='<term>')
search.add_argument('-p', '--project', metavar='<name>')
search.add_argument('-r', '--regex', metavar='<regex>')
parser.add_argument('-bd', '--before', metavar='YYYY-MM-DD')
parser.add_argument('-ad', '--after', metavar='YYYY-MM-DD')

args = parser.parse_args()

inputdata = json.load(args.file)

totaltime = 0.0
projects = []

for day in inputdata['days']:
    if matchDate(day):
        for project in day['projects']:
            if matchProject(project):
                totaltime = totaltime + project['grand_total']['total_seconds']

c = defaultdict(int)
for d in projects:
    c[d['name']] += d['time']

projects = [{'name': name, 'time': time} for name, time in c.items()]

print("Counted time: " + str(display_time(int(totaltime), 10)))
print("PF compatable: " + str(foundry(int(totaltime))))
if len(projects) > 1:
    print()
    print("Counted time from matching projects:")
    for p in projects:
        print("    " + p['name'] + ": " + str(display_time(int(p['time']), 10)))
exit()
