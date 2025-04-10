import boto3
import sys

def remove_sns_actions(topic_arn, confirm):
    cloudwatch = boto3.client('cloudwatch')
    paginator = cloudwatch.get_paginator('describe_alarms')

    alarms_to_update = []

    print("\n[DRY-RUN] Alarmes que seriam atualizados:")
    for page in paginator.paginate():
        for alarm in page['MetricAlarms']:
            changed = False

            for action_list_name in ['AlarmActions', 'OKActions', 'InsufficientDataActions']:
                actions = alarm.get(action_list_name, [])
                if topic_arn in actions:
                    changed = True

            if changed:
                print(f"- {alarm['AlarmName']}")
                for action_list_name in ['AlarmActions', 'OKActions', 'InsufficientDataActions']:
                    actions = alarm.get(action_list_name, [])
                    if topic_arn in actions:
                        print(f"    [REMOVER] {topic_arn} de {action_list_name} no alarme '{alarm['AlarmName']}'")
                alarms_to_update.append(alarm)

    if not alarms_to_update:
        print("\nNenhum alarme será alterado.")
        return

    if confirm.strip().lower() != 's':
        print("\n[DRY-RUN] As alterações NÃO foram aplicadas. Execute novamente com confirmação 's' para aplicar.")
        return

    print("\n[ATUALIZAÇÃO] Iniciando remoção real...")
    for alarm in alarms_to_update:
        for action_list_name in ['AlarmActions', 'OKActions', 'InsufficientDataActions']:
            actions = alarm.get(action_list_name, [])
            if topic_arn in actions:
                print(f"[INFO] Removendo {topic_arn} de {action_list_name} no alarme '{alarm['AlarmName']}'")
                actions = [a for a in actions if a != topic_arn]
            alarm[action_list_name] = actions

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
        print(f"[INFO] Alarme '{alarm['AlarmName']}' atualizado.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python main.py <sns_topic_arn> <confirm (s/N)>")
        sys.exit(1)

    topic_arn = sys.argv[1]
    confirm = sys.argv[2]
    remove_sns_actions(topic_arn, confirm)
