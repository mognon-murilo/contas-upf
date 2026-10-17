# Aula 1: relatos de defeito

Casos de teste correspondentes: [`aula1_casos_de_teste.csv`](aula1_casos_de_teste.csv).

## D1. Pagamento no dia do vencimento é cobrado com multa

```text
Título: Baixa feita no dia do vencimento cobra multa de 2%
Ambiente: versão da aula 1 (commit 11bfccd), Docker Desktop no Windows 10, navegador Chromium, http://localhost:8000
Regra relacionada: 4 (Encargos por atraso)
Passos para reproduzir:
  1. Em Novo título, cadastrar: tipo A pagar, descrição qualquer, valor 1000,00, vencimento 10/11/2026 (terça-feira), 1 parcela.
  2. Na lista de títulos, clicar em Baixar no título criado.
  3. Registrar baixa de 1000,00 com data de pagamento 10/11/2026.
Resultado esperado: encargos 0,00 ("Pagamento até o dia do vencimento, inclusive, não tem encargos").
Resultado obtido: encargos 20,00 (multa de 2% cobrada sem nenhum dia de atraso).
Severidade (baixa, média, alta): alta
```

Observações: o mesmo defeito aparece quando o vencimento cai no fim de semana e o pagamento é feito
na segunda-feira prorrogada (CT21 e CT24: encargos 20,00 em vez de 0,00). A prorrogação em si está
correta: pagando na terça-feira, os encargos são de 1 dia (20,33). Atinge todo cliente que paga em dia.

## D2. Baixa maior que o saldo é aceita

```text
Título: Sistema aceita baixa com valor maior que o saldo e deixa o saldo negativo
Ambiente: versão da aula 1 (commit 11bfccd), Docker Desktop no Windows 10, navegador Chromium, http://localhost:8000
Regra relacionada: 3 (Baixa)
Passos para reproduzir:
  1. Cadastrar título a pagar de 1000,00 com vencimento 10/11/2026, 1 parcela.
  2. Clicar em Baixar no título criado.
  3. Registrar baixa de 1000,01 com data de pagamento 09/11/2026.
Resultado esperado: baixa rejeitada, pois o valor não pode ser maior que o saldo (1000,00).
Resultado obtido: baixa registrada; saldo -0,01 e status "parcial".
Severidade (baixa, média, alta): alta
```

## D3. Título cancelado recebe baixa e volta a ficar ativo

```text
Título: Baixa em título cancelado é aceita e muda o status de cancelado para parcial
Ambiente: versão da aula 1 (commit 11bfccd), Docker Desktop no Windows 10, navegador Chromium, http://localhost:8000
Regra relacionada: 3 (Baixa) e 2 (Status)
Passos para reproduzir:
  1. Cadastrar título a pagar de 1000,00 com vencimento 10/11/2026, 1 parcela.
  2. Na lista de títulos, clicar em Cancelar no título criado (status passa a "cancelado").
  3. Clicar em Baixar no mesmo título e registrar baixa de 100,00 com data 09/11/2026.
Resultado esperado: baixa rejeitada ("Título cancelado ou quitado não recebe baixa"); status continua "cancelado".
Resultado obtido: baixa registrada; saldo 900,00 e status "parcial".
Severidade (baixa, média, alta): alta
```

Observação: em título quitado a regra funciona (CT28: a baixa é rejeitada).

## D4. Parcelamento perde os centavos da divisão

```text
Título: Soma das parcelas fica menor que o valor original
Ambiente: versão da aula 1 (commit 11bfccd), Docker Desktop no Windows 10, navegador Chromium, http://localhost:8000
Regra relacionada: 6 (Parcelamento)
Passos para reproduzir:
  1. Em Novo título, cadastrar: tipo A pagar, valor 100,00, vencimento 10/11/2026, parcelas 3.
  2. Conferir na lista de títulos os valores das parcelas (1/3), (2/3) e (3/3).
Resultado esperado: 33,34, 33,33 e 33,33 (soma 100,00; os centavos que sobram vão para a primeira parcela).
Resultado obtido: 33,33, 33,33 e 33,33 (soma 99,99; 1 centavo perdido).
Severidade (baixa, média, alta): média
```

Observação: com 100,00 em 6 vezes a perda é de 4 centavos (seis parcelas de 16,66; soma 99,96).
Os vencimentos de 30 em 30 dias estão corretos.

## D5. Título com valor zero ou negativo é cadastrado

```text
Título: Cadastro aceita título com valor 0,00 ou negativo
Ambiente: versão da aula 1 (commit 11bfccd), Docker Desktop no Windows 10, navegador Chromium, http://localhost:8000
Regra relacionada: 1 (Valor do título)
Passos para reproduzir:
  1. Em Novo título, cadastrar: tipo A pagar, descrição qualquer, valor 0,00, vencimento 10/11/2026, 1 parcela.
  2. Repetir com valor -50,00.
Resultado esperado: os dois cadastros rejeitados, pois o valor deve ser maior que zero.
Resultado obtido: os dois títulos são cadastrados (valor 0.00 com saldo 0.00; valor -50.00 com saldo -50.00), com status "aberto".
Severidade (baixa, média, alta): média
```

Observação: as outras validações do cadastro funcionam (descrição vazia, tipo inválido e parcelas
menores que 1 são rejeitados).
