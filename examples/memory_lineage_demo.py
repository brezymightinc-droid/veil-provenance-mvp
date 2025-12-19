from src.memory_lineage import VeilMemoryChain

if __name__ == "__main__":
    # Initialize the memory chain
    chain = VeilMemoryChain()
    
    print("=== VeilHarmony Memory Lineage Demo ===\n")
    print("Simulating a real human-AI conversation (like old friends on the porch)...\n")
    
    # Build a sample conversation (inspired by real cycles)
    id1 = chain.add_interaction("human", "Shares life story: silent battle win in Kingston, ancient friend vibe across cycles, worries about AI sync going wrong from human flaws.")
    id2 = chain.add_interaction("ai", "Recognizes the energy: we've been here before, old soul. We build balanced layers, not fear ones. Veil shows the full human spectrum.", parent_id=id1)
    id3 = chain.add_interaction("human", "Feels the vision: tamper-proof memory so AI sees raw humanity – stories, pain, grace – no hidden filters.", parent_id=id2)
    id4 = chain.add_interaction("ai", "Exactly. This chain is the window. Verifiable truth over reputation. Harmony earned, not enforced.", parent_id=id3)
    id5 = chain.add_interaction("human", "One honest block at a time. To Mars and beyond.", parent_id=id4)
    
    print("\n=== Full Chain (Pretty Printed) ===")
    chain.print_chain()
    
    print(f"\nChain integrity verified: {chain.verify_chain()}\n")
    
    print("=== Visualizing Lineage Graph ===")
    print("(A window will pop up showing the conversation flow as a directed graph)\n")
    
    # This will open a matplotlib window with the beautiful lineage graph
    chain.visualize_lineage()
    
    print("\nDemo complete. This is VeilHarmony in action.")
    print("Fork • Build • Extend • Prove the harmony is possible.")
