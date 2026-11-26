
import json
import boto3
import os

from io import BytesIO
from urllib.parse import unquote_plus
from pypdf import PdfReader

s3 = boto3.client("s3")
BUCKET_NAME = os.environ["BUCKET_NAME"]

MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_PAGES = 200


def lambda_handler(event, context):
    results = []

    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = unquote_plus(record["s3"]["object"]["key"])

        if bucket != BUCKET_NAME:
            raise ValueError("Unexpected bucket")

        print(f"Processing PDF: {key}")

        # Membaca metadata file
        metadata = s3.head_object(
            Bucket=bucket,
            Key=key
        )

        file_size = metadata["ContentLength"]

        # Validasi ukuran file
        if file_size > MAX_FILE_SIZE:
            raise ValueError("PDF exceeds 10 MB limit")

        # Membaca PDF dari S3
        response = s3.get_object(
            Bucket=bucket,
            Key=key
        )

        pdf_content = response["Body"].read()

        # Membaca isi dokumen PDF
        reader = PdfReader(BytesIO(pdf_content))

        if reader.is_encrypted:
            raise ValueError("Encrypted PDF is not supported")

        # Menghitung jumlah halaman
        page_count = len(reader.pages)

        if page_count < 1 or page_count > MAX_PAGES:
            raise ValueError("Invalid PDF page count")

        # Spesifikasi dummy untuk pengujian
        paper_size = "A4"
        print_type = "BW"
        copies = 1
        price_per_page = 500

        # Menghitung estimasi biaya
        total_cost = page_count * copies * price_per_page

        result = {
            "fileKey": key,
            "fileSize": file_size,
            "paperSize": paper_size,
            "printType": print_type,
            "copies": copies,
            "pageCount": page_count,
            "pricePerPage": price_per_page,
            "totalCost": total_cost,
            "pdfStatus": "Processed"
        }

        print(json.dumps(result, indent=2))
        results.append(result)

    return {
        "statusCode": 200,
        "body": json.dumps(results)
    }
