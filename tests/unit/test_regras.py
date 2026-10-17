from datetime import date
from decimal import Decimal

import pytest

from app.regras import (
    RegraVioladaError,
    calcular_encargos,
    gerar_parcelas,
    novo_status,
    proximo_dia_util,
    validar_baixa,
    validar_titulo,
    vencimentos_das_parcelas,
)


def test_um_dia_de_atraso_paga_multa_mais_um_dia_de_juros():
    valor = Decimal("1000.00")
    vencimento = date(2026, 11, 10)           # terça-feira

    encargos = calcular_encargos(valor, vencimento, pagamento=date(2026, 11, 11))

    assert encargos == Decimal("20.33")       # multa 20,00 + juros de um dia 0,33


def test_parcelamento_em_zero_vezes_e_rejeitado():
    with pytest.raises(RegraVioladaError):
        gerar_parcelas(Decimal("100.00"), 0)


def test_pagamento_no_dia_do_vencimento_nao_tem_encargos():
    vencimento = date(2026, 11, 10)

    encargos = calcular_encargos(Decimal("1000.00"), vencimento, pagamento=vencimento)

    assert encargos == Decimal("0.00")


# Casos da planilha docs/aula1_casos_de_teste.csv

# Regra 4: encargos por atraso (CT15 a CT20)

def test_trinta_dias_de_atraso_pagam_multa_mais_trinta_dias_de_juros():
    vencimento = date(2026, 11, 10)

    encargos = calcular_encargos(Decimal("1000.00"), vencimento, pagamento=date(2026, 12, 10))

    assert encargos == Decimal("29.90")


def test_pagamento_antes_do_vencimento_nao_tem_encargos():
    vencimento = date(2026, 11, 10)

    encargos = calcular_encargos(Decimal("1000.00"), vencimento, pagamento=date(2026, 11, 9))

    assert encargos == Decimal("0.00")


def test_encargos_arredondam_meio_centavo_para_cima():
    vencimento = date(2026, 11, 10)

    encargos = calcular_encargos(Decimal("50.00"), vencimento, pagamento=date(2026, 11, 20))

    assert encargos == Decimal("1.17")        # 1,00 de multa + 0,165 de juros = 1,165


def test_encargos_de_baixa_parcial_incidem_sobre_o_valor_da_baixa():
    vencimento = date(2026, 11, 10)

    encargos = calcular_encargos(Decimal("500.00"), vencimento, pagamento=date(2026, 11, 11))

    assert encargos == Decimal("10.17")


# Regra 5: vencimento em fim de semana (CT21 a CT25)

def test_vencimento_no_domingo_e_prorrogado_para_segunda():
    domingo = date(2026, 11, 15)

    assert proximo_dia_util(domingo) == date(2026, 11, 16)


def test_vencimento_em_dia_util_nao_e_prorrogado():
    terca = date(2026, 11, 10)

    assert proximo_dia_util(terca) == terca


def test_vencimento_no_sabado_pago_na_segunda_nao_tem_encargos():
    sabado = date(2026, 11, 14)

    encargos = calcular_encargos(Decimal("1000.00"), sabado, pagamento=date(2026, 11, 16))

    assert encargos == Decimal("0.00")


def test_atraso_de_vencimento_no_sabado_conta_a_partir_da_segunda():
    sabado = date(2026, 11, 14)

    encargos = calcular_encargos(Decimal("1000.00"), sabado, pagamento=date(2026, 11, 17))

    assert encargos == Decimal("20.33")       # um dia de atraso, não três


# Regra 6: parcelamento (CT08 a CT13)

def test_centavos_que_sobram_vao_para_a_primeira_parcela():
    parcelas = gerar_parcelas(Decimal("100.00"), 3)

    assert parcelas == [Decimal("33.34"), Decimal("33.33"), Decimal("33.33")]


def test_soma_das_parcelas_e_o_valor_original():
    parcelas = gerar_parcelas(Decimal("100.00"), 6)

    assert sum(parcelas) == Decimal("100.00")


def test_parcelamento_em_uma_vez_e_o_proprio_valor():
    parcelas = gerar_parcelas(Decimal("100.00"), 1)

    assert parcelas == [Decimal("100.00")]


def test_parcelamento_em_quantidade_negativa_e_rejeitado():
    with pytest.raises(RegraVioladaError):
        gerar_parcelas(Decimal("100.00"), -1)


def test_parcelas_vencem_de_trinta_em_trinta_dias():
    vencimentos = vencimentos_das_parcelas(date(2026, 11, 10), 3)

    assert vencimentos == [date(2026, 11, 10), date(2026, 12, 10), date(2027, 1, 9)]


# Regra 1: cadastro do título (CT02 a CT07)

def test_titulo_com_valor_zero_e_rejeitado():
    with pytest.raises(RegraVioladaError):
        validar_titulo("pagar", "Aluguel", Decimal("0.00"))


def test_titulo_com_valor_negativo_e_rejeitado():
    with pytest.raises(RegraVioladaError):
        validar_titulo("pagar", "Aluguel", Decimal("-50.00"))


def test_titulo_com_um_centavo_e_aceito():
    validar_titulo("pagar", "Aluguel", Decimal("0.01"))      # não pode levantar exceção


def test_titulo_sem_descricao_e_rejeitado():
    with pytest.raises(RegraVioladaError):
        validar_titulo("pagar", "   ", Decimal("100.00"))


def test_titulo_com_tipo_invalido_e_rejeitado():
    with pytest.raises(RegraVioladaError):
        validar_titulo("outro", "Aluguel", Decimal("100.00"))


# Regra 3: baixa (CT28 a CT32)

def test_baixa_maior_que_o_saldo_e_rejeitada():
    with pytest.raises(RegraVioladaError):
        validar_baixa(saldo=Decimal("1000.00"), status="aberto", valor=Decimal("1000.01"))


def test_baixa_igual_ao_saldo_e_aceita():
    validar_baixa(saldo=Decimal("600.00"), status="parcial", valor=Decimal("600.00"))


def test_baixa_em_titulo_cancelado_e_rejeitada():
    with pytest.raises(RegraVioladaError):
        validar_baixa(saldo=Decimal("1000.00"), status="cancelado", valor=Decimal("100.00"))


def test_baixa_em_titulo_quitado_e_rejeitada():
    with pytest.raises(RegraVioladaError):
        validar_baixa(saldo=Decimal("0.00"), status="quitado", valor=Decimal("1.00"))


def test_baixa_de_valor_zero_e_rejeitada():
    with pytest.raises(RegraVioladaError):
        validar_baixa(saldo=Decimal("1000.00"), status="aberto", valor=Decimal("0.00"))


# Regra 2: status depois da baixa (CT26 e CT27)

def test_baixa_parcial_deixa_o_titulo_parcial():
    assert novo_status(Decimal("1000.00"), saldo_restante=Decimal("600.00")) == "parcial"


def test_baixa_do_saldo_inteiro_quita_o_titulo():
    assert novo_status(Decimal("1000.00"), saldo_restante=Decimal("0.00")) == "quitado"
