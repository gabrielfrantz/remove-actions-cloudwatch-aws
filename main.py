import boto3
import sys

def remove_sns_actions(topic_arn):
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

    confirm = input("\nDeseja aplicar essas alterações? (s/N): ").strip().lower()
    if confirm != 's':
        print("Operação cancelada.")
        return

    print("\n[ATUALIZAÇÃO] Iniciando remoção real...")

    for alarm in alarms_to_update:
        # Para cada alarme, itera em cada lista e remove as actions solicitadas, com log detalhado.
        for action_list_name in ['AlarmActions', 'OKActions', 'InsufficientDataActions']:
            actions = alarm.get(action_list_name, [])
            if topic_arn in actions:
                print(f"[INFO] Removendo {topic_arn} de {action_list_name} no alarme '{alarm['AlarmName']}'")
                actions = [a for a in actions if a != topic_arn]
            alarm[action_list_name] = actions

        # Prepara os parâmetros para atualização, somente adicionando campos opcionais se não forem None
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
    if len(sys.argv) < 2:
        print("Uso: python main.py <sns_topic_arn>")
        sys.exit(1)

    topic_arn = sys.argv[1]
    remove_sns_actions(topic_arn)
