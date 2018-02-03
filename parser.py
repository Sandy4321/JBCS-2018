try:
    from datetime import datetime
    import collections
    import json
    import csv
    import os
except ImportError as error:
    raise ImportError(error)

def monthly_pull_requests(pull_requests):

    frequency = collections.OrderedDict()
    for pull_request in pull_requests:
        date = datetime.strptime(
            pull_request['created_at'],
            '%Y-%m-%dT%H:%M:%SZ').date().replace(day=15)
        if date not in frequency:
            frequency[date] = 1
        else:
            frequency[date] = frequency[date] + 1
    return frequency

# Outputs the monthly distribution of pull requests in a project. (Source: pull_requests.json)
# If you don't have a pull_requests.json file for your project, use collector.py!
def pull_requests(data, folder):
    employees_opened = []
    employees_closed = []
    employees_merged = []
    volunteers_opened = []
    volunteers_closed = []
    volunteers_merged = []

    for pull_request in data:
        if pull_request['state'] == 'open':
            if pull_request['user']['site_admin'] == True:
                employees_opened.append(pull_request)
            else:
                volunteers_opened.append(pull_request)
        if pull_request['state'] == 'closed':
            if pull_request['merged_at'] == None:
                if pull_request['user']['site_admin'] == True:
                    employees_closed.append(pull_request)
                else:
                    volunteers_closed.append(pull_request)
            else:
                if pull_request['user']['site_admin'] == True:
                    employees_merged.append(pull_request)
                else:
                    volunteers_merged.append(pull_request)

    employees_opened = monthly_pull_requests(employees_opened)
    employees_closed = monthly_pull_requests(employees_closed)
    employees_merged = monthly_pull_requests(employees_merged)
    volunteers_opened = monthly_pull_requests(volunteers_opened)
    volunteers_closed = monthly_pull_requests(volunteers_closed)
    volunteers_merged = monthly_pull_requests(volunteers_merged)

    with open(folder, 'w') as output:
        fieldnames = ['month', 'pull_type', 'pull_amount', 'user_type']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for date in employees_opened:
            writer.writerow({'month': date, 'pull_type': 'opened', 'pull_amount': employees_opened[date], 'user_type':'Employees'})
        for date in employees_closed:
            writer.writerow({'month': date, 'pull_type': 'closed', 'pull_amount': employees_closed[date], 'user_type':'Employees'})
        for date in employees_merged:
            writer.writerow({'month': date, 'pull_type': 'merged', 'pull_amount': employees_merged[date], 'user_type':'Employees'})
        for date in volunteers_opened:
            writer.writerow({'month': date, 'pull_type': 'opened', 'pull_amount': volunteers_opened[date], 'user_type':'Volunteers'})
        for date in volunteers_closed:  
            writer.writerow({'month': date, 'pull_type': 'closed', 'pull_amount': volunteers_closed[date], 'user_type':'Volunteers'})
        for date in volunteers_merged:
            writer.writerow({'month': date, 'pull_type': 'merged', 'pull_amount': volunteers_merged[date], 'user_type':'Volunteers'})

def outsiders_contributions(data, folder):
    outsiders = {}

    for pull_request in data:
        if pull_request['state'] == 'closed' and pull_request['merged_at'] != None:
            if pull_request['user']['site_admin'] != True:
                username = pull_request['user']['login']

                if username in outsiders:
                    outsiders[username] = outsiders[username] + 1
                else:
                    outsiders[username] = 1

    with open(folder, 'w') as output:
        fieldnames = ['username', 'url', 'count']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for outsider in sorted(outsiders, key=outsiders.get, reverse=True):
            url = 'https://github.com/' + outsider
            writer.writerow({'username': outsider, 'url': url, 'count': outsiders[outsider]})



if __name__ == '__main__':
    dataset_folder = 'Dataset/'
    projects = [{'organization':'electron','name':'electron'},
    {'organization':'github','name':'linguist'},
    {'organization':'git-lfs','name':'git-lfs'},
    {'organization':'hubotio','name':'hubot'},
    {'organization':'atom','name':'atom'}]

    for project in projects:
        folder = dataset_folder + project['name']

        with open(folder + '/pull_requests.json', 'r') as data_file:
            data = json.load(data_file)
            # pull_requests(data, folder + '/pull_requests_per_month.csv')
            outsiders_contributions(data, project['name'] + '_outsiders.csv')