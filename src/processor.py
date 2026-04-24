# Imports
from src.reader import read_csv
from src.validator import validate_required_columns, add_validation_columns
from src.reporter import save_processed_data
from src.metrics import calculate_kpis, save_kpis_report


# Functions
def process_financial_file(input_file, output_data_file, output_report_file):
    # Usa a função pra ler o arquivo
    df = read_csv(input_file)

    # Usa a função pra validar o arquivo
    validate_required_columns(df)

    # Usa a função pra adicionar colunas de verificação no arquivo
    df = add_validation_columns(df)

    # Usa a função pra salvar o arquivo processado
    save_processed_data(df, output_data_file)

    # Usa a função pra calcular os KPIs
    kpis = calculate_kpis(df)

    # Usa a função pra salvar os KPIs em um arquivo txt
    save_kpis_report(kpis, output_report_file)

    return df, kpis