import os

import oracledb
from dotenv import load_dotenv

load_dotenv()


def conectar():
    return oracledb.connect(
        user=os.getenv("usernameBd"),
        password=os.getenv("passwordBd"),
        dsn=os.getenv("dsn"),
    )


def _consultar(sql):
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()


def retornoCnpj():
    return _consultar(
        """
        SELECT M0_CODIGO, M0_FILIAL, M0_CGC, M0_CODFIL FROM PROTHEUS11.sigaemp
        WHERE LENGTH(trim(M0_CGC)) >= 12
        """
    )


def retornoInscEstd():
    return _consultar(
        """
        SELECT m0_insc, M0_FILIAL, M0_CODFIL, M0_CODIGO FROM PROTHEUS11.sigaemp
        WHERE LENGTH(trim(M0_CGC)) >= 12 AND
        m0_insc NOT IN ('ISENTO',' ') OR m0_insc IS NULL
        """
    )
