import subprocess
import time
import pandas as pd


def readCSV(arquivo, sep):
    df = pd.read_csv(arquivo, sep=sep)
    return df

def saveCSV(df, file, sep):
    df.to_csv(file, index=False, sep=sep, encoding='utf-8')

def saveCSVSigEncoding(df, file, sep):
    df.to_csv(file, index=False, sep=sep, encoding='utf-8-sig')

def readExcel(arquivo):
    df = pd.read_excel(arquivo)
    return df

def readExcelSheet(arquivo, sheet):
    df = pd.read_excel(arquivo, sheet_name=sheet)
    return df

def saveExcel(df, file):
    df.to_excel(file, index=False)

def deleteCsv(file):
    try:
        os.remove(file)
    except OSError:
        pass


def connectVPN():
    pydirectinput.doubleClick(30, 30)
    pydirectinput.moveTo(950, 325)
    pydirectinput.click(950, 325)
    pydirectinput.moveTo(950, 720)
    pydirectinput.click(950, 720)


def checkVPN():
    output = subprocess.check_output(['ipconfig', '/all']).decode('latin-1')

    if 'Fortinet SSL VPN' in output:
        print('VPN Conectada')
    else:
        print('VPN Desconectada')
        connectVPN()

        print('Aguardando 30 segundos para iniciar o processo')

        time.sleep(30)

def vpn():
    for i in range(2):
        checkVPN()
        print('Loop: ', i)
        time.sleep(15)
