# EventViKG

**Note:** This repository is a modification of [robert-mcdermott/ai-knowledge-graph](https://github.com/robert-mcdermott/ai-knowledge-graph) by Robert McDermott. :contentReference[oaicite:0]{index=0}  
We extend it with additional capabilities such as event-centric extraction, temporal (time) and geographic (location) determination, and claim-extraction techniques.

---

## What this project does  
This project builds on the original knowledge-graph generation pipeline, and adds the following enhancements:

- Event-centric extraction: Identify and represent events (who, what, when, where) explicitly.  
- Time & location determination: Extract temporal and geographic metadata associated with entities and events.  
- Claim extraction: Beyond Subject-Predicate-Object triples, the system identifies claims/assertions made in the text.  
- All the original features of the base project: text chunking, entity relationship extraction, entity standardization, relationship inference, interactive visualization.

---

## Features  
- Unstructured text → structured graph representation (entities, relationships, events, claims)  
- Time and location metadata captured in the graph nodes/edges  
- Claim extraction: identify statements/assertions from text  
- Interactive visualization of the resulting graph  
- Supports any LLM compatible API endpoint  
- Configurable via `config.toml`

---