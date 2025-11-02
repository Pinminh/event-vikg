"""
Knowledge Graph Generator and Visualizer main module.
"""
import argparse
import json
import os
import sys
import re

# Add the parent directory to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.knowledge_graph.config import load_config
from src.knowledge_graph.llm import call_llm, extract_json_from_text
from src.knowledge_graph.visualization import visualize_knowledge_graph, sample_data_visualization
from src.knowledge_graph.text_utils import chunk_text
from src.knowledge_graph.entity_standardization import standardize_entities, infer_relationships, limit_predicate_length
from src.knowledge_graph.prompts import MAIN_SYSTEM_PROMPT, MAIN_USER_PROMPT
from src.knowledge_graph.prompts import CLAIM_EXTRACTION_SYSTEM_PROMPT, get_claim_extraction_user_prompt
from src.knowledge_graph.prompts import PREKG_ENTITY_RESOLUTION_SYSTEM_PROMPT, get_prekg_entity_resolution_user_prompt

def process_with_llm(config, input_text, debug=False):
    """
    Process input text with LLM to extract triples.
    
    Args:
        config: Configuration dictionary
        input_text: Text to analyze
        debug: If True, print detailed debug information
        
    Returns:
        List of extracted triples or None if processing failed
    """
    
    # LLM configuration
    model = config["llm"]["model"]
    api_key = config["llm"]["api_key"]
    max_tokens = config["llm"]["max_tokens"]
    temperature = config["llm"]["temperature"]
    base_url = config["llm"]["base_url"]
    
    # Use prompts from the prompts module
    system_prompt = MAIN_SYSTEM_PROMPT
    user_prompt = MAIN_USER_PROMPT
    
    import time
    import random
    
    # Entity resolution + Entity filling
    prekg_resolution_system_prompt = PREKG_ENTITY_RESOLUTION_SYSTEM_PROMPT
    prekg_resolution_user_prompt = get_prekg_entity_resolution_user_prompt(input_text)
    prekg_response = call_llm(model, prekg_resolution_user_prompt, api_key, prekg_resolution_system_prompt, max_tokens, temperature, base_url)
    
    # Claim extraction
    claim_system_prompt = CLAIM_EXTRACTION_SYSTEM_PROMPT
    claim_user_prompt = get_claim_extraction_user_prompt(prekg_response)
    extracting_claims_response = call_llm(model, claim_user_prompt, api_key, claim_system_prompt, max_tokens, temperature, base_url)
    
    context_claims = extracting_claims_response.split('\n')
    print(f"📝 Extracted {len([c for c in context_claims if c])} claims from chunk")
    
    # FAST MODE: Không delay preventive, chỉ chờ khi gặp lỗi
    # Delay tối thiểu để tránh spam
    time.sleep(0.5)

    triples = []
    metadata = {}
    
    claim_index = 0
    total_claims = len([c for c in context_claims if c])
    
    for i, claim in enumerate(context_claims):
        if claim == "":
            continue
        
        claim_index += 1
        print(f"\n🔍 Processing claim {claim_index}/{total_claims}...")
        print(claim)
        
        # Thêm delay giữa các API calls để tránh rate limit và server overload
        if claim_index > 1:
            base_delay = 5.0  # Tăng từ 4.5s lên 5s (12 req/min)
            jitter = random.uniform(0, 1.0)  # Random 0-1s
            time.sleep(base_delay + jitter)
            
        extract_triplete_prompt = user_prompt + f"```{claim}```"
        triplets_response = call_llm(model, extract_triplete_prompt, api_key, system_prompt, max_tokens, temperature, base_url)
        result = extract_json_from_text(triplets_response)
        
        if result:
            print(f"✅ Found {len(result)} triples")
            for item in result:
                item["claim"] = claim
            triples.extend(result)
        else:
            print(f"⚠️  No triples found")

    print(triples)
    
    # Validate and filter triples to ensure they have all required fields
    valid_triples = []
    invalid_count = 0
    
    for item in triples:
        if isinstance(item, dict) and "subject" in item and "predicate" in item and "object" in item:
            # Add metadata to valid items
            valid_triples.append(dict(item, **metadata))
        else:
            invalid_count += 1
    
    if invalid_count > 0:
        print(f"Warning: Filtered out {invalid_count} invalid triples missing required fields")
    
    if not valid_triples:
        print("Error: No valid triples found in LLM response")
        return None
    
    # Apply predicate length limit to all valid triples
    for triple in valid_triples:
        triple["predicate"] = limit_predicate_length(triple["predicate"])
    
    # Print extracted JSON only if debug mode is on
    if debug:
        print("Extracted JSON:")
        print(json.dumps(valid_triples, indent=2))  # Pretty print the JSON
    
    return valid_triples

def process_text_in_chunks(config, full_text, debug=False):
    """
    Process a large text by breaking it into chunks with overlap,
    and then processing each chunk separately.
    
    Args:
        config: Configuration dictionary
        full_text: The complete text to process
        debug: If True, print detailed debug information
    
    Returns:
        List of all extracted triples from all chunks
    """
    # Get chunking parameters from config
    chunk_size = config.get("chunking", {}).get("chunk_size", 500)
    overlap = config.get("chunking", {}).get("overlap", 50)
    
    # Split text into chunks
    text_chunks = chunk_text(full_text, chunk_size, overlap)
    print(text_chunks)
    
    print("=" * 50)
    print("PHASE 1: INITIAL TRIPLE EXTRACTION")
    print("=" * 50)
    print(f"Processing text in {len(text_chunks)} chunks (size: {chunk_size} words, overlap: {overlap} words)")
    print(f"⏱️  Estimated time: ~{len(text_chunks) * 2.5:.0f} minutes (due to API rate limits + server load)")
    print("⚠️  Note: Gemini API may be overloaded at peak hours, please be patient")
    print("=" * 50)
    
    import time
    start_time = time.time()
    
    # Process each chunk
    latest_chunk = 13
    
    with open(f"output/chunk-1-to-{latest_chunk - 1}.json", "r") as file:
        all_results = json.load(file)
    
    for i, chunk in enumerate(text_chunks):
        chunk_start = time.time()
        print(f"\n{'='*50}")
        print(f"📦 Processing chunk {i+1}/{len(text_chunks)} ({len(chunk.split())} words)")
        print(f"{'='*50}")
        
        if i + 1 < latest_chunk:
            continue
        
        # Process the chunk with LLM
        chunk_results = process_with_llm(config, chunk, debug)
        
        if chunk_results:
            # Add chunk information to each triple
            for item in chunk_results:
                item["chunk"] = i + 1
            
            # Add to overall results
            all_results.extend(chunk_results)
            
            chunk_time = time.time() - chunk_start
            elapsed_time = time.time() - start_time
            avg_time_per_chunk = elapsed_time / (i + 1)
            remaining_chunks = len(text_chunks) - (i + 1)
            eta = avg_time_per_chunk * remaining_chunks
            
            print(f"✅ Chunk {i+1} completed: {len(chunk_results)} triples extracted")
            print(f"⏱️  Chunk time: {chunk_time:.1f}s | Total elapsed: {elapsed_time/60:.1f}m | ETA: {eta/60:.1f}m")
            
            with open(f"output/chunk-1-to-{i + 1}.json", "w") as file:
                json.dump(all_results, file, indent=2)
        else:
            print(f"⚠️  Warning: Failed to extract triples from chunk {i+1}")
    
    print(f"\nExtracted a total of {len(all_results)} triples from all chunks")
    
    # Apply entity standardization if enabled
    if config.get("standardization", {}).get("enabled", False):
        print("Standardization is enabled", config.get("standardization", {}).get("enabled", False))
        print("\n" + "="*50)
        print("PHASE 2: ENTITY STANDARDIZATION")
        print("="*50)
        print(f"Starting with {len(all_results)} triples and {len(get_unique_entities(all_results))} unique entities")
        
        all_results = standardize_entities(all_results, config)
        
        print(f"After standardization: {len(all_results)} triples and {len(get_unique_entities(all_results))} unique entities")
    
    # Apply relationship inference if enabled
    if config.get("inference", {}).get("enabled", False):
        print("Inference is enabled", config.get("inference", {}).get("enabled", False))
        print("\n" + "="*50)
        print("PHASE 3: RELATIONSHIP INFERENCE")
        print("="*50)
        print(f"Starting with {len(all_results)} triples")
        
        # Count existing relationships
        relationship_counts = {}
        for triple in all_results:
            relationship_counts[triple["predicate"]] = relationship_counts.get(triple["predicate"], 0) + 1
        
        print("Top 5 relationship types before inference:")
        for pred, count in sorted(relationship_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {pred}: {count} occurrences")
        
        all_results = infer_relationships(all_results, config)
        
        # Count relationships after inference
        relationship_counts_after = {}
        for triple in all_results:
            relationship_counts_after[triple["predicate"]] = relationship_counts_after.get(triple["predicate"], 0) + 1
        
        print("\nTop 5 relationship types after inference:")
        for pred, count in sorted(relationship_counts_after.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {pred}: {count} occurrences")
        
        # Count inferred relationships
        inferred_count = sum(1 for triple in all_results if triple.get("inferred", False))
        print(f"\nAdded {inferred_count} inferred relationships")
        print(f"Final knowledge graph: {len(all_results)} triples")
    
    return all_results

def get_unique_entities(triples):
    """
    Get the set of unique entities from the triples.
    
    Args:
        triples: List of triple dictionaries
        
    Returns:
        Set of unique entity names
    """
    entities = set()
    for triple in triples:
        if not isinstance(triple, dict):
            continue
        if "subject" in triple:
            entities.add(triple["subject"])
        if "object" in triple:
            entities.add(triple["object"])
    return entities

def main():
    """Main entry point for the knowledge graph generator."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Knowledge Graph Generator and Visualizer')
    parser.add_argument('--test', action='store_true', help='Generate a test visualization with sample data')
    parser.add_argument('--config', type=str, default='config.toml', help='Path to configuration file')
    parser.add_argument('--output', type=str, default='knowledge_graph.html', help='Output HTML file path')
    parser.add_argument('--input', type=str, required=False, help='Path to input text file (required unless --test is used)')
    parser.add_argument('--debug', action='store_true', help='Enable debug output (raw LLM responses and extracted JSON)')
    parser.add_argument('--no-standardize', action='store_true', help='Disable entity standardization')
    parser.add_argument('--no-inference', action='store_true', help='Disable relationship inference')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    if not config:
        print(f"Failed to load configuration from {args.config}. Exiting.")
        return
    
    # If test flag is provided, generate a sample visualization
    if args.test:
        print("Generating sample data visualization...")
        sample_data_visualization(args.output, config=config)
        print(f"\nSample visualization saved to {args.output}")
        print(f"To view the visualization, open the following file in your browser:")
        print(f"file://{os.path.abspath(args.output)}")
        return
    
    # For normal processing, input file is required
    if not args.input:
        print("Error: --input is required unless --test is used")
        parser.print_help()
        return
    
    # Override configuration settings with command line arguments
    if args.no_standardize:
        config.setdefault("standardization", {})["enabled"] = False
    if args.no_inference:
        config.setdefault("inference", {})["enabled"] = False
    
    # Load input text from file
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            input_text = f.read()
        print(f"Using input text from file: {args.input}")
    except Exception as e:
        print(f"Error reading input file {args.input}: {e}")
        return
    
    result = process_text_in_chunks(config, input_text, args.debug)

    try:
        with open(f"response.json", 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Saved raw knowledge graph data to response.json")
    except Exception as e:
        print(f"Warning: Could not save raw data to response.json: {e}")
    
    # Visualize the knowledge graph
    stats = visualize_knowledge_graph(result, args.output, config=config)
    print("\nKnowledge Graph Statistics:")
    print(f"Nodes: {stats['nodes']}")
    print(f"Edges: {stats['edges']}")
    print(f"Communities: {stats['communities']}")
    
    # Provide command to open the visualization in a browser
    print("\nTo view the visualization, open the following file in your browser:")
    print(f"file://{os.path.abspath(args.output)}")
    
    out_name = args.output.split(".")[:-1]
    out_name = ".".join(out_name) + ".json"
    
    with open(out_name, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2)
    print(f"Stored JSON objects at: {out_name}")

    # import pandas as pd
    # df = pd.read_csv("data/intrinsic_vihallu.csv")
    # i = 1
    # for row in df.itertuples():
    #     input_text = f"context: {row.context}\nprompt: {row.prompt}\nresponse: {row.response}"
    #     # Process text in chunks
    #     result = process_text_in_chunks(config, input_text, args.debug)
        
    #     if result:
    #         os.makedirs(f"output/{i}", exist_ok=True)
    #         # Save the raw data as JSON for potential reuse
    #         context_result = [item for item in result if item.get("part") == "context"]
    #         response_result = [item for item in result if item.get("part") == "response"]
    #         try:
    #             with open(f"output/{i}/context.json", 'w', encoding='utf-8') as f:
    #                 json.dump(context_result, f, indent=2, ensure_ascii=False)
    #             print(f"Saved raw knowledge graph data to output/{i}/context.json")
    #         except Exception as e:
    #             print(f"Warning: Could not save raw data to output/{i}/context.json: {e}")

    #         try:
    #             with open(f"output/{i}/response.json", 'w', encoding='utf-8') as f:
    #                 json.dump(response_result, f, indent=2, ensure_ascii=False)
    #             print(f"Saved raw knowledge graph data to output/{i}/response.json")
    #         except Exception as e:
    #             print(f"Warning: Could not save raw data to output/{i}/response.json: {e}")
            
    #         # Visualize the knowledge graph
    #         # stats = visualize_knowledge_graph(result, args.output, config=config)
    #         # print("\nKnowledge Graph Statistics:")
    #         # print(f"Nodes: {stats['nodes']}")
    #         # print(f"Edges: {stats['edges']}")
    #         # print(f"Communities: {stats['communities']}")
            
    #         # Provide command to open the visualization in a browser
    #         print("\nTo view the visualization, open the following file in your browser:")
    #         print(f"file://{os.path.abspath(args.output)}")
    #     else:
    #         print("Knowledge graph generation failed due to errors in LLM processing.")
    #     print('Done with', i)
    #     i += 1
if __name__ == "__main__":
    main() 