import sys
import shutil
from pathlib import Path

# Thêm thư mục src vào sys.path để import
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import json
import pandas as pd
from core.config import load_settings
from retrieval.index import LocalEmbeddingIndex
from retrieval.agent import build_agent, run_agent_question

def run_checkpoint_6_demo():
    print("=" * 60)
    print("ROLE 4 - CHECKPOINT 6 DEMO (REPAIR)")
    print("=" * 60)
    print()

    settings = load_settings()
    
    repaired_data_path = settings.paths.repaired_clean_json
    
    if not repaired_data_path.exists():
        print(f"File {repaired_data_path.name} không tồn tại. Tạm thời copy từ papers_clean.json để mô phỏng...")
        shutil.copy2(settings.paths.clean_json, repaired_data_path)

    # 1. TẠO INDEX REPAIRED
    print("[1] XÂY DỰNG INDEX TỪ DỮ LIỆU ĐÃ SỬA CHỮA (REPAIRED)")
    print("-" * 60)
    
    try:
        df_repaired = pd.read_json(repaired_data_path, lines=True)
        print(f"-> Đã load {len(df_repaired)} records từ {repaired_data_path.name}")
        
        print(f"-> Đang build collection '{settings.repaired_collection_name}'...")
        repaired_index = LocalEmbeddingIndex.build(
            settings=settings,
            df=df_repaired,
            embeddings_output_path=settings.paths.repaired_embeddings_json
        )
        print(f"=> THÀNH CÔNG: Đã tạo index repaired với {len(repaired_index.documents)} documents.")
    except Exception as e:
        print(f"=> LỖI: {e}")
        return
        
    print("\n[2] KIỂM TRA CHỨC NĂNG SEMANTIC SEARCH & AGENT (TRÊN TẬP REPAIRED)")
    print("-" * 60)
    query = "machine learning in healthcare"
    print(f"* Semantic Search với query: '{query}'")
    try:
        results = repaired_index.search(query, top_k=2)
        for i, res in enumerate(results):
            print(f"   Kết quả {i+1}: {res['title']} (Score: {res['score']:.4f}, ID: {res['paper_id']})")
    except Exception as e:
        print(f"   -> Search lỗi: {e}")
        
    print("\n* Hỏi Agent (Câu hỏi trong corpus baseline)")
    agent_query = "Tóm tắt giúp tôi nội dung của bài báo có tiêu đề '0346 Retrieval Augmented Generation Improves Large Language Model Performance in Sleep Medicine'."
    print(f"Q: {agent_query}")
    try:
        agent = build_agent(settings, repaired_index)
        answer = run_agent_question(agent, agent_query)
        print(f"A: {answer}")
    except Exception as e:
        print(f"   -> Agent lỗi: {e}")

    print("\n[3] CHỨNG MINH 3 COLLECTIONS/PATHS TÁCH BIỆT")
    print("-" * 60)
    import chromadb
    client = chromadb.PersistentClient(path=str(settings.paths.chroma_dir))
    collections = client.list_collections()
    
    print("Danh sách Collections hiện có trong ChromaDB:")
    for c in collections:
        print(f"  - {c.name}")
        
    print("\nDanh sách Manifest (Embeddings JSON) trong ổ đĩa:")
    paths = [
        settings.paths.embeddings_json,
        settings.paths.corrupted_embeddings_json,
        settings.paths.repaired_embeddings_json
    ]
    for p in paths:
        status = "TỒN TẠI" if p.exists() else "KHÔNG TỒN TẠI"
        print(f"  - {p.name}: {status}")

if __name__ == "__main__":
    run_checkpoint_6_demo()
