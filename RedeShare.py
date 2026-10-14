import ctypes
import os
from contextlib import contextmanager
from ctypes import wintypes

RESOURCETYPE_DISK = 1
CONNECT_TEMPORARY = 4
ERRO_JA_CONECTADO = 1219


class NETRESOURCE(ctypes.Structure):
    _fields_ = [
        ("dwScope", wintypes.DWORD),
        ("dwType", wintypes.DWORD),
        ("dwDisplayType", wintypes.DWORD),
        ("dwUsage", wintypes.DWORD),
        ("lpLocalName", wintypes.LPWSTR),
        ("lpRemoteName", wintypes.LPWSTR),
        ("lpComment", wintypes.LPWSTR),
        ("lpProvider", wintypes.LPWSTR),
    ]


@contextmanager
def conexao_rede(compartilhamento):
    """Conecta ao compartilhamento com REDE_USUARIO/REDE_SENHA (.env) apenas durante o bloco."""
    usuario = os.getenv("REDE_USUARIO")
    senha = os.getenv("REDE_SENHA")
    if not usuario or not senha:
        yield
        return

    mpr = ctypes.WinDLL("mpr")
    recurso = NETRESOURCE(dwType=RESOURCETYPE_DISK, lpRemoteName=compartilhamento)
    codigo = mpr.WNetAddConnection2W(
        ctypes.byref(recurso), senha, usuario, CONNECT_TEMPORARY
    )
    if codigo == ERRO_JA_CONECTADO:
        raise ConnectionError(
            f"Já existe uma sessão com outro usuário em {compartilhamento} (erro 1219). "
            "Feche-a com 'net use * /delete' ou use outro nome do servidor."
        )
    if codigo != 0:
        raise ConnectionError(
            f"Falha ao conectar em {compartilhamento} com {usuario} (erro {codigo})."
        )
    print(f"Conectado em {compartilhamento} como {usuario}.")

    try:
        yield
    finally:
        mpr.WNetCancelConnection2W(compartilhamento, 0, True)
