import pandas as pd
import pandas_gbq as gbq
from pprint import pprint

# Carregar diferentes arquivos usando o pandas. 
# df = pd.read_csv('./caminho/arquivo.csv')
# df = pd.read_excel('./caminho/arquivo.xlsx')
# df = pd.read_json('./caminho/arquivo.json')
# df = pd.read_parquet('./caminho/arquivo.parquet')
# df = pd.read_xml('./caminho/arquivo.xml')
#...

pd.set_option("display.max_columns", 5)

df = pd.read_csv('./users.csv')
pprint(df.head(1).to_dict())