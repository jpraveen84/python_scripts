import boto3
import pygsheets
import string
from datetime import date, timedelta

today = date.today()-timedelta(days=1)

dat = today.strftime("%d-%m-%Y")

a_key = 'xxxxxxx'
s_key = 'xxxxxxx'

client = boto3.client('ce',aws_access_key_id=a_key,aws_secret_access_key=s_key)

response = client.get_cost_and_usage(
    TimePeriod={'Start': '2020-01-01','End': '2020-02-01'},
    Filter={'Dimensions': {'Key': 'LINKED_ACCOUNT','Values': ['xxxxxxxx']}},
    Granularity='MONTHLY',
    GroupBy=[{'Type': 'DIMENSION','Key':'SERVICE'}],
    Metrics=['AmortizedCost'])

service_name = []
final_amount = []
#print (len(response['ResultsByTime'][0]['Groups']))
for i in range(0,(len(response['ResultsByTime'][0]['Groups']))):
    service = response['ResultsByTime'][0]['Groups'][i]['Keys'][0]
    amount = response['ResultsByTime'][0]['Groups'][i]['Metrics']['AmortizedCost']['Amount']
    service_name.append(service)
    final_amount.append(amount)

dictionary = dict(zip(service_name,final_amount))

values = list(dictionary.values())

#print(dictionary)
#exit()

credentials = pygsheets.authorize(service_file='/root/NewRelic-6d54dec5d48c.json')
sheet = credentials.open_by_url('https://docs.google.com/spreadsheets/d/1wVT6_XwgGTpyf859vmu01xtXtO6OPC2K9AG4fbhg4cs/edit#gid=xxxxxxxx')
ws = sheet.worksheet('title','January 2020')

alpha = list(string.ascii_uppercase)
new = []
for i in alpha:
    alpha2 = list(string.ascii_uppercase)
    for j in range(0,26):
        final = i+alpha2[j]
        new.append(final)
excel = alpha + new

#print(excel)
#exit()

for i in excel:
    if ws.get_value('{}1'.format(i)) == "":
        next_col = i
        break
last_col = excel[excel.index(i)-1]
#print (next_col)
#print (type(next_col))



for i in range(3,10000):
    if ws.get_value('A{}'.format(i)) == "":
        next_row = i
        break
        


list_cell_value = []

ws.update_value('{}1'.format(next_col),dat)
for j in range(2,35):
    cell_value = ws.get_value('A{}'.format(j))
    list_cell_value.append(cell_value)

diff_values = list(set(list(dictionary.keys())) - set(list_cell_value))

diff_values_no_empty = list(filter(None,diff_values))

if len(diff_values_no_empty) != 0:
    for i in range(next_row,next_row+len(diff_values)):
        ws.update_value('A{}'.format(i),diff_values[i-next_row])
    print(len(diff_values),'New elements has been found')
else:
    print('No new elements')

for i in range(2,next_row+len(diff_values)):
    cell_value = ws.get_value('A{}'.format(i))
    if cell_value in list(dictionary.keys()):
        ws.update_value('{}{}'.format(next_col,i),dictionary[cell_value])
    else:
        ws.update_value('{}{}'.format(next_col,i),'0')


if 'Tax' in dictionary:
    ws.update_value('{}34'.format(next_col),dictionary['Tax'])
    
#if service_name[-1] == 'Tax':
    #ws.update_value('{}34'.format(next_col),values[-1])
else:
    ws.update_value('{}34'.format(next_col), '0')
ws.update_value('{}37'.format(next_col), '=SUM({}2:{}34)'.format(next_col,next_col))
ws.update_value('{}38'.format(next_col), '=({}37-{}37)'.format(next_col,last_col))    

print('Cost updated successfully.....')
