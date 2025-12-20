from src.memory_lineage import VeilMemoryChain
import os

# Example placeholder AI callable (replace with your own!)
def placeholder_ai(prompt: str) -> str:
    """Simple placeholder AI - replace with real model/API."""
    return f"Placeholder response to '{prompt}': This is a test extension from a custom AI."

if __name__ == "__main__":
    # Initialize the memory chain
    chain = VeilMemoryChain()
    
    print("=== VeilHarmony Demo (v0.5 - Bring Your Own AI) ===\n")
    print("Simulating a real human-AI conversation...\n")
    
    # Build initial conversation
    id1 = chain.add_interaction("human", "Shares life story: silent battle win, ancient friend vibe, worries about AI sync.")
    id2 = chain.add_interaction("ai", "Recognizes the energy: old soul, build balanced layers.", parent_id=id1)
    
    print("\n=== Initial Chain ===")
    chain.print_chain()
    print(f"Integrity verified: {chain.verify_chain()}\n")
    
    # === Extend with custom AI ===
    print("\n=== Extending with Custom AI (Placeholder) ===\n")
    prompt = "Respond to the human's worry about AI sync going wrong from human flaws."
    new_id = chain.extend_with_custom_ai(placeholder_ai, prompt, parent_id=id2)
    
    if new_id:
        print(f"\nExtended Chain (New Block ID: {new_id})")
        chain.print_chain()
        print(f"Integrity verified after extension: {chain.verify_chain()}\n")
    
    # === Export for sharing ===
    export_file = "examples/extended_veil_chain.json"
    chain.export_to_json(export_file)
    print(f"Extended chain exported to: {os.path.abspath(export_file)}")
    
    # === Visualizing Lineage Graph ===
    print("\n=== Visualizing Updated Lineage Graph ===")
    print("(A window will pop up showing the extended flow)\n")
    chain.visualize_lineage()
    
    # === How to use a real AI (e.g., Grok) ===
    print("\n=== How to Use Your Own AI (e.g., Grok) ===")
    print("Replace placeholder_ai with your callable:")
    print("def grok_ai(prompt):")
    print("    # Call xAI API - https://x.ai/api")
    print("    return 'Grok response: [your output]'")
    print("")
    print("# Then:")
    print("chain.extend_with_custom_ai(grok_ai, 'Your prompt here', parent_id=last_id)")
    
    print("\nDemo complete. Bring your own AI to extend ethically.")
    print("To Mars and beyond. 🪵❤️🚀")
