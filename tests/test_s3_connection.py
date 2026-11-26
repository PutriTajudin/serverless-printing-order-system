
import json
import boto3
import os
from datetime import datetime, timezone

s3 = boto3.client('s3')
BUCKET_NAME = os.environ['BUCKET_NAME']

def lambda_handler(event, context):

    # 1. Membaca PDF dari S3
    pdf = s3.get_object(
        Bucket=BUCKET_NAME,
        Key='uploads/test.pdf'
    )

    pdf_content = pdf['Body'].read()

    # 2. Membuat data pesanan dummy
    order = {
        'orderId': 'test-001',
        'customerName': 'Test Customer',
        'fileName': 'test.pdf',
        'fileSize': len(pdf_content),
        'contentType': pdf['ContentType'],
        'paperSize': 'A4',
        'printType': 'BW',
        'copies': 1,
        'pdfStatus': 'WaitingUpload',
        'pageCount': None,
        'totalCost': None,
        'status': 'Pending',
        'createdAt': datetime.now(timezone.utc).isoformat()
    }

    # 3. Menyimpan JSON ke S3
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key='orders/test-001.json',
        Body=json.dumps(order, indent=2),
        ContentType='application/json'
    )

    # 4. Membaca kembali JSON
    result = s3.get_object(
        Bucket=BUCKET_NAME,
        Key='orders/test-001.json'
    )

    saved_order = json.loads(result['Body'].read())

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Lambda-S3 connectivity test successful',
            'bucket': BUCKET_NAME,
            'pdfRead': True,
            'jsonWritten': True,
            'jsonRead': True,
            'order': saved_order
        })
    }
