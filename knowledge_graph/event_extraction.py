import json
import time
from pprint import pprint
from tqdm.auto import tqdm
from functools import reduce
from collections import defaultdict
from knowledge_graph.llm import LLM, extract_json_from_text

from knowledge_graph.event_prompts import (
    # Event identification
    EVENT_IDENTIFICATION_SYSTEM_PROMPT,
    get_event_identification_user_prompt,
    # Event attributes
    EVENT_ATTRIBUTE_SYSTEM_PROMPT,
    get_event_attribute_user_prompt,
    # Within-chunk event relations
    WITHIN_CHUNK_EVENT_RELATION_SYSTEM_PROMPT,
    get_within_chunk_event_relation_user_prompt,
    # Event resolution
    EVENT_RESOLUTION_SYSTEM_PROMPT,
    get_event_resolution_user_prompt,
    # Within-community event relations
    WITHIN_COMMUNITY_EVENT_RELATION_SYSTEM_PROMPT,
    get_within_community_event_relation_user_prompt,
    # Between-community event relations
    BETWEEN_COMMUNITY_EVENT_RELATION_SYSTEM_PROMPT,
    get_between_community_event_relation_user_prompt,
    # Entity-entity relations
    ENTITY_RELATION_SYSTEM_PROMPT,
    get_entity_relation_user_prompt,
)


with open("config.json", "r", encoding="utf-8") as file:
    config = json.load(file)

claims = [
    'Vào ngày 17 giờ ngày 26 tháng 4 năm 1975, tại miền Nam Việt Nam, lực lượng của Chiến dịch Hồ Chí Minh bắt đầu mở cuộc tổng công kích từ năm hướng.',
    'Năm hướng bao gồm: Bắc (qua Bình Định – Quảng Ngãi), Tây Bắc (qua Tây Nguyên), Đông Nam (qua Sài Gòn – Gia Định), Đông (qua Cửu Long), và Tây thoại (qua vùng Tây Nam).',
    'Cuộc tổng công kích nhằm vào chính quyền Dinh Độc Lập tại Sài Gòn.',
    'Đúng lúc 11:30 trưa ngày 30 tháng 4 năm 1975, lá cờ Giải phóng tung bay trên nóc Dinh Độc Lập.',
    'Sự kiện lá cờ Giải phóng tung bay trên nóc Dinh Độc Lập đánh dấu sự sụp đổ hoàn toàn chính quyền Việt Nam Cộng Hòa tại Sài Gòn.',
    'Sự kiện lá cờ Giải phóng tung bay trên nóc Dinh Độc Lập kết thúc 30 năm chiến tranh.',
    'Sự kiện lá cờ Giải phóng tung bay trên nóc Dinh Độc Lập chấm dứt chế độ chia cắt đất nước.',
    'Ngày 25 tháng 4 năm 1976, trên toàn quốc diễn ra cuộc Tổng tuyển cử bầu Quốc hội khóa VI cho cả nước thống nhất.',
    'Ngày 2 tháng 7 năm 1976 Quốc hội khóa VI quyết định đổi tên nước thành Cộng hòa xã hội chủ nghĩa Việt Nam.'
]


def get_events_from_claim(target_claim, context_claims, config=config, verbose=False):
    llm = LLM(config)
    text_events = llm(
        EVENT_IDENTIFICATION_SYSTEM_PROMPT,
        get_event_identification_user_prompt(target_claim, context_claims),
    )
    return extract_json_from_text(text_events, verbose)


def get_event_attributes(target_events, target_claim, context_claims, config=config, verbose=False):
    llm = LLM(config)
    text_event_attributes = llm(
        EVENT_ATTRIBUTE_SYSTEM_PROMPT,
        get_event_attribute_user_prompt(target_events, target_claim, context_claims),
    )
    return extract_json_from_text(text_event_attributes, verbose)


def event2triplets(event):
    subject = "EVENT|" + event["description"]
    objects = [f"ENTITY|{p}" for p in event["participants"]]
    participant_triplets = [{"subject": subject, "predicate": "HAS_PARTICIPANT", "object": obj} for obj in objects]

    time_triplet = [{"subject": subject, "predicate": "AT_TIME", "object": "TIME|" + event["time"]}] if event.get("time") else []
    location_triplet = [{"subject": subject, "predicate": "AT_LOCATION", "object": "LOCATION|" + event["location"]}] if event.get("location") else []
    return participant_triplets + time_triplet + location_triplet


def get_events_from_claims(claims, config=config, verbose=False):
    output_events = []
    llm = LLM(config)
    
    for claim in tqdm(claims, desc="Events from Claims"):
        if verbose:
            print(f"Processing claim: {claim}")
        
        text_events = llm(EVENT_IDENTIFICATION_SYSTEM_PROMPT, get_event_identification_user_prompt(claim, claims))
        events = extract_json_from_text(text_events, verbose=False)
        
        if verbose:
            print("="*50)
            pprint(text_events)

        text_attr_events = llm(EVENT_ATTRIBUTE_SYSTEM_PROMPT, get_event_attribute_user_prompt(events, claim, claims))
        attr_events = extract_json_from_text(text_attr_events, verbose)
        
        if verbose:
            print("="*50)
            pprint(text_attr_events)
        
        def accumulate_triplets(acc, event):
            triplets = event2triplets(event)
            for triplet in triplets:
                triplet["claim"] = claim
            return acc + triplets
        output_events += reduce(accumulate_triplets, attr_events, [])
    return output_events


def infer_within_chunk_event_relations(event_triples, config=config, verbose=False):
    llm = LLM(config)
    within_chunk_relations = llm(
        WITHIN_CHUNK_EVENT_RELATION_SYSTEM_PROMPT,
        get_within_chunk_event_relation_user_prompt(event_triples),
    )
    return extract_json_from_text(within_chunk_relations, verbose)


def resolve_events_with_llm(triples, config=config, verbose=False):
    def get_event_content(event):
        if not event or not event.startswith("EVENT"):
            return ""
        return event.split("|")[1]

    # Extract all unique events
    all_events = set()
    for triple in triples:
        if get_event_content(triple["subject"]):
            all_events.add(get_event_content(triple["subject"]))
        if get_event_content(triple["object"]):
            all_events.add(get_event_content(triple["object"]))

    # If there are too many events, limit to the most frequent ones
    event_counts = defaultdict(int)
    for triple in triples:
        if get_event_content(triple["subject"]):
            event_counts[get_event_content(triple["subject"])] += 1
        if get_event_content(triple["object"]):
            event_counts[get_event_content(triple["object"])] += 1
    if len(all_events) > 100:
        # Keep only the top 100 most frequent events
        all_events = {event for event, count in sorted(event_counts.items(), key=lambda x: -x[1])[:100]}

    # Prepare triples context (limit to most relevant ones)
    context_triples = sorted(triples, key=lambda t: event_counts[t["subject"]], reverse=True)[:200]
    def get_event_claim(triplet):
        claim = triplet.get("claim", "")
        return f"(từ nhận định: {claim})" if claim else claim
    
    triple_texts = "\n".join([
        f"- {t['subject']} {t['predicate']} {t['object']} {get_event_claim(t)}"
        for t in context_triples if t["subject"] and t["object"]
    ])
    event_texts = "\n".join(sorted(all_events))

    try:
        # Call LLM to get event resolution mapping
        llm = LLM(config)
        response = llm(
            EVENT_RESOLUTION_SYSTEM_PROMPT,
            get_event_resolution_user_prompt(triple_texts, event_texts),
        )
        event_mapping = extract_json_from_text(response)
        print("Event mapping from LLM:")
        for standard, variants in event_mapping.items():
            print(f"- '{standard}': {variants}")

        if event_mapping and isinstance(event_mapping, dict):
            # Apply the mapping to standardize events
            event_to_standard = {}
            for standard, variants in event_mapping.items():
                for variant in variants:
                    event_to_standard[variant] = standard
                # Also map the standard form to itself
                event_to_standard[standard] = standard

            # Apply standardization to triples
            for triple in triples:
                subj_content, obj_content = get_event_content(triple["subject"]), get_event_content(triple["object"])
                if subj_content:
                    triple["subject"] = "EVENT|" + event_to_standard.get(subj_content, subj_content)
                if obj_content:
                    triple["object"] = "EVENT|" + event_to_standard.get(obj_content, obj_content)

            print(f"Applied LLM-based event standardization for {len(event_mapping)} event groups")
        else:
            print("Could not extract valid event mapping from LLM response")

    except Exception as e:
        print(f"Error in LLM-based event resolution: {e}")

    return triples


def build_event_graph(event_triples):
    event_graph = defaultdict(set)
    all_nodes = set()
    
    for triple in event_triples:
        subj, obj = triple["subject"], triple["object"]
        if subj.startswith("EVENT") and obj.startswith("EVENT"):
            event_graph[subj].add(obj)
            all_nodes.add(subj)
            all_nodes.add(obj)
    
    return event_graph, all_nodes


def identify_event_communities(event_graph):
    # Get all nodes
    all_nodes = set(event_graph.keys()).union(*[event_graph[node] for node in event_graph])

    # Track visited nodes
    visited = set()
    communities = []

    # Depth-first search to find connected components
    def dfs(node, community):
        visited.add(node)
        community.add(node)

        # Visit outgoing edges
        for neighbor in event_graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor, community)

        # Visit incoming edges (we need to check all nodes)
        for source, targets in event_graph.items():
            if node in targets and source not in visited:
                dfs(source, community)

    # Find all communities
    for node in all_nodes:
        if node not in visited:
            community = set()
            dfs(node, community)
            communities.append(community)

    return communities


def infer_within_event_community_relations(triples, communities, config=config, verbose=False):
    new_triples = []
    
    # Process larger communities
    for community in sorted(communities, key=len, reverse=True)[:5]:
        # Skip small communities
        if len(community) < 3:
            continue
            
        # Get all entities in this community
        community_events = list(community)
        
        # Create an adjacency matrix to identify disconnected event pairs
        connections = {(a, b): False for a in community_events for b in community_events if a != b}
        
        # Mark existing connections
        for triple in triples:
            if triple["subject"] in community_events and triple["object"] in community_events:
                connections[(triple["subject"], triple["object"])] = True
        
        # Find disconnected pairs that might be semantically related
        disconnected_pairs = []
        for (a, b), connected in connections.items():
            if not connected and a != b:  # Ensure a and b are different entities
                # Check for potential semantic relationship (e.g., shared words)
                a_words = set(a.lower().split())
                b_words = set(b.lower().split())
                shared_words = a_words.intersection(b_words)
                
                # If they share words or one is contained in the other, they might be related
                if shared_words or a.lower() in b.lower() or b.lower() in a.lower():
                    disconnected_pairs.append((a, b))
        
        # Limit to the most promising pairs
        disconnected_pairs = disconnected_pairs[:10]
        
        if not disconnected_pairs:
            continue
            
        # Get relevant context
        context_triples = []
        entities_of_interest = set()
        for a, b in disconnected_pairs:
            entities_of_interest.add(a)
            entities_of_interest.add(b)
            
        for triple in triples:
            if triple["subject"] in entities_of_interest or triple["object"] in entities_of_interest:
                context_triples.append(triple)
        
        # Limit context size
        if len(context_triples) > 50:
            context_triples = context_triples[:50]
            
        # Convert triples to text for prompt
        triples_text = "\n".join([
            f"{t['subject']} {t['predicate']} {t['object']}"
            for t in context_triples
        ])
        
        # Create pairs text
        pairs_text = "\n".join([f"{a} và {b}" for a, b in disconnected_pairs])
        
        try:
            # Call LLM
            llm = LLM(config)
            response = llm(
                WITHIN_COMMUNITY_EVENT_RELATION_SYSTEM_PROMPT,
                get_within_community_event_relation_user_prompt(pairs_text, triples_text),
            )

            # Extract JSON results
            inferred_triples = extract_json_from_text(response, verbose)
            
            if inferred_triples and isinstance(inferred_triples, list):
                # Mark as inferred and add to new triples
                for triple in inferred_triples:
                    if "subject" in triple and "predicate" in triple and "object" in triple:
                        # Skip self-referencing triples
                        if triple["subject"] == triple["object"]:
                            continue
                        triple["inferred"] = True
                        new_triples.append(triple)
                
                print(f"Inferred {len(inferred_triples)} new event relations within event communities")
            else:
                print("Could not extract valid inferred event relations from LLM response")
        
        except Exception as e:
            print(f"Error in LLM-based event relation inference within event communities: {e}")
    
    return new_triples


def infer_between_event_community_relations(triples, communities, config=config, verbose=False):
    if len(communities) <= 1:
        print("Only one community found, skipping LLM-based relationship inference")
        return []

    # Focus on the largest event communities
    def count_events_in_community(com):
        return len([e for e in com if e.startswith("EVENT")])
    large_communities = sorted(communities, key=count_events_in_community, reverse=True)[:10]

    # For each event pair of large communities, try to infer relationships
    new_triples = []

    for i, comm1 in enumerate(large_communities):
        for j, comm2 in enumerate(large_communities):
            if i >= j:
                continue  # Skip self-comparisons and duplicates

            # Select representative events from each community
            rep1 = [e for e in list(comm1) if e.startswith("EVENT")][:min(10, len(comm1))]
            rep2 = [e for e in list(comm2) if e.startswith("EVENT")][:min(10, len(comm2))]

            # Prepare relevant existing triples for context
            context_triples = []
            for triple in triples:
                if (triple["subject"] in rep1 or triple["subject"] in rep2)\
                    or (triple["object"] in rep1 or triple["object"] in rep2):
                    context_triples.append(triple)

            # Limit context size
            if len(context_triples) > 100:
                context_triples = context_triples[:100]

            # Convert triples to text for prompt
            def get_event_claim(triplet):
                claim = triplet.get("claim", "")
                return f"(từ nhận định: {claim})" if claim else claim

            triples_text = "\n".join([
                f"{t['subject']} {t['predicate']} {t['object']} (từ nhận định: {get_event_claim(t)})"
                for t in context_triples
            ])

            # Prepare entity lists
            events1 = ", ".join(rep1)
            events2 = ", ".join(rep2)

            try:
                # Call LLM
                llm = LLM(config)
                response = llm(
                    BETWEEN_COMMUNITY_EVENT_RELATION_SYSTEM_PROMPT,
                    get_between_community_event_relation_user_prompt(events1, events2, triples_text),
                )

                inferred_triples = extract_json_from_text(response, verbose)

                if inferred_triples and isinstance(inferred_triples, list):
                    # Mark as inferred and add to new triples
                    for triple in inferred_triples:
                        if "subject" in triple and "predicate" in triple and "object" in triple:
                            # Skip self-referencing triples
                            if triple["subject"] == triple["object"]:
                                continue
                            triple["inferred"] = True
                            new_triples.append(triple)

                    print(f"Inferred {len(new_triples)} new relationships between communities")
                else:
                    print("Could not extract valid inferred relationships from LLM response")

            except Exception as e:
                print(f"Error in LLM-based relationship inference: {e}")

    return new_triples


def deduplicate_triples(triples):
    # Use tuple of (subject, predicate, object) as key
    unique_triples = {}
    
    for triple in triples:
        key = (triple["subject"], triple["predicate"], triple["object"])
        # Keep original triples (not inferred) when duplicates exist
        if key not in unique_triples or not triple.get("inferred", False):
            unique_triples[key] = triple
    
    return list(unique_triples.values())


def infer_event_relationships(triples, config=config, verbose=False):
    event_graph, _ = build_event_graph(triples)
    communities = identify_event_communities(event_graph)
    print(f"Identified {len(communities)} disconnected event communities in the event graph")
    
    within_inferred = infer_within_event_community_relations(triples, communities, config, verbose)
    triples += within_inferred
    between_inferred = infer_between_event_community_relations(triples, communities, config, verbose)
    triples += between_inferred
    
    triples = deduplicate_triples(triples)
    filtered = [triple for triple in triples if triple["subject"] != triple["object"]]
    if len(filtered) < len(triples):
        print(f"Removed {len(triples) - len(filtered)} self-referencing event triples")
    
    print(f"Added {len(filtered) - len(triples)} inferred event relationships")
    return filtered


def get_event_stats(event_triples):
    nodes = [t["subject"] for t in event_triples] + [t["object"] for t in event_triples]
    nodes = list(set(nodes))
    events = list(set([n for n in nodes if n.startswith("EVENT")]))
    participants = list(set([n for n in nodes if n.startswith("ENTITY")]))
    locations = list(set([n for n in nodes if n.startswith("LOCATION")]))
    times = list(set([n for n in nodes if n.startswith("TIME")]))
    
    return {
        "events": len(events),
        "participants": len(participants),
        "locations": len(locations),
        "times": len(times),
        "relations": len([e for e in event_triples if e["subject"].startswith("EVENT") or e["object"].startswith("EVENT")]),
        "has_participant": len([e for e in event_triples if e["predicate"] == "HAS_PARTICIPANT"]),
        "at_location": len([e for e in event_triples if e["predicate"] == "AT_LOCATION"]),
        "at_time": len([e for e in event_triples if e["predicate"] == "AT_TIME"]),
        "precede": len([e for e in event_triples if e["predicate"] == "PRECEDE"]),
        "co_occur": len([e for e in event_triples if e["predicate"] == "CO_OCCUR"]),
        "cause": len([e for e in event_triples if e["predicate"] == "CAUSE"]),
    }


def get_unique_entities(event_triples):
    entities = [
        t["subject"] if t["subject"].startswith("ENTITY") else t["object"]
        for t in event_triples
        if t["subject"].startswith("ENTITY") or t["object"].startswith("ENTITY")
    ]
    return list(set(entities))


def get_entity_relations(text, events, claims, config=config, verbose=False):
    entities = get_unique_entities(events)
    entity_relations = []
    llm = LLM(config)
    
    for _ in tqdm(range(2), desc="Entity-Entity Relations"):
        if len(entities) < 1:
            break
        
        if verbose:
            print(f"Remaining {len(entities)} entities to process...")
        
        text_entity_relations = llm(
            ENTITY_RELATION_SYSTEM_PROMPT,
            get_entity_relation_user_prompt(text, entities, claims),
        )
        entity_relations += extract_json_from_text(text_entity_relations, verbose)
        
        if verbose:
            print(f"Extracted {len(entity_relations)} entity relations so far.")
        
        new_entities = get_unique_entities(entity_relations)
        entities = list(set(entities) - set(new_entities))
    
    return entity_relations