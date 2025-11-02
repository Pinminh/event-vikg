"""
Event extraction and processing module for hybrid entity-event knowledge graphs.
This module handles extraction of events, their attributes, duration, and inter-event relations.
"""

from src.knowledge_graph.llm import call_llm, extract_json_from_text
from src.knowledge_graph.event_prompts import (
    EVENT_EXTRACTION_SYSTEM_PROMPT,
    get_event_extraction_user_prompt,
    EVENT_ATTRIBUTE_SYSTEM_PROMPT,
    get_event_attribute_user_prompt,
    EVENT_DURATION_SYSTEM_PROMPT,
    get_event_duration_user_prompt,
    EVENT_RELATION_SYSTEM_PROMPT,
    get_event_relation_user_prompt
)
import time
import random


def extract_events_from_claims(claims, config, debug=False):
    """
    Extract events from a list of claims.
    
    Args:
        claims: List of claim strings
        config: Configuration dictionary
        debug: If True, print detailed debug information
        
    Returns:
        List of event dictionaries with 'event_id', 'event_type', 'description', 'participants', 'claim'
    """
    if not claims:
        return []
    
    print(f"\n{'='*50}")
    print("STAGE 1: EVENT EXTRACTION")
    print(f"{'='*50}")
    print(f"Extracting events from {len(claims)} claims...")
    
    # LLM configuration
    model = config["llm"]["model"]
    api_key = config["llm"]["api_key"]
    max_tokens = config["llm"]["max_tokens"]
    temperature = config["llm"]["temperature"]
    base_url = config["llm"]["base_url"]
    
    all_events = []
    event_counter = 0
    
    # Process claims in batches to reduce API calls
    batch_size = config.get("event_extraction", {}).get("batch_size", 5)
    
    for batch_start in range(0, len(claims), batch_size):
        batch_end = min(batch_start + batch_size, len(claims))
        batch_claims = claims[batch_start:batch_end]
        
        # Join claims for batch processing
        claims_text = "\n".join([f"{i+1}. {claim}" for i, claim in enumerate(batch_claims)])
        
        print(f"\n📦 Processing claims batch {batch_start//batch_size + 1}/{(len(claims)-1)//batch_size + 1}")
        
        # Add delay between batches to avoid rate limits
        if batch_start > 0:
            delay = random.uniform(4.0, 6.0)
            time.sleep(delay)
        
        # Prepare prompt
        system_prompt = EVENT_EXTRACTION_SYSTEM_PROMPT
        user_prompt = get_event_extraction_user_prompt(claims_text)
        
        try:
            # Call LLM
            response = call_llm(model, user_prompt, api_key, system_prompt, max_tokens, temperature, base_url)
            
            # Extract JSON
            events_batch = extract_json_from_text(response)
            
            if events_batch and isinstance(events_batch, list):
                # Assign event IDs and add claim reference
                for event in events_batch:
                    if isinstance(event, dict) and "event_type" in event:
                        event["event_id"] = f"event_{event_counter}"
                        event_counter += 1
                        
                        # Map back to original claim
                        claim_idx = event.get("claim_index", 0)
                        if 0 <= claim_idx < len(batch_claims):
                            event["claim"] = batch_claims[claim_idx]
                        
                        all_events.append(event)
                
                print(f"✅ Extracted {len(events_batch)} events from batch")
            else:
                print(f"⚠️  No events extracted from batch")
        
        except Exception as e:
            print(f"❌ Error extracting events from batch: {e}")
    
    print(f"\n✅ Total events extracted: {len(all_events)}")
    
    if debug and all_events:
        print("\nSample events:")
        for event in all_events[:3]:
            print(f"  - {event.get('event_id')}: {event.get('event_type')} - {event.get('description', '')[:80]}...")
    
    return all_events


def extract_event_attributes(events, config, debug=False):
    """
    Extract detailed attributes (time, location) for events.
    
    Args:
        events: List of event dictionaries
        config: Configuration dictionary
        debug: If True, print detailed debug information
        
    Returns:
        List of event dictionaries enriched with 'time', 'location', and 'time_type' attributes
    """
    if not events:
        return []
    
    print(f"\n{'='*50}")
    print("STAGE 2: EVENT ATTRIBUTE EXTRACTION")
    print(f"{'='*50}")
    print(f"Extracting attributes for {len(events)} events...")
    
    # LLM configuration
    model = config["llm"]["model"]
    api_key = config["llm"]["api_key"]
    max_tokens = config["llm"]["max_tokens"]
    temperature = config["llm"]["temperature"]
    base_url = config["llm"]["base_url"]
    
    enriched_events = []
    
    # Process events individually for accurate attribute extraction
    for i, event in enumerate(events):
        print(f"\n🔍 Processing event {i+1}/{len(events)}: {event.get('event_id')}")
        
        # Add delay to avoid rate limits
        if i > 0:
            delay = random.uniform(4.0, 6.0)
            time.sleep(delay)
        
        # Prepare event context
        event_context = f"""
Event ID: {event.get('event_id')}
Event Type: {event.get('event_type')}
Description: {event.get('description')}
Participants: {event.get('participants', [])}
Source Claim: {event.get('claim', '')}
"""
        
        # Prepare prompt
        system_prompt = EVENT_ATTRIBUTE_SYSTEM_PROMPT
        user_prompt = get_event_attribute_user_prompt(event_context)
        
        try:
            # Call LLM
            response = call_llm(model, user_prompt, api_key, system_prompt, max_tokens, temperature, base_url)
            
            # Extract JSON
            attributes = extract_json_from_text(response)
            
            if attributes and isinstance(attributes, dict):
                # Enrich event with attributes
                event["time"] = attributes.get("time")
                event["location"] = attributes.get("location")
                event["time_type"] = attributes.get("time_type", "unknown")
                event["time_precision"] = attributes.get("time_precision", "unknown")
                
                print(f"✅ Extracted attributes - Time: {event['time']}, Location: {event['location']}")
            else:
                print(f"⚠️  No attributes extracted")
                event["time"] = None
                event["location"] = None
                event["time_type"] = "unknown"
                event["time_precision"] = "unknown"
            
            enriched_events.append(event)
        
        except Exception as e:
            print(f"❌ Error extracting attributes: {e}")
            event["time"] = None
            event["location"] = None
            event["time_type"] = "unknown"
            event["time_precision"] = "unknown"
            enriched_events.append(event)
    
    print(f"\n✅ Attributes extracted for {len(enriched_events)} events")
    
    return enriched_events


def extract_event_durations(events, config, debug=False):
    """
    Extract duration information for events.
    
    Args:
        events: List of event dictionaries with attributes
        config: Configuration dictionary
        debug: If True, print detailed debug information
        
    Returns:
        List of duration triplets: {'event_id', 'relation_type', 'duration_value', 'reference_event'}
    """
    if not events:
        return []
    
    print(f"\n{'='*50}")
    print("STAGE 3: EVENT DURATION EXTRACTION")
    print(f"{'='*50}")
    print(f"Extracting duration information for {len(events)} events...")
    
    # LLM configuration
    model = config["llm"]["model"]
    api_key = config["llm"]["api_key"]
    max_tokens = config["llm"]["max_tokens"]
    temperature = config["llm"]["temperature"]
    base_url = config["llm"]["base_url"]
    
    all_durations = []
    
    # Prepare events context
    events_context = []
    for event in events:
        event_info = {
            "event_id": event.get("event_id"),
            "event_type": event.get("event_type"),
            "description": event.get("description"),
            "time": event.get("time"),
            "location": event.get("location"),
            "claim": event.get("claim")
        }
        events_context.append(event_info)
    
    # Convert to text
    events_text = "\n".join([
        f"{i+1}. [{e['event_id']}] {e['event_type']}: {e['description']} "
        f"(Time: {e['time']}, Location: {e['location']})"
        for i, e in enumerate(events_context)
    ])
    
    print(f"\n🔍 Analyzing duration for all events...")
    
    # Add delay to avoid rate limits
    time.sleep(random.uniform(4.0, 6.0))
    
    # Prepare prompt
    system_prompt = EVENT_DURATION_SYSTEM_PROMPT
    user_prompt = get_event_duration_user_prompt(events_text)
    
    try:
        # Call LLM
        response = call_llm(model, user_prompt, api_key, system_prompt, max_tokens, temperature, base_url)
        
        # Extract JSON
        durations = extract_json_from_text(response)
        
        if durations and isinstance(durations, list):
            all_durations = [d for d in durations if isinstance(d, dict) and "event_id" in d]
            print(f"✅ Extracted {len(all_durations)} duration relations")
        else:
            print(f"⚠️  No duration relations extracted")
    
    except Exception as e:
        print(f"❌ Error extracting durations: {e}")
    
    if debug and all_durations:
        print("\nSample durations:")
        for dur in all_durations[:3]:
            print(f"  - {dur.get('event_id')}: {dur.get('relation_type')} - {dur.get('duration_value')}")
    
    return all_durations


def extract_event_relations(events, config, debug=False):
    """
    Extract relations between events (PRECEDE, CAUSE, ENABLE, PREVENT, etc.).
    
    Args:
        events: List of event dictionaries with attributes
        config: Configuration dictionary
        debug: If True, print detailed debug information
        
    Returns:
        List of relation triplets: {'source_event', 'relation_type', 'target_event', 'confidence'}
    """
    if not events or len(events) < 2:
        return []
    
    print(f"\n{'='*50}")
    print("STAGE 4: EVENT RELATION EXTRACTION")
    print(f"{'='*50}")
    print(f"Extracting relations between {len(events)} events...")
    
    # LLM configuration
    model = config["llm"]["model"]
    api_key = config["llm"]["api_key"]
    max_tokens = config["llm"]["max_tokens"]
    temperature = config["llm"]["temperature"]
    base_url = config["llm"]["base_url"]
    
    all_relations = []
    
    # Prepare events context
    events_context = []
    for event in events:
        event_info = {
            "event_id": event.get("event_id"),
            "event_type": event.get("event_type"),
            "description": event.get("description"),
            "participants": event.get("participants", []),
            "time": event.get("time"),
            "location": event.get("location"),
            "claim": event.get("claim")
        }
        events_context.append(event_info)
    
    # Convert to text
    events_text = "\n".join([
        f"{i+1}. [{e['event_id']}] {e['event_type']}: {e['description']}\n"
        f"   Participants: {', '.join(e['participants']) if e['participants'] else 'None'}\n"
        f"   Time: {e['time']}, Location: {e['location']}\n"
        f"   Source: \"{e['claim'][:100]}...\""
        for i, e in enumerate(events_context)
    ])
    
    print(f"\n🔍 Analyzing relations between events...")
    
    # Add delay to avoid rate limits
    time.sleep(random.uniform(4.0, 6.0))
    
    # Prepare prompt
    system_prompt = EVENT_RELATION_SYSTEM_PROMPT
    user_prompt = get_event_relation_user_prompt(events_text)
    
    try:
        # Call LLM
        response = call_llm(model, user_prompt, api_key, system_prompt, max_tokens, temperature, base_url)
        
        # Extract JSON
        relations = extract_json_from_text(response)
        
        if relations and isinstance(relations, list):
            # Validate relations
            valid_event_ids = {e.get("event_id") for e in events}
            all_relations = []
            
            for rel in relations:
                if isinstance(rel, dict) and "source_event" in rel and "target_event" in rel:
                    # Check if events exist
                    if rel["source_event"] in valid_event_ids and rel["target_event"] in valid_event_ids:
                        # Avoid self-referencing relations
                        if rel["source_event"] != rel["target_event"]:
                            all_relations.append(rel)
            
            print(f"✅ Extracted {len(all_relations)} event relations")
        else:
            print(f"⚠️  No event relations extracted")
    
    except Exception as e:
        print(f"❌ Error extracting event relations: {e}")
    
    if debug and all_relations:
        print("\nSample event relations:")
        for rel in all_relations[:5]:
            print(f"  - {rel.get('source_event')} --[{rel.get('relation_type')}]--> {rel.get('target_event')}")
    
    return all_relations


def process_event_extraction_pipeline(claims, config, debug=False):
    """
    Complete pipeline for event extraction: events, attributes, durations, and relations.
    
    Args:
        claims: List of claim strings
        config: Configuration dictionary
        debug: If True, print detailed debug information
        
    Returns:
        Dictionary containing:
        - 'events': List of event dictionaries
        - 'durations': List of duration triplets
        - 'relations': List of relation triplets
    """
    print(f"\n{'='*50}")
    print("EVENT EXTRACTION PIPELINE")
    print(f"{'='*50}")
    print(f"Starting event extraction from {len(claims)} claims...")
    
    # Stage 1: Extract events
    events = extract_events_from_claims(claims, config, debug)
    
    if not events:
        print("\n⚠️  No events extracted. Skipping remaining stages.")
        return {
            "events": [],
            "durations": [],
            "relations": []
        }
    
    # Stage 2: Extract event attributes
    events_with_attributes = extract_event_attributes(events, config, debug)
    
    # Stage 3: Extract event durations
    durations = extract_event_durations(events_with_attributes, config, debug)
    
    # Stage 4: Extract event relations
    relations = extract_event_relations(events_with_attributes, config, debug)
    
    print(f"\n{'='*50}")
    print("EVENT EXTRACTION PIPELINE COMPLETE")
    print(f"{'='*50}")
    print(f"✅ Extracted {len(events_with_attributes)} events")
    print(f"✅ Extracted {len(durations)} duration relations")
    print(f"✅ Extracted {len(relations)} event relations")
    
    return {
        "events": events_with_attributes,
        "durations": durations,
        "relations": relations
    }