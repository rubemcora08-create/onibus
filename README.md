Coleta de tarifas de ônibus (cidades brasileiras)
Script em Python que coleta as tarifas de ônibus de algumas capitais por Selenium, salva/atualiza onibusurbano_dados.xlsx e faz commit mensal automático via GitHub Actions.

Como usar
Crie um repositório no GitHub e suba estes arquivos:
onibus_scraper.py
requirements.txt
.github/workflows/scrape.yml
Faça o primeiro commit/push.
O GitHub Actions rodará todo dia 10 às 12:00 UTC e atualizará o Excel com uma nova coluna timbrada com o timestamp (UTC) da execução.
Você também pode rodar manualmente em Actions → Coleta tarifas ônibus → Run workflow.
O arquivo onibusurbano_dados.xlsx fica na raiz do repositório e é versionado.

Copied! 
