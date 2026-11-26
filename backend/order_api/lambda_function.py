"""OrderAPI - starter code (Week 12).

Hanya mengembalikan respons HTTP sederhana. CRUD, presigned URL, dan
dashboard adalah fitur Planned dan belum diimplementasikan.
"""

import json


def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "message": "Printing Order API is running",
            "service": "OrderAPI",
            "status": "success",
        }),
    }
