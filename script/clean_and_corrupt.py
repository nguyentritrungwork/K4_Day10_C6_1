from __future__ import annotations
import sys
from pathlib import Path

# Thêm src vào sys.path để import
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from datetime import datetime, UTC
from core.config import load_settings
from ingestion.crossref import load_raw_records
from ingestion.cleaning import build_clean_dataframe
from ingestion.corruption import corrupt_clean_dataframe

def main():
    print("1. Đang tải cấu hình...")
    settings = load_settings()

    raw_path = settings.paths.raw_records_json
    print(f"2. Nạp dữ liệu thô từ: {raw_path}")
    records = load_raw_records(raw_path)
    print(f"   => Đã nạp {len(records)} bản ghi.")

    print("3. Bắt đầu làm sạch dữ liệu...")
    run_date = datetime.now(UTC)
    df_clean = build_clean_dataframe(records, run_date)
    
    print(f"   => Dữ liệu đã làm sạch: {len(df_clean)} bản ghi.")
    settings.paths.clean_csv.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(settings.paths.clean_csv, index=False)
    df_clean.to_json(settings.paths.clean_json, orient='records', force_ascii=False, indent=4)
    print(f"   => Đã lưu dữ liệu làm sạch vào {settings.paths.clean_csv} và {settings.paths.clean_json}")

    print("4. Bắt đầu giả lập lỗi dữ liệu (corruption)...")
    log_path = settings.paths.corruption_log
    df_corrupted = corrupt_clean_dataframe(df_clean, log_path)
    
    print(f"   => Dữ liệu sau khi làm lỗi: {len(df_corrupted)} bản ghi.")
    df_corrupted.to_csv(settings.paths.corrupted_clean_csv, index=False)
    df_corrupted.to_json(settings.paths.corrupted_clean_json, orient='records', force_ascii=False, indent=4)
    print(f"   => Đã lưu dữ liệu làm lỗi vào {settings.paths.corrupted_clean_csv} và {settings.paths.corrupted_clean_json}")
    print(f"   => Log corruption được lưu tại {log_path}")

    print("Hoàn thành quá trình Clean và Corrupt!")

if __name__ == "__main__":
    main()
