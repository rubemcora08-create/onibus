import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from datetime import datetime
import re
from pathlib import Path

EXCEL_PATH = Path("onibusurbano_dados.xlsx")

def save_to_excel(data):
    # Lê se existir, senão cria DF vazio
    try:
        df = pd.read_excel(EXCEL_PATH)
    except FileNotFoundError:
        df = pd.DataFrame()

    # Coluna com timestamp da execução
    date_col = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")  # UTC (cron do GitHub usa UTC)
    new_data_df = pd.DataFrame(data, columns=["Cidade", date_col])

    # Garante coluna 'Cidade' como chave
    if "Cidade" not in df.columns:
        df = pd.DataFrame({"Cidade": new_data_df["Cidade"]})

    # Faz merge para anexar a nova coluna pelo nome da cidade
    df = df.merge(new_data_df[["Cidade", date_col]], on="Cidade", how="outer")

    # Ordena por Cidade para manter estável
    df = df.sort_values("Cidade").reset_index(drop=True)

    # Salva (engine openpyxl garante compatibilidade)
    df.to_excel(EXCEL_PATH, index=False, engine="openpyxl")
    print(f"\n✅ Dados salvos em '{EXCEL_PATH.resolve()}' na coluna '{date_col}'.")

def fetch_bus_tariff():
    urls = [
        ("Porto Alegre", "https://prefeitura.poa.br/transporte"),
        ("São Paulo", "https://www.sptrans.com.br/tarifas"),
        ("Belo Horizonte", "https://prefeitura.pbh.gov.br/bhtrans/informacoes/transportes/onibus/tarifas-e-integracao"),
        ("Rio de Janeiro", "https://www.riocardmais.com.br/Tarifas"),
        ("Fortaleza", "https://catalogodeservicos.fortaleza.ce.gov.br/categoria/mobilidade/servico/86"),
        ("Recife", "https://www.granderecife.pe.gov.br/transporte/tarifas/")
    ]

    chromedriver_autoinstaller.install()

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)
    data = []

    try:
        for city, url in urls:
            try:
                driver.get(url)
                print(f"\n🔗 Página de {city} carregada.")
                wait = WebDriverWait(driver, 30)
                value = "N/A"

                if city == "Porto Alegre":
                    element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "numero_destaque")))
                    value = element.text.strip().replace("R$", "").replace(",", ".").strip()

                elif city == "São Paulo":
                    element = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/section/div[2]/div/div/div/table[1]/tbody/tr[2]/td[2]/span/span/span/span')))
                    value = element.text.strip().replace("R$", "").replace(",", ".").strip()

                elif city == "Belo Horizonte":
                    element = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[5]/div/div/div/div/div[1]/div/div/div/div[2]/div/div/div/div/div/div/div/div/div[1]/div/div/div[1]/div/div/div/div/div/div/div[3]/div/table/tbody/tr[5]/td[2]')))
                    value = element.text.strip().replace("R$", "").replace(",", ".").strip()

                elif city == "Rio de Janeiro":
                    try:
                        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                        match = re.search(r"ônibus.*r\$\s?(\d+,\d{2})", body_text)
                        if match:
                            value = match.group(1).replace(",", ".").strip()
                        else:
                            raise ValueError("Tarifa não localizada no texto da página.")
                    except Exception as e:
                        print(f"❌ Erro ao coletar dados de {city}: {e}")
                        value = "Erro"

                elif city == "Fortaleza":
                    body = driver.find_element(By.TAG_NAME, "body").text
                    match = re.search(r"(?i)-\s*inteira:\s*R\$\s*(\d+,\d{2})", body)
                    if match:
                        value = match.group(1).replace(",", ".").strip()
                    else:
                        value = "Erro"

                elif city == "Recife":
                    element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div[2]/div/main/div/div/div[2]/table/tbody/tr/td[2]/span/b')))
                    value = element.text.strip().replace("R$", "").replace(",", ".").strip()

                print(f"✅ Tarifa em {city}: R$ {value}")

            except Exception as e:
                print(f"❌ Erro ao coletar dados de {city}: {e}")
                value = "Erro"

            data.append([city, value])

        save_to_excel(data)

    finally:
        driver.quit()

if __name__ == "__main__":
    fetch_bus_tariff()
