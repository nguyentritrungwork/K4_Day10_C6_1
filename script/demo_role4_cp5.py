import sys
from pathlib import Path

# Thêm thư mục src vào sys.path để import
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import json
import pandas as pd
from core.config import load_settings
from retrieval.index import LocalEmbeddingIndex
from retrieval.agent import build_agent, run_agent_question

def main():
    print("="*60)
    print("ROLE 4 - CHECKPOINT 5 DEMO (CORRUPTION)")
    print("="*60)
    
    settings = load_settings()
    
    # 1. Tạo papers-corrupted riêng từ corrupted clean data
    print("\n[1] XÂY DỰNG INDEX TỪ DỮ LIỆU LỖI (CORRUPTED)")
    print("-" * 60)
    corrupted_data_path = settings.paths.corrupted_clean_json
    try:
        df_corrupted = pd.read_json(corrupted_data_path, lines=True)
        print(f"-> Đã load {len(df_corrupted)} records từ {corrupted_data_path.name}")
        
        # Build index, chỉ định output manifest vào corrupted_embeddings_json
        print(f"-> Đang build collection '{settings.corrupted_collection_name}'...")
        corrupted_index = LocalEmbeddingIndex.build(
            df=df_corrupted,
            settings=settings,
            embeddings_output_path=settings.paths.corrupted_embeddings_json
        )
        print(f"=> THÀNH CÔNG: Đã tạo index corrupted với {len(corrupted_index.documents)} documents.")
    except Exception as e:
        print(f"Lỗi khi xử lý corrupted data: {e}")
        return

    # 2. Chạy lại query baseline để quan sát retrieval đổi thế nào
    print("\n[2] ĐỐI CHIẾU SEMANTIC SEARCH, LOOKUP & AGENT (TRÊN TẬP LỖI)")
    print("-" * 60)
    
    query = "machine learning in healthcare"
    print(f"* Semantic Search với query: '{query}'")
    try:
        search_results = corrupted_index.search(query, top_k=2)
        if search_results:
            for i, res in enumerate(search_results, 1):
                print(f"   Kết quả {i}: {res.title} (Score: {res.score:.4f}, ID: {res.paper_id})")
        else:
            print("   Không tìm thấy kết quả semantic search.")
    except Exception as e:
        print(f"Lỗi khi chạy semantic search: {e}")
        
    sample_id = "10-1093-sleep-zsag091-0346"
    print(f"\n* Exact Lookup với paper_id: '{sample_id}' (Đây là sample có ở baseline)")
    try:
        lookup_res = corrupted_index.lookup(sample_id)
        if lookup_res:
            print(f"   Tìm thấy: {lookup_res['title']}")
            print(f"   (Bản báo này có thể đã bị sửa/xóa nội dung nếu nó bị dính lỗi corruption)")
        else:
            print("   Không tìm thấy bài báo này nữa! (Khả năng đã bị xóa trong quá trình corrupt).")
    except Exception as e:
        print(f"Lỗi khi chạy exact lookup: {e}")
        
    print(f"\n* Hỏi Agent (Câu hỏi trong corpus baseline)")
    try:
        agent = build_agent(settings, corrupted_index)
        q_in_corpus = f"Tóm tắt giúp tôi nội dung của bài báo có tiêu đề '0346 Retrieval Augmented Generation Improves Large Language Model Performance in Sleep Medicine'."
        print(f"Q: {q_in_corpus}")
        ans_in = run_agent_question(agent, q_in_corpus)
        print(f"A: {ans_in}\n")
    except Exception as e:
        print(f"Lỗi khi chạy Agent: {e}")

    # 3. Kiểm tra papers-baseline còn đọc được và không bị mutate
    print("\n[3] KIỂM TRA BẢO TOÀN BASELINE")
    print("-" * 60)
    try:
        baseline_index = LocalEmbeddingIndex.load(settings, embeddings_path=settings.paths.embeddings_json)
        print(f"-> Đã load lại baseline từ {settings.paths.embeddings_json.name}")
        print(f"-> Số lượng documents trong baseline: {len(baseline_index.documents)}")
        
        # Test nhẹ semantic search trên baseline
        base_res = baseline_index.search("test", top_k=1)
        if len(base_res) > 0 and len(baseline_index.documents) == 24:
            print("=> THÀNH CÔNG: papers-baseline vẫn NGUYÊN VẸN, không bị mutate bởi bước build lỗi.")
        else:
            print("=> THẤT BẠI: papers-baseline có dấu hiệu bị thay đổi!")
    except Exception as e:
        print(f"Lỗi khi load LocalEmbeddingIndex baseline: {e}")

if __name__ == "__main__":
    main()
