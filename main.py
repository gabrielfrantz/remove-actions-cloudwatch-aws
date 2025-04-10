import boto3
import sys

def remove_sns_actions(topic_arn):
    cloudwatch = boto3.client('cloudwatch')

    paginator = cloudwatch.get_paginator('describe_alarms')
    for page in paginator.paginate():
        for alarm in page['MetricAlarms']:
            changed = False

            for action_list_name in ['AlarmActions', 'OKActions', 'InsufficientDataActions']:
                actions = alarm.get(action_list_name, [])
                if topic_arn in actions:
                    actions.remove(topic_arn)
                    changed = True
                    print(f"[INFO] Removendo {topic_arn} de {action_list_name} em '{alarm['AlarmName']}'")
                    alarm[action_list_name] = actions  # Atualiza na estrutura local

            if changed:
                # Monta os parâmetros dinamicamente
                params = {
                    'AlarmName': alarm['AlarmName'],
                    'MetricName': alarm['MetricName'],
                    'Namespace': alarm['Namespace'],
                    'ComparisonOperator': alarm['ComparisonOperator'],
                    'Threshold': alarm['Threshold'],
                    'Period': alarm['Period'],
                    'EvaluationPeriods': alarm['EvaluationPeriods'],
                    'AlarmActions': alarm.get('AlarmActions', []),
                    'OKActions': alarm.get('OKActions', []),
                    'InsufficientDataActions': alarm.get('InsufficientDataActions', []),
                    'Dimensions': alarm.get('Dimensions', []),
                    'ActionsEnabled': alarm.get('ActionsEnabled', True),
                    'TreatMissingData': alarm.get('TreatMissingData', 'missing')
                }

                # Campos opcionais (só adiciona se não for None)
                if alarm.get('Statistic') is not None:
                    params['Statistic'] = alarm['Statistic']
                if alarm.get('ExtendedStatistic') is not None:
                    params['ExtendedStatistic'] = alarm['ExtendedStatistic']
                if alarm.get('DatapointsToAlarm') is not None:
                    params['DatapointsToAlarm'] = alarm['DatapointsToAlarm']
                if alarm.get('Unit') is not None:
                    params['Unit'] = alarm['Unit']
                if alarm.get('ThresholdMetricId') is not None:
                    params['ThresholdMetricId'] = alarm['ThresholdMetricId']

                cloudwatch.put_metric_alarm(**params)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python main.py <sns_topic_arn>")
        sys.exit(1)

    topic_arn = sys.argv[1]
    remove_sns_actions(topic_arn)
