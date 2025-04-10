# Remover SNS Actions de Alarmes no CloudWatch via GitHub Actions

Este projeto executa um script Python para **remover um ARN de SNS** das actions (`AlarmActions`, `OKActions`, `InsufficientDataActions`) de todos os alarmes do **Amazon CloudWatch**. Ele pode ser executado manualmente via GitHub Actions, com opção de "dry-run" para pré-visualização das alterações.

---

## :gear: Funcionalidades
- Lista todos os alarmes do CloudWatch.
- Verifica se o SNS Topic informado está associado a ações dos alarmes.
- Remove o tópico das ações, mantendo **todas as outras configurações do alarme inalteradas**.
- Permite execução em modo **dry-run** com confirmação antes de aplicar alterações.
- Integração segura com AWS via **OIDC + IAM Role assumida por GitHub Actions**.

---

## :snake: Script Python (`main.py`)

### Argumentos
```bash
python main.py <sns_topic_arn> <confirm (s/N)>
```
- `sns_topic_arn`: ARN do tópico SNS a remover.
- `confirm`: Digite `s` para aplicar alterações. Qualquer outro valor executa apenas o dry-run.

### Comportamento
- Se `confirm != "s"`: O script lista os alarmes que **seriam** modificados.
- Se `confirm == "s"`: O script aplica a remoção da action e atualiza o alarme com os mesmos dados.

---

## :octocat: GitHub Actions Workflow

### Execução manual
O workflow pode ser executado via UI do GitHub usando `workflow_dispatch`, exigindo os seguintes inputs:

```yaml
on:
  workflow_dispatch:
    inputs:
      sns_topic:
        description: 'ARN do tópico SNS a remover das actions'
        required: true
      confirm:
        description: 'Digite "s" para confirmar que deseja aplicar as alterações (caso contrário, será dry-run)'
        required: true
        default: 'n'
```

### Permissões
```yaml
permissions:
  id-token: write
  contents: read
```

### Etapas principais
```yaml
- name: Configurar credenciais AWS
  uses: aws-actions/configure-aws-credentials@v2
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_TO_ASSUME }}
    aws-region: ${{ secrets.AWS_REGION }}

- name: Rodar script Python
  run: |
    python main.py "${{ github.event.inputs.sns_topic }}" "${{ github.event.inputs.confirm }}"
```

---

## :lock: Segurança
- A autenticação com a AWS é feita via **OIDC**.
- A Role utilizada define permissões específicas para interagir com o CloudWatch.
- Nenhuma alteração é aplicada sem confirmação explícita do usuário.

---

## :memo: Exemplo de saída (dry-run)
```
[DRY-RUN] Alarmes que seriam atualizados:
- Meu-Alarme-Teste
    [REMOVER] arn:aws:sns:...:sns-black-friday de AlarmActions no alarme 'Meu-Alarme-Teste'
    [REMOVER] arn:aws:sns:...:sns-black-friday de OKActions no alarme 'Meu-Alarme-Teste'

Deseja aplicar essas alterações? (s/N):
```

---

## :warning: Importante
- Este script **não altera nenhuma configuração** dos alarmes além de remover o SNS especificado.
- Ideal para cenários como limpeza de tópicos SNS obsoletos antes de descomissionamento.
