from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from src.processor import process_financial_file
from src.s3_storage import upload_file_to_s3

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

    timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M")
    output_data_file = OUTPUT_DIR / f"processed_data_{timestamp}.csv"
    output_report_file = OUTPUT_DIR / f"financial_report_{timestamp}.txt"

    with open(input_file, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    try:
        df, kpis = process_financial_file(
            str(input_file),
            str(output_data_file),
            str(output_report_file)
        )

        uploaded_file_s3_uri = upload_file_to_s3(
            str(input_file),
            f"uploads/{input_file.name}"
        )

        processed_data_s3_uri = upload_file_to_s3(
            str(output_data_file),
            f"outputs/{output_data_file.name}"
        )

        financial_report_s3_uri = upload_file_to_s3(
            str(output_report_file),
            f"outputs/{output_report_file.name}"
        )

        kpis = {k: float(v) for k, v in kpis.items()}

        valid = kpis["valid_transactions"]
        total = kpis["total_transactions"]
        invalid = kpis["invalid_transactions"]

        validation_summary = {
            "valid_rows": int(valid),
            "invalid_rows": int(invalid),
            "invalid_rate": float(invalid / total) if total else 0.0
        }

        preview = df.head(5).to_dict(orient="records")

        return {
            "status": "success",
            "message": "File processed successfully",
            "kpis": kpis,
            "validation_summary": validation_summary,
            "preview": preview,
            "outputs": {
                "local_uploaded_file": str(input_file),
                "local_processed_data_file": str(output_data_file),
                "local_financial_report_file": str(output_report_file),
                "s3_uploaded_file": uploaded_file_s3_uri,
                "s3_processed_data_file": processed_data_s3_uri,
                "s3_financial_report_file": financial_report_s3_uri
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

