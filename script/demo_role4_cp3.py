import sys
from pathlib import Path

# Thêm thư mục src vào sys.path để import
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import json
from core.config import load_settings
from retrieval.index import LocalEmbeddingIndex
from retrieval.agent import build_agent, run_agent_question

def main():
    print("="*60)
    print("ROLE 4 - CHECKPOINT 3 DEMO")
    print("="*60)
    
    settings = load_settings()
    
    # 1. Xác nhận papers-baseline và embedding manifest khớp clean dataset
    print("\n[1] XÁC NHẬN BASELINE & CLEAN DATASET")
    print("-" * 60)
    clean_data_path = settings.paths.clean_json
    try:
        with open(clean_data_path, "r", encoding="utf-8") as f:
            clean_data = [json.loads(line) for line in f if line.strip()]
        clean_ids = set(record["paper_id"] for record in clean_data)
        print(f"-> Đã load {len(clean_data)} records từ {clean_data_path.name}")
    except Exception as e:
        print(f"Lỗi khi đọc clean data: {e}")
        return

    try:
        index = LocalEmbeddingIndex.load(settings)
        index_docs = index.documents
        index_ids = set(doc["paper_id"] for doc in index_docs)
        print(f"-> Đã load {len(index_docs)} documents từ index '{index.collection_name}' (manifest: {settings.paths.embeddings_json.name})")
        
        missing_in_index = clean_ids - index_ids
        missing_in_clean = index_ids - clean_ids
        
        if len(clean_ids) == len(index_ids) and not missing_in_index and not missing_in_clean:
            print("=> THÀNH CÔNG: Dữ liệu index HOÀN TOÀN KHỚP với clean dataset.")
        else:
            print("=> THẤT BẠI: Dữ liệu không khớp!")
            if missing_in_index:
                print(f"   Thiếu {len(missing_in_index)} ID trong index.")
            if missing_in_clean:
                print(f"   Dư {len(missing_in_clean)} ID trong index (không có trong clean).")
    except Exception as e:
        print(f"Lỗi khi load LocalEmbeddingIndex: {e}")
        return

    # 2. Trình bày một semantic search và một exact lookup
    print("\n[2] DEMO SEMANTIC SEARCH & EXACT LOOKUP")
    print("-" * 60)
    
    query = "machine learning in healthcare"
    print(f"* Semantic Search với query: '{query}'")
    try:
        search_results = index.search(query, top_k=2)
        if search_results:
            for i, res in enumerate(search_results, 1):
                print(f"   Kết quả {i}: {res.title} (Score: {res.score:.4f}, ID: {res.paper_id})")
        else:
            print("   Không tìm thấy kết quả semantic search.")
    except Exception as e:
        print(f"Lỗi khi chạy semantic search: {e}")
        
    sample_id = next(iter(index_ids))
    print(f"\n* Exact Lookup với paper_id: '{sample_id}'")
    try:
        lookup_res = index.lookup(sample_id)
        if lookup_res:
            print(f"   Tìm thấy: {lookup_res['title']}")
        else:
            print("   Không tìm thấy bằng exact lookup.")
    except Exception as e:
        print(f"Lỗi khi chạy exact lookup: {e}")
        
    # 3. Kiểm tra agent theo dữ kiện answer dùng tool result, không vượt corpus
    print("\n[3] KIỂM TRA AGENT (RAG)")
    print("-" * 60)
    
    try:
        agent = build_agent(settings, index)
        
        # Test 1: Câu hỏi trong corpus
        if lookup_res:
            test_title = lookup_res['title']
            q_in_corpus = f"Tóm tắt giúp tôi nội dung của bài báo có tiêu đề '{test_title}'."
            print(f"Q (Trong corpus): {q_in_corpus}")
            ans_in = run_agent_question(agent, q_in_corpus)
            print(f"A: {ans_in}\n")
            
        # Test 2: Câu hỏi ngoài corpus
        q_out_corpus = "Ai là tổng thống Mỹ vào năm 2000? Chỉ trả lời dựa vào corpus."
        print(f"Q (Ngoài corpus): {q_out_corpus}")
        ans_out = run_agent_question(agent, q_out_corpus)
        print(f"A: {ans_out}\n")
        
        print("=> Xong phần kiểm tra agent. (Hãy xem log để xác nhận Agent gọi tool và không tự bịa đáp án)")
        
    except Exception as e:
        print(f"Lỗi khi chạy Agent: {e}")

if __name__ == "__main__":
    main()
