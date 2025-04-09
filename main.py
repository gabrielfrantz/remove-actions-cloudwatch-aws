import boto3
import sys

def remove_sns_actions(topic_arn):
    cloudwatch = boto3.client('cloudwatch')

    paginator = cloudwatch.get_paginator('describe_alarms')
    for page in paginator.paginate():
        for alarm in page['MetricAlarms']:
            actions_to_remove = []
            changed = False

            for action_list_name in ['AlarmActions', 'OKActions', 'InsufficientDataActions']:
                actions = alarm.get(action_list_name, [])
                if topic_arn in actions:
                    actions.remove(topic_arn)
                    changed = True
                    print(f"[INFO] Removendo {topic_arn} de {action_list_name} em '{alarm['AlarmName']}'")
                alarm[action_list_name] = actions

            if changed:
                cloudwatch.put_metric_alarm(
                    AlarmName=alarm['AlarmName'],
                    MetricName=alarm['MetricName'],
                    Namespace=alarm['Namespace'],
                    Statistic=alarm.get('Statistic'),
                    Dimensions=alarm.get('Dimensions', []),
                    Period=alarm['Period'],
                    EvaluationPeriods=alarm['EvaluationPeriods'],
                    Threshold=alarm['Threshold'],
                    ComparisonOperator=alarm['ComparisonOperator'],
                    AlarmActions=alarm.get('AlarmActions', []),
                    OKActions=alarm.get('OKActions', []),
                    InsufficientDataActions=alarm.get('InsufficientDataActions', []),
                    ActionsEnabled=True,
                    Unit=alarm.get('Unit'),
                    TreatMissingData=alarm.get('TreatMissingData', 'missing'),
                    DatapointsToAlarm=alarm.get('DatapointsToAlarm')
                )

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python remove_sns_actions.py <sns_topic_arn>")
        sys.exit(1)

    topic_arn = sys.argv[1]
    remove_sns_actions(topic_arn)
