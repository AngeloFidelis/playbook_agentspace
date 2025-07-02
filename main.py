import bson
from bson.codec_options import CodecOptions, DatetimeConversion
import pandas as pd
import pandas_gbq as gbq
import os
import logging

# define opções de decodificação para datas no formato de milissegundos presentes no banco
codec_options = CodecOptions(datetime_conversion=DatetimeConversion.DATETIME_MS)
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './credentials.json'

# configuração para logging da aplicação
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)

# lista vazia que vai servir para armazenar os dados conforme eles são transformados
rows = []

# Nome do projeto, dataset e da tabela de destino dos dados
data_set_name = "agent_space_data_1p"
tabela_name = '' #definir com base no caso de uso.
project_id = 'agentspace-trial-na'

# função para extrair os dados do arquivo BSON
def extract_data(path):
    with open(path, 'rb') as mongodb_file:
        data_users = bson.decode_all(mongodb_file.read(), codec_options=codec_options)
        return data_users


# função para transformar os dados extraídos em um formato estruturado
def transform_data(data_users):
    for data in data_users:
        try:
            # Extrai informações principais do usuário
            position = data.get('positions', [{}])[0].get("name", None)
            name = data.get('name', None)
            email = data.get('email', None)
            isactive = data.get('isActive', None)
            provider = data.get('provider', None)

            """
            As listas abaixam vão armazenar as informações em array, para que haja apenas uma
            entidade por linha, sem que os dados sejam perdidos
            """
            language_skills = [
                {
                    "language": lang.get('name'),
                    "level": lang.get('level'),
                } for lang in data.get('languageSkills', [])
            ]

            certifications = [
                {
                    "authority": cert.get('authority'),
                    "certification": cert.get('name'),
                } for cert in data.get('certifications', [])
            ]

            education = [
                {
                    "field": edu.get('field'),
                    "degree": edu.get('degree'),
                    "school": edu.get('school'),
                    "status": edu.get('status'),
                } for edu in data.get('education', [])
            ]

            skillscloud = [
                {
                    "experience_years": int(skill.get('experienceYears')),
                    "stack": skill.get('name')
                } for skill in data.get('skillsCloud', [])
            ]
            # Cria um dicionario efêmero com todos os dados transformados
            row_dataframe = {
                'name': name,
                'email': email,
                "position": position,
                'isActive': isactive,
                'provider': provider,
                'language_skills': language_skills,
                'certifications': certifications,
                'education': education,
                'skillscloud': skillscloud
            }
            
            # Armazena esse dicionario efêmero dentro da lista criada no início do código
            rows.append(row_dataframe)

        except Exception as e:
            # Em caso de erro, exibe a mensagem e continua com o próximo usuário
            print(f"Erro ao processar usuário: {e}")
            continue

    # Converte a lista de dicionários para um DataFrame
    df_users = pd.DataFrame(rows)
    print(df_users.dtypes)
    return df_users
    
    #função para carregar os dados no BigQuery e salvar uma cópia local em CSV
def load_data(df_users):
    df_users.to_csv('users.csv', index=None)
    
    path_table_projects = ".".join([data_set_name, tabela_name])
    gbq.to_gbq(df_users, path_table_projects,project_id=project_id, if_exists='replace')
    
    

# Execução principal do script
if __name__ == "__main__":
    data_users = extract_data('./users.bson') # Extração
    df_users = transform_data(data_users)     # Transformação
    load_data(df_users)                       # Carregamento
