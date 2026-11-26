# Deployment Plan

Panduan deployment ulang di AWS Academy Cloud Foundations Sandbox (`us-east-1`). Resource Sandbox terhapus ketika sesi berakhir, sehingga langkah ini diulang setiap sesi melalui AWS Console.

Jangan menyimpan Account ID, ARN, Function URL, credentials, atau nilai environment variable di repository.

## Ringkasan konfigurasi Week 12

| Resource | Konfigurasi |
|---|---|
| S3 bucket | General Purpose; Block all public access aktif; ACL disabled (Bucket owner enforced); enkripsi SSE-S3; versioning nonaktif |
| Prefix S3 | `uploads/` untuk PDF, `orders/` untuk data JSON |
| `OrderAPI` | Python 3.11, x86_64, `LabRole`, memory 128 MB, timeout 3 detik, env `BUCKET_NAME` |
| `PDFProcessor` | Python 3.11, x86_64, `LabRole`, memory 256 MB, timeout 30 detik, env `BUCKET_NAME`, paket ZIP |
| Function URL | Untuk `OrderAPI`; auth type `NONE`; invoke mode `BUFFERED` |
| S3 Event Notification | `s3:ObjectCreated:*`, prefix `uploads/`, suffix `.pdf`, tujuan `PDFProcessor` |
| CloudWatch Logs | `/aws/lambda/OrderAPI`, `/aws/lambda/PDFProcessor` |

Semua Lambda memakai handler `lambda_function.lambda_handler`. Pengaturan lain dibiarkan default.

## 1. S3 bucket

1. Buat bucket General Purpose dengan nama unik.
2. Pastikan **Block all public access** aktif dan Object Ownership **Bucket owner enforced**.
3. Buat prefix `uploads/` dan `orders/`.
4. Di **Permissions > CORS**, tempel isi `infrastructure/cors.json`:
   - origin `http://localhost:8000`;
   - method GET dan POST;
   - semua header, dengan expose `ETag`;
   - max age 300 detik.
5. Unggah PDF dummy sebagai `uploads/test.pdf`. PDF tidak disimpan di repository.

## 2. Lambda OrderAPI

1. Buat function `OrderAPI`: Python 3.11, x86_64, existing role `LabRole`.
2. Atur memory 128 MB dan timeout 3 detik, lalu tambahkan environment variable `BUCKET_NAME`.
3. Uji secara bertahap. Untuk setiap kode, tempel ke editor Console, Deploy, lalu jalankan Test.

   | Kode | Event test | Hasil yang diharapkan |
   |---|---|---|
   | `tests/hello_world.py` | `{}` | Status 200 |
   | `tests/test_s3_connection.py` | `{}` | Status 200, dengan `pdfRead`, `jsonWritten`, dan `jsonRead` bernilai `true` |
   | `backend/order_api/lambda_function.py` (starter) | — | Respons `"Printing Order API is running"` |

`test_s3_connection.py` membaca `uploads/test.pdf` serta menulis dan membaca `orders/test-001.json`.

## 3. Lambda Function URL

1. Buka **OrderAPI > Configuration > Function URL**, lalu buat dengan auth type `NONE` dan invoke mode `BUFFERED`.
2. Aktifkan CORS:
   - origin `http://localhost:8000`;
   - method GET dan POST;
   - header `content-type`;
   - max age 300 detik;
   - allow credentials nonaktif.
3. Buka URL di browser. Respons yang diharapkan berisi `"Printing Order API is running"`.
4. **Hapus Function URL setelah pengujian selesai.** Endpoint ini publik dan tidak memiliki autentikasi.

## 4. Lambda PDFProcessor

1. Buat paket ZIP dari root repository (PowerShell). File dependency harus berada di root ZIP, sejajar dengan `lambda_function.py`, bukan di dalam subfolder:

   ```powershell
   Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
   New-Item -ItemType Directory -Force build/pdf_processor
   python -m pip install -r backend/pdf_processor/requirements.txt -t build/pdf_processor
   Copy-Item backend/pdf_processor/lambda_function.py build/pdf_processor/
   Compress-Archive -Path build/pdf_processor/* -DestinationPath build/pdf_processor.zip -Force
   ```

2. Buat function `PDFProcessor`: Python 3.11, x86_64, existing role `LabRole`.
3. Unggah `build/pdf_processor.zip`, atur memory 256 MB dan timeout 30 detik, lalu tambahkan environment variable `BUCKET_NAME`.
4. Buat ulang ZIP setiap kali kode berubah. Folder `build/` tidak masuk repository.

## 5. S3 Event Notification

1. Buka bucket, lalu **Properties > Event notifications > Create event notification**.
2. Pilih event **All object create events**, prefix `uploads/`, suffix `.pdf`, dan tujuan `PDFProcessor`.
3. Unggah PDF ke `uploads/`, lalu periksa log `PDFProcessor` di CloudWatch.

Data JSON disimpan di prefix `orders/`, sehingga tidak memicu event ini kembali.

## 6. CloudWatch Logs

Periksa log group `/aws/lambda/OrderAPI` dan `/aws/lambda/PDFProcessor`. `PDFProcessor` mencatat key objek, jumlah halaman, dan estimasi biaya.

## Batasan Week 12

- `PDFProcessor` masih feasibility test:
  - konfigurasi cetak dummy (A4, BW, 1 salinan, Rp500 per halaman);
  - hasil hanya dicatat ke log, belum memperbarui `orders/{orderId}.json`;
  - PDF tidak valid menghasilkan error, bukan status `Rejected`.
- S3 CORS dan Function URL CORS sudah dikonfigurasi, tetapi belum diuji dengan frontend.
- Presigned POST/GET, frontend, CRUD, dashboard, dan manajemen status pesanan ditunda ke tahap implementasi.

## Sebelum sesi berakhir

- Salin setiap perubahan kode dari Console ke repository lokal.
- Simpan evidence di luar repository, lalu sensor Account ID, ARN, Function URL, dan token.
- Hapus Function URL.
