#Functions
def save_processed_data(df, output_file):
    df.to_csv(output_file, index=False)