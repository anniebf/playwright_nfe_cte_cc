from anticaptchaofficial.imagecaptcha import *
from anticaptchaofficial.recaptchav2proxyless import *
from anticaptchaofficial.turnstileproxyless import *
import csv
from dotenv import load_dotenv
from datetime import datetime
import time
import oracledb
import os

load_dotenv()

usernameBd = os.getenv('usernameBd') 
passwordBd= os.getenv('passwordBd')
dsn = os.getenv('dsn')

connectionBd = oracledb.connect(user=usernameBd, password=passwordBd, dsn=dsn)
cursor = connectionBd.cursor()
insert_query = ''' INSERT INTO rpa.RequisicoesCaptcha (AUTOMACAO, DATA, qtd_requisicoes, FINALIZACAO, valor_consumo,SALDO_ATUAL)
            VALUES (:automacao, :data_atual, :qtd, :finalizacao, :valor, :saldo_atual) '''
data_atual = datetime.now()

token = os.getenv("token")

def Saldo():
    # Get your balance
    solver = recaptchaV2Proxyless() # or any other class
    solver.set_verbose(1)
    solver.set_key(token)
    money_balance = solver.get_balance()
    subscription_credits_balance = solver.get_credits_balance()
    return money_balance


def anticaptchaTurnstile(automacao):
    token = os.getenv("token")

    solver = turnstileProxyless()
    solver.set_verbose(1)
    solver.set_key(token)
    solver.set_website_url("https://www.sefaz.mt.gov.br/acesso/pages/login/login.xhtml")
    solver.set_website_key("0x4AAAAAABpF5mikgYMo5Mk-")

    timeout = 120
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            token = solver.solve_and_return_solution()
            saldo_bruto = Saldo()
            saldo = round(float(saldo_bruto), 2)

            if token:
                cursor.execute(
                insert_query,
                {
                    "automacao": automacao,
                    "data_atual": data_atual,
                    "qtd": 1,
                    "FINALIZACAO":"OK",
                    "valor": 0.0007,
                    "saldo_atual": saldo,
                },
                )
                connectionBd.commit()
                return token
            else:
                cursor.execute(
                insert_query,
                {
                    "automacao": automacao,
                    "data_atual": data_atual,
                    "qtd": 1,
                    "FINALIZACAO":"ERRO",
                    "valor": 0,
                    "saldo_atual": saldo,
                },
                )
                connectionBd.commit()
                #print("Falha ao resolver CAPTCHA, tentando novamente...")
                time.sleep(3)
        except Exception as e:
            saldo_bruto = Saldo()
            saldo = round(float(saldo_bruto), 2)
            cursor.execute(
                insert_query,
                {
                    "automacao": automacao,
                    "data_atual": data_atual,
                    "qtd": 1,
                    "FINALIZACAO":"ERRO",
                    "valor": 0,
                    "saldo_atual": saldo,
                },
                )
            connectionBd.commit()
            print("Erro ao tentar resolver CAPTCHA:", e)
            time.sleep(3)

    #print("Tempo limite atingido")
    return None

if __name__ == "__main__":
    anticaptchaTurnstile("")