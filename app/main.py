from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from src.processor import process_financial_file

app = FastAPI(
    title="Financial Data Processor API",
    description="API for processing and validating financial CSV files.",
    version="1.0.0"
)

UPLOAD_DIR = Path("data/uploads")
OUTPUT_DIR = Path("output")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "financial-data-processor-api",
        "version": "1.0.0"
    }

@app.post("/process-csv")
async def process_csv(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported."
        )

    input_file = UPLOAD_DIR / file.filename

    # nomes únicos para evitar sobrescrita
    timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M")
    output_data_file = OUTPUT_DIR / f"processed_data_{timestamp}.csv"
    output_report_file = OUTPUT_DIR / f"financial_report_{timestamp}.txt"

    # salvar upload
    with open(input_file, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    try:
        df, kpis = process_financial_file(
            str(input_file),
            str(output_data_file),
            str(output_report_file)
        )

        # padronizar tipos
        kpis = {k: float(v) for k, v in kpis.items()}

        # validation summary
        valid = kpis["valid_transactions"]
        total = kpis["total_transactions"]
        invalid = kpis["invalid_transactions"]

        validation_summary = {
            "valid_rows": int(valid),
            "invalid_rows": int(invalid),
            "invalid_rate": float(invalid / total) if total else 0.0
        }

        # preview das primeiras linhas
        preview = df.head(5).to_dict(orient="records")

        return {
            "status": "success",
            "message": "File processed successfully",
            "kpis": kpis,
            "validation_summary": validation_summary,
            "preview": preview,
            "outputs": {
                "processed_data_file": str(output_data_file),
                "financial_report_file": str(output_report_file)
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")