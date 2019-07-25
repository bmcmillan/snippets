import pandas
import json
import requests
import time
import re

username = 'bentest-api@qg.com'
password = ''
#companykey = '2fbe9730-5a7f-4c97-8cd3-e25336c9cf9b' #bentest
companykey = 'e5c23ef0-c05a-4230-837f-8f4a5515dff7' #envision

baseurl = 'https://api-test.qgenda.com/v2/'
#baseurl = 'https://api.qgenda.com/v2/'
jwt = ''

resp = requests.post(baseurl + 'login', json={
    'email': username,
    'password': password
})
jwt = resp.json()['access_token']
if (jwt == ''):
    print("Error logging in")
    exit

authheaders = {"Authorization": "Bearer " + jwt}
rawtasks = requests.get(baseurl + 'task', params={'companyKey': companykey}, headers=authheaders)
if rawtasks.status_code != 200:
    print("Error getting tasks:" + rawtasks.text)
    print(rawtasks.url)
    exit

tasks = {}
for task in rawtasks.json():    
    tasks[task['Name']] = task['TaskKey']
print(tasks.keys())

df = pandas.read_csv('daily.csv', dtype='unicode')
size = df.size
cases_created = 0
for index,row in df.iterrows():
    start = time.time()
    if row['Location'] not in tasks:
        print('Task ' + str(row['Location']) + " was not found")        
    else:
        case = {
            'CompanyKey': companykey,
            'TaskKey': tasks[row['Location']], #tasks['Midtown OR1'] for testing
            'EmrId': row['EMR ID'],
            'LocationName': row['Location'],
            'Date': row['Procedure Date'], # TODO: format
            'StartTime': row['Start Time'], # TODO: format
            'EndTime': row['End Time'], # TODO: format
            'Surgeon': row['Surgeon'],
            'Procedure': row['Procedure'],
            'IsCancelled': row['Cancelled'] == 'Y',
            'DPStaffID[0]': row['Abbreviation'],
            'CustomTextFields[0][0]': 'TextField1',
            'CustomTextFields[0][1]': row['Procedure'],
            'CustomTextFields[9][0]': 'TextField10',
            'CustomTextFields[9][1]': row['Private Notes (No PHI)'],
            'CustomTextFields[2][0]': 'TextField3',
            'CustomTextFields[2][1]': row['Block'],
            'CustomTextFields[10][0]': 'TextField11',
            'CustomTextFields[10][1]': row['Cancellation Reason'],
            'CustomTextFields[4][0]': 'TextField5',
            'CustomTextFields[4][1]': row['Room #'],
            'CustomTextFields[15][0]': 'TextField16',
            'CustomTextFields[15][1]': row['Insurance'],
            'CustomTextFields[14][0]': 'TextField15',
            'CustomTextFields[14][1]': row['Case Status'],
            'CustomTextFields[8][0]': 'TextField9',
            'CustomTextFields[8][1]': row['Public Notes'],
            'CustomCheckboxFields[0][0]': 'Checkbox1',
            'CustomCheckboxFields[0][1]': row['High Risk / PEDs'],
            'CustomCheckboxFields[1][0]': 'Checkbox2',
            'CustomCheckboxFields[1][1]': row['Cardiac'],
            'CustomCheckboxFields[2][0]': 'Checkbox3',
            'CustomCheckboxFields[2][1]': row['DR/PT Requested'],
            'CustomCheckboxFields[3][0]': 'Checkbox4',
            'CustomCheckboxFields[3][1]': row['Confirmed'],
            'CustomCheckboxFields[4][0]': 'Checkbox5',
            'CustomCheckboxFields[4][1]': row['Notified'],
            'CustomCheckboxFields[5][0]': 'Checkbox6',
            'CustomCheckboxFields[5][1]': row['Finished'],
            'CustomCheckboxFields[6][0]': 'Checkbox7',
            'CustomCheckboxFields[6][1]': row['Read Me/Special'],
            'CustomCheckboxFields[7][0]': 'Checkbox8',
            'CustomCheckboxFields[7][1]': row['GME Case'],
            'CustomCheckboxFields[8][0]': 'Checkbox9',
            'CustomCheckboxFields[8][1]': row['Case Delayed'],
            'PatientFirstName': row['Patient First Name'],
            'PatientLastName': row['Patient Last Name'],
            'PatientAgeYears': row['Patient Age y'],
            'PatientGender': row['Patient Gender'],
            'PatientEmail': row['Patient Email'],
            'PatientHomePhone': row['Patient Home Phone'],
            'PatientCellPhone': row['Patient Cell Phone'],
            'PatientDOB': row['Patient DOB'],
            'PatientMRN': row['Patient MRN'],
        }
        
        resp = requests.post(baseurl + 'dailyCase', json=case, headers=authheaders)
        if resp.status_code == 200:
            print('Created case # ' + str(index) + '/' + str(size) + ': ' + str(resp.json()['DailyCase']['DailyCaseID']))
            cases_created+=1
        else:
            print('Error creating case # ' + str(index) + '/' + str(size) + ': ' + str(row['EMR ID']) + ' ' + str(row['Location']) + ' ' + str(row['Procedure Date']))
    recordsremaining = size - index
    end = time.time()
    print('Elapsed: ' + str(end - start) + ' sec')
    #print('Time remaining: ' + str(int((recordsremaining * (end - start) / 60))) + ' min')
print("Total cases created: " + str(cases_created))