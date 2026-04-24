# Functions
def calculate_kpis(df):

    valid_df = df[df["validation_status"] == "valid"]
    total_income = valid_df[valid_df["category"] == "income"]["amount"].sum()
    total_expense = valid_df[valid_df["category"] == "expense"]["amount"].sum()
    balance = total_income + total_expense
    
    total_transactions = len(df)
    valid_transactions = len(valid_df)
    invalid_transactions = total_transactions - valid_transactions

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "total_transactions": total_transactions,
        "valid_transactions": valid_transactions,
        "invalid_transactions": invalid_transactions
    }

def save_kpis_report(kpis, output_file):
    with open(output_file, "w") as file:
            file.write("=== Financial Report ===\n")
            for key, value in kpis.items():
                file.write(f"{key}: {value}\n")  