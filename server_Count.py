import boto3
import pygsheets
from datetime import timedelta, datetime, date
from settings import api_asg_name, api_spot_fleet, api_ondemand_cpu, api_spot_cpu, api_sheet, api_server_count_sheet
from settings import web_asg_name, web_spot_fleet, web_ondemand_cpu, web_spot_cpu, web_sheet, web_server_count_sheet

time_range = datetime.now() - timedelta(hours=8)

date = date.today() #- timedelta(days=1)

dat = date.strftime("%d-%B-%Y")

source_region='eu-west-2'
destination_region='eu-west-1'
a_key='xxxxxxxxxxxx'
s_key='xxxxxxxxxxxx'

def serverdetails(asg_name, spot_fleet_id, ondemand_cpu, spot_cpu, sheet, server_count_sheet):

    cloudwatch = boto3.resource('cloudwatch',aws_access_key_id=a_key,aws_secret_access_key=s_key,region_name=source_region)
    metric_ondemand = cloudwatch.Metric('AWS/AutoScaling','GroupInServiceInstances')
    on_demand_count = metric_ondemand.get_statistics(Dimensions=[{'Name': 'AutoScalingGroupName','Value': asg_name }],StartTime= time_range, EndTime=datetime.now(),Period=86400,Statistics=['Maximum'],)

    metric_spot = cloudwatch.Metric('AWS/EC2Spot','FulfilledCapacity')
    spot_count = metric_spot.get_statistics(Dimensions=[{'Name': 'FleetRequestId','Value': spot_fleet_id }],StartTime=time_range,EndTime=datetime.now(),Period=86400,Statistics=['Maximum'],)

    cpu = boto3.client('cloudwatch',aws_access_key_id=a_key,aws_secret_access_key=s_key,region_name=source_region)
    ondemand_cpu = cpu.describe_alarms(AlarmNames=[ondemand_cpu])
    spot_cpu = cpu.describe_alarms(AlarmNames=[spot_cpu])

    if asg_name == api_asg_name:
        credentials = pygsheets.authorize(service_file='/root/NewRelic-6d54dec5d48c.json')
        sheet = credentials.open_by_url(sheet)
        ws3 = sheet.worksheet('title',server_count_sheet)
        for i in range(2,10000):
            if ws3.get_value('A{}'.format(i)) == "":
                next_row = i
                break
        ws3.update_value('A{}'.format(next_row),dat)
        ws3.update_value('B{}'.format(next_row),int(on_demand_count['Datapoints'][0]['Maximum']))
        ws3.update_value('C{}'.format(next_row),int(spot_count['Datapoints'][0]['Maximum']))
        ws3.update_value('D{}'.format(next_row),str(int(ondemand_cpu['MetricAlarms'][0]['Threshold']))+'%')
        ws3.update_value('E{}'.format(next_row),str(int(spot_cpu['MetricAlarms'][0]['Threshold']))+'%')
        ws3_bor=pygsheets.DataRange(start='A{}'.format(next_row), end='E{}'.format(next_row), worksheet=ws3).update_borders(top=True, right=True, bottom=True, left=True, inner_horizontal=True,inner_vertical=True,style='SOLID')
    else:
        credentials = pygsheets.authorize(service_file='/root/NewRelic-6d54dec5d48c.json')
        sheet = credentials.open_by_url(sheet)
        ws3 = sheet.worksheet('title',server_count_sheet)
        for i in range(2,10000):
            if ws3.get_value('A{}'.format(i)) == "":
                next_row = i
                break
        ws3.update_value('A{}'.format(next_row),dat)
        ws3.update_value('B{}'.format(next_row),int(on_demand_count['Datapoints'][0]['Maximum']))
        ws3.update_value('C{}'.format(next_row),int(spot_count['Datapoints'][0]['Maximum']))
        ws3.update_value('D{}'.format(next_row),str(int(ondemand_cpu['MetricAlarms'][0]['Threshold']))+'%')
        ws3.update_value('E{}'.format(next_row),str(int(spot_cpu['MetricAlarms'][0]['Threshold']))+'%')
        ws3_bor=pygsheets.DataRange(start='A{}'.format(next_row), end='E{}'.format(next_row), worksheet=ws3).update_borders(top=True, right=True, bottom=True, left=True, inner_horizontal=True,inner_vertical=True,style='SOLID')

update_api_sheet = serverdetails(api_asg_name,api_spot_fleet,api_ondemand_cpu,api_spot_cpu,api_sheet,api_server_count_sheet)
print('API updated successfully....')
update_web_sheet = serverdetails(web_asg_name,web_spot_fleet,web_ondemand_cpu,web_spot_cpu,web_sheet,web_server_count_sheet)
print('WebApp updated successfully....')
