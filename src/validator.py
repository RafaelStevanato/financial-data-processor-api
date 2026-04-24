#Imports
import pandas as pd
# Variables
REQUIRED_COLUMNS = ["date", "description", "amount", "category"]

#Functions
def validate_required_columns(df):
    
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]

    if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")

def add_validation_columns(df):
        df["validation_status"] = "valid"
        df["validation_message"] = ""
        
        missing_required_values = df[REQUIRED_COLUMNS].isnull().any(axis=1)
        invalid_amount = pd.to_numeric(df["amount"], errors="coerce").isnull()
        invalid_category = ~df["category"].isin(["income", "expense"])
        invalid_date = pd.to_datetime(df["date"], errors="coerce").isnull()
        
        invalid_rows = missing_required_values | invalid_amount | invalid_category | invalid_date

        df.loc[invalid_rows, "validation_status"] = "invalid"
        df.loc[missing_required_values, "validation_message"] = "missing required value"
        df.loc[invalid_amount & ~missing_required_values, "validation_message"] = "invalid amount"
        df.loc[invalid_category & ~missing_required_values, "validation_message"] = "invalid category"
        df.loc[invalid_date & ~missing_required_values, "validation_message"] = "invalid date"

        return df