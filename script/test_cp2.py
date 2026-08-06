import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
from core.config import load_settings
from retrieval.index import LocalEmbeddingIndex
from retrieval.agent import build_agent, run_agent_question

def main():
    print("=== 1. Load Settings ===")
    settings = load_settings()
    
    print("=== 2. Build Baseline Index ===")
    # Đọc dữ liệu sạch
    df = pd.read_json(settings.paths.clean_json, orient="records")
    
    # Build collection
    index = LocalEmbeddingIndex.build(df, settings)
    print(f"Index built successfully at: {settings.paths.chroma_dir}")
    print(f"Total documents indexed: {len(index.documents)}")
    
    print("\n=== 3. Test Retrieval (Smoke Test) ===")
    # Chuẩn bị một paper có trong data (ví dụ)
    sample_title = df.iloc[0]["title"]
    
    print(f"\n[Lookup Test] Title: {sample_title}")
    exact_match = index.lookup(sample_title)
    if exact_match:
        print("-> FOUND EXACT MATCH!")
    else:
        print("-> NOT FOUND!")
        
    print(f"\n[Semantic Search Test] Query: 'machine learning'")
    results = index.search("machine learning", top_k=2)
    for r in results:
        print(f" - {r.score:.4f} | {r.title}")
        
    print("\n=== 4. Test Agent ===")
    agent = build_agent(settings, index)
    
    questions = [
        f"Who authored '{sample_title}'?",
        f"When was '{sample_title}' published?"
    ]
    
    for q in questions:
        print(f"\nQ: {q}")
        ans = run_agent_question(agent, q)
        print(f"A: {ans}")

if __name__ == "__main__":
    main()
