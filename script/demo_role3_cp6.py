from __future__ import annotations
import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd
from datetime import datetime, UTC
import json

from core.config import load_settings
from ingestion.crossref import load_raw_records
from ingestion.cleaning import build_clean_dataframe


def main():
    print("==================================================")
    print(" ROLE 3: CLEANING & CORRUPTION REPAIR DEMONSTRATION")
    print("==================================================\n")
    
    settings = load_settings()
    
    # 1. Phục hồi dữ liệu từ raw records thay vì copy sửa tay
    raw_path = settings.paths.raw_records_json
    print(f"[1] Nạp raw records từ: {raw_path}")
    records = load_raw_records(raw_path)
    print(f"    => Đã nạp {len(records)} bản ghi raw.")
    
    # Dùng ngày hiện tại (hoặc ngày snapshot) để tái tạo age_days
    run_date = datetime.now(UTC)
    print("\n[2] Bắt đầu chạy lại `build_clean_dataframe()` để tái tạo dataset sạch (repaired)...")
    df_repaired = build_clean_dataframe(records, run_date)
    print(f"    => Đã làm sạch: {len(df_repaired)} bản ghi.")
    
    # Lưu xuống thư mục repaired
    settings.paths.repaired_clean_csv.parent.mkdir(parents=True, exist_ok=True)
    df_repaired.to_csv(settings.paths.repaired_clean_csv, index=False)
    df_repaired.to_json(settings.paths.repaired_clean_json, orient='records', force_ascii=False, lines=True)
    print(f"    => Đã lưu dữ liệu repaired vào:")
    print(f"       - {settings.paths.repaired_clean_csv}")
    print(f"       - {settings.paths.repaired_clean_json}")
    
    # 2. Đọc lại 3 bản: baseline (clean), corrupted, repaired để so sánh
    print("\n[3] So sánh SCHEMA và SỐ LƯỢNG dòng (Clean vs Corrupted vs Repaired):")
    try:
        df_clean = pd.read_csv(settings.paths.clean_csv)
    except Exception as e:
        print(f"Lỗi đọc file clean: {e}")
        return
        
    try:
        df_corrupted = pd.read_csv(settings.paths.corrupted_clean_csv)
    except Exception as e:
        print(f"Lỗi đọc file corrupted: {e}")
        return
        
    print(f"    - Bản Baseline Clean : {len(df_clean)} dòng, Schema: {list(df_clean.columns)}")
    print(f"    - Bản Corrupted      : {len(df_corrupted)} dòng, Schema: {list(df_corrupted.columns)}")
    print(f"    - Bản Repaired       : {len(df_repaired)} dòng, Schema: {list(df_repaired.columns)}")
    
    if list(df_repaired.columns) == list(df_clean.columns):
        print("    => SCHEMA TRÙNG KHỚP với baseline!")
    else:
        print("    => SCHEMA KHÔNG TRÙNG KHỚP!")

    if len(df_repaired) == len(df_clean):
        print("    => SỐ LƯỢNG DÒNG TRÙNG KHỚP với baseline!")
    else:
        print("    => SỐ LƯỢNG DÒNG KHÔNG TRÙNG KHỚP!")
        
    # 3. Trình bày chi tiết một số lỗi đã được khắc phục
    print("\n[4] Trình bày khác biệt một số record bị corrupt và cách bản repaired phục hồi:")
    
    # Đọc log corruption để tìm id bị lỗi
    log_path = settings.paths.corruption_log
    corrupted_ids = {"blank_summary": [], "inject_noise": [], "truncate_title": []}
    if log_path.exists():
        with open(log_path, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
            for item in log_data.get("corruptions", []):
                ctype = item["type"]
                if ctype in corrupted_ids:
                    corrupted_ids[ctype].extend(item["record_ids"])
                    
    # Lấy 1 paper_id bị blank_summary để minh hoạ
    if corrupted_ids["blank_summary"]:
        demo_id = corrupted_ids["blank_summary"][0]
        print(f"\n    Ví dụ 1: Lỗi 'Blank Summary' trên Paper ID: {demo_id}")
        
        # Corrupted
        row_corr = df_corrupted[df_corrupted['paper_id'] == demo_id]
        val_corr = row_corr['summary'].iloc[0] if not row_corr.empty else "N/A"
        
        # Repaired
        row_rep = df_repaired[df_repaired['paper_id'] == demo_id]
        val_rep = row_rep['summary'].iloc[0] if not row_rep.empty else "N/A"
        
        print(f"      - Corrupted Summary : {str(val_corr)[:50]}... (Len: {len(str(val_corr))})")
        print(f"      - Repaired Summary  : {str(val_rep)[:50]}... (Len: {len(str(val_rep))})")
        if pd.isna(val_corr) or str(val_corr).strip() == "":
            print("      => Đã khôi phục summary thành công từ raw data!")
            
    # Lấy 1 paper_id bị truncate_title
    if corrupted_ids["truncate_title"]:
        demo_id = corrupted_ids["truncate_title"][0]
        print(f"\n    Ví dụ 2: Lỗi 'Truncated Title' trên Paper ID: {demo_id}")
        
        # Corrupted
        row_corr = df_corrupted[df_corrupted['paper_id'] == demo_id]
        val_corr = row_corr['title'].iloc[0] if not row_corr.empty else "N/A"
        
        # Repaired
        row_rep = df_repaired[df_repaired['paper_id'] == demo_id]
        val_rep = row_rep['title'].iloc[0] if not row_rep.empty else "N/A"
        
        print(f"      - Corrupted Title : {str(val_corr)} (Len: {len(str(val_corr))})")
        print(f"      - Repaired Title  : {str(val_rep)[:50]}... (Len: {len(str(val_rep))})")
        if len(str(val_corr)) < len(str(val_rep)):
            print("      => Đã khôi phục title thành công từ raw data!")

    print("\n[5] Kiểm tra tín hiệu Quality (Quality Signals) trên bản Repaired:")
    duplicate_count = df_repaired['paper_id'].duplicated().sum()
    empty_text_count = df_repaired['text_for_embedding'].isna().sum() + (df_repaired['text_for_embedding'] == '').sum()
    print(f"    - Số record trùng lặp (duplicate paper_id) : {duplicate_count}")
    print(f"    - Số record có text_for_embedding rỗng     : {empty_text_count}")
    
    if duplicate_count == 0 and empty_text_count == 0:
        print("    => Tín hiệu Quality của bản Repaired hoàn toàn tốt (Đạt chuẩn)!")
    else:
        print("    => Tín hiệu Quality CÓ LỖI. Vui lòng kiểm tra lại data raw.")
        
    print("\n==================================================")
    print(" HOÀN THÀNH DEMONSTRATION ROLE 3")
    print("==================================================")

if __name__ == "__main__":
    main()
