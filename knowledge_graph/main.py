"""
Knowledge Graph Generator and Visualizer main module.
"""
import os
import re
import sys
import json
import time
import random
import argparse

# Add the parent directory to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from knowledge_graph.llm import LLM
from knowledge_graph.config import load_config
from knowledge_graph.visualization import visualize_knowledge_graph, sample_data_visualization
from knowledge_graph.text_utils import chunk_text

from knowledge_graph.entity_standardization import (
    standardize_entities,
    infer_relationships,
    limit_predicate_length,
)

from knowledge_graph.prompts import (
    # Pre-KG resolution
    PREKG_ENTITY_RESOLUTION_SYSTEM_PROMPT,
    get_prekg_entity_resolution_user_prompt,
    # Claim extraction
    CLAIM_EXTRACTION_SYSTEM_PROMPT,
    get_claim_extraction_user_prompt,
)

from knowledge_graph.event_extraction import (
    get_events_from_claims,                 # Event identification
    get_event_stats,                        # Used for logging
    infer_within_chunk_event_relations,     # Within-chunk event relation
    get_entity_relations,                   # Entity relations from events
    resolve_events_with_llm,                # Event resolution
    infer_event_relationships               # Event inference
)

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
    llm = LLM(config)
    
    # Pre-KG resolution
    prekg_text = llm(
        PREKG_ENTITY_RESOLUTION_SYSTEM_PROMPT,
        get_prekg_entity_resolution_user_prompt(input_text),
    )
    
    # Claim extraction
    text_claims = llm(
        CLAIM_EXTRACTION_SYSTEM_PROMPT,
        get_claim_extraction_user_prompt(prekg_text),
    )
    
    context_claims = text_claims.strip().split('\n')
    print(f"📝 Extracted {len([c for c in context_claims if c])} claims from chunk")
    
    # FAST MODE: Không delay preventive, chỉ chờ khi gặp lỗi
    # Delay tối thiểu để tránh spam
    time.sleep(0.5)
    
    # Within-chunk event processing
    event_triples = get_events_from_claims(context_claims, config, debug)
    event_triples += infer_within_chunk_event_relations(event_triples, config, debug)
    
    estats = get_event_stats(event_triples)
    print(f">> Extracted {estats['events']} events, {estats['participants']} entities, {estats['locations']} locations, and {estats['times']} time points.")
    
    # Connect entities from events
    print(f">> Extracting entity-entity relations from {estats['participants']} entities...")
    entity_triples = get_entity_relations(prekg_text, event_triples, context_claims, config, debug)
    print(f">> Extracted {len(entity_triples)} entity relations.")

    triples = event_triples + entity_triples
    metadata = {}
    
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
    already_chunked = config.get("chunking", {}).get("already_chunked", False)
    chunk_size = config.get("chunking", {}).get("chunk_size", 500)
    overlap = config.get("chunking", {}).get("overlap", 50)
    
    # Split text into chunks
    text_chunks = chunk_text(full_text, config)
    print(text_chunks)
    chunking_info = f"size: {chunk_size} words, overlap: {overlap} words" if not already_chunked else "pre-chunked"
    print("=" * 50)
    print("PHASE 1: INITIAL EVENT-ENTITY TRIPLE EXTRACTION")
    print("=" * 50)
    print(f"Processing text in {len(text_chunks)} chunks ({chunking_info})")
    print(f"⏱️  Estimated time: ~{len(text_chunks) * 2.5:.0f} minutes (due to API rate limits + server load)")
    print("⚠️  Note: Gemini API may be overloaded at peak hours, please be patient")
    print("=" * 50)
    
    import time
    start_time = time.time()
    
    # Process each chunk from specified index
    next_chunk = config.get("next_chunk", 1)
    os.makedirs("cumulative_output", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    input_name = config.get("input_name", "")
    
    if next_chunk == 1:
        all_results = []
    else:
        with open(f"cumulative_output/{input_name}.chunk-1-to-{next_chunk - 1}.json", "r", encoding="utf-8") as file:
            all_results = json.load(file)
    
    for i, chunk in enumerate(text_chunks):
        chunk_start = time.time()
        print(f"\n{'='*50}")
        print(f"📦 Processing chunk {i + 1}/{len(text_chunks)} ({len(chunk.split())} words)")
        print(f"{'='*50}")
        
        if i + 1 < next_chunk:
            continue
        
        # Process the chunk with LLM
        chunk_results = process_with_llm(config, chunk, debug)
        
        if chunk_results:
            # Add chunk information to each triple
            for item in chunk_results:
                item["chunk"] = i + 1
            
            # Add to overall results
            with open(f"output/{input_name}.chunk-{i + 1}.json", "w", encoding="utf-8") as file:
                json.dump(chunk_results, file, indent=2, ensure_ascii=False)
            all_results.extend(chunk_results)
            
            chunk_time = time.time() - chunk_start
            elapsed_time = time.time() - start_time
            avg_time_per_chunk = elapsed_time / (i + 1)
            remaining_chunks = len(text_chunks) - (i + 1)
            eta = avg_time_per_chunk * remaining_chunks
            
            print(f"✅ Chunk {i + 1} completed: {len(chunk_results)} triples extracted")
            print(f"⏱️  Chunk time: {chunk_time:.1f}s | Total elapsed: {elapsed_time/60:.1f}m | ETA: {eta/60:.1f}m")
            
            with open(f"cumulative_output/{input_name}.chunk-1-to-{i + 1}.json", "w", encoding="utf-8") as file:
                json.dump(all_results, file, indent=2, ensure_ascii=False)
        else:
            print(f"⚠️  Warning: Failed to extract triples from chunk {i + 1}")
    
    print(f"\nExtracted a total of {len(all_results)} triples from all chunks")
    
    # Apply entity standardization if enabled
    if config.get("standardization", {}).get("enabled", False):
        print("Standardization is enabled", config.get("standardization", {}).get("enabled", False))
        
        print("\n" + "="*50)
        print("PHASE 2A: EVENT STANDARDIZATION")
        print("="*50)
        print(f"Starting with {len(all_results)} triples and {len(get_unique_entities(all_results))} unique names")
        all_results = resolve_events_with_llm(all_results, config)
        print(f"After standardization: {len(all_results)} triples and {len(get_unique_entities(all_results))} unique names")
        
        print("\n" + "="*50)
        print("PHASE 2B: ENTITY STANDARDIZATION")
        print("="*50)
        print(f"Starting with {len(all_results)} triples and {len(get_unique_entities(all_results))} unique names")
        all_results = standardize_entities(all_results, config)
        print(f"After standardization: {len(all_results)} triples and {len(get_unique_entities(all_results))} unique names")
    
    # Apply relationship inference if enabled
    if config.get("inference", {}).get("enabled", False):
        print("Inference is enabled", config.get("inference", {}).get("enabled", False))
        
        print("\n" + "="*50)
        print("PHASE 3A: EVENT RELATIONSHIP INFERENCE")
        print("="*50)
        print(f"Starting with {len(all_results)} triples")
        
        # Count existing relationships
        relationship_counts = {}
        for triple in all_results:
            relationship_counts[triple["predicate"]] = relationship_counts.get(triple["predicate"], 0) + 1
        
        print("Top 5 relationship types before inference:")
        for pred, count in sorted(relationship_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f" - {pred}: {count} occurrences")
        
        all_results = infer_event_relationships(all_results, config)
        
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
        
        print("\n" + "="*50)
        print("PHASE 3B: ENTITY RELATIONSHIP INFERENCE")
        print("="*50)
        print(f"Starting with {len(all_results)} triples")
        
        # Count existing relationships
        relationship_counts = {}
        for triple in all_results:
            relationship_counts[triple["predicate"]] = relationship_counts.get(triple["predicate"], 0) + 1
        
        print("Top 5 relationship types before inference:")
        for pred, count in sorted(relationship_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f" - {pred}: {count} occurrences")
        
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
    parser.add_argument('-o', '--output', type=str, default='knowledge_graph.html', help='Output HTML file path')
    parser.add_argument('-i', '--input', type=str, required=False, help='Path to input text file (required unless --test is used)')
    parser.add_argument('--debug', action='store_true', help='Enable debug output (raw LLM responses and extracted JSON)')
    parser.add_argument('--no-standardize', action='store_true', help='Disable entity standardization')
    parser.add_argument('--no-inference', action='store_true', help='Disable relationship inference')
    parser.add_argument('-n', '--next-chunk', type=int, default=1, help="Next chunk to be processed")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    if not config:
        print(f"Failed to load configuration from {args.config}. Exiting.")
        return
    config["next_chunk"] = args.next_chunk
    
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
    
    config["input_name"] = os.path.splitext(args.input)[0]
    if not args.output:
        args.output = f"{config['input_name']}.html"
    
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
    
    # Visualize the knowledge graph
    html_output = config["input_name"] + ".html"
    
    # print(json.dumps(result, indent=2, ensure_ascii=False))
    
    stats = visualize_knowledge_graph(result, html_output, config=config)
    print("\nKnowledge Graph Statistics:")
    print(f"Nodes: {stats['nodes']}")
    print(f"Edges: {stats['edges']}")
    print(f"Communities: {stats['communities']}")
    
    # # Provide command to open the visualization in a browser
    print("\nTo view the visualization, open the following file in your browser:")
    print(f"file://{os.path.abspath(html_output)}".replace('\\', '/'))
    
    out_name = config["input_name"] + ".json"
    
    with open(out_name, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)
    print(f"Stored JSON objects at: {out_name}")


if __name__ == "__main__":
    main()