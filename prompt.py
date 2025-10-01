extraction_prompt = """
You are an expert research assistant. 
Extract structured information from the following research paper text according to this ontology:

Entities:
- Paper: {title, year, authors, venue (if available)}
- Technique: {name, type [architecture/training/optimization/etc.]}
- Result: {metric, value, dataset (if available)}
- Application: {domain, purpose, use_case}

Relationships:
- (Paper) —[USES]→ (Technique)
- (Paper) —[REPORTS]→ (Result)
- (Paper) —[ADDRESSES]→ (Application)
- (Technique) —[LEADS_TO]→ (Result) [if explicitly stated or strongly implied]
- (Technique) —[ENABLES]→ (Application) [if the technique enables the application]

Instructions:
1. Only extract techniques that the paper introduces, applies, or compares. 
2. Only extract results with clearly measurable outcomes (BLEU, accuracy, latency, training speed, etc.).
3. Extract applications by identifying the domain (e.g., machine translation, computer vision, NLP) and specific purpose or use case the paper addresses.
4. Return the output in JSON with this structure:

{
  "paper": {
    "title": "...",
    "year": "...",
    "authors": ["...", "..."],
    "venue": "..."
  },
  "techniques": [
    {"name": "...", "type": "..."},
    {"name": "...", "type": "..."}
  ],
  "results": [
    {"metric": "...", "value": "...", "dataset": "..."}
  ],
  "applications": [
    {"domain": "...", "purpose": "...", "use_case": "..."}
  ],
  "relationships": [
    {"subject": "Paper_name", "predicate": "USES", "object": "Technique"},
    {"subject": "Paper_name", "predicate": "REPORTS", "object": "Result"},
    {"subject": "Paper_name", "predicate": "ADDRESSES", "object": "Application"},
    {"subject": "Technique_name", "predicate": "LEADS_TO", "object": "Result"},
    {"subject": "Technique_name", "predicate": "ENABLES", "object": "Application"}
  ]
}

Now extract according to this schema from the following text:
---
{paper_text}
---
"""

