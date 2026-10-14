from datetime import datetime, timedelta


def _ultimo_dia_mes_anterior():
    hoje = datetime.now()
    return datetime(hoje.year, hoje.month, 1) - timedelta(days=1)


def gerar_intervalo_datas():
    ultimo_dia = _ultimo_dia_mes_anterior()
    primeiro_dia = ultimo_dia.replace(day=1)
    return primeiro_dia.strftime("%d%m%Y"), ultimo_dia.strftime("%d%m%Y")


def dataContaCorrente():
    ultimo_dia = _ultimo_dia_mes_anterior()
    return ultimo_dia.month, ultimo_dia.year
