"""
Prompt construction for RAG using analyst-grade information formatting.

Provides formatted context with full metadata for transparency and traceability.
"""

from rag.intent_classification import classify_intent, STYLE_RULES


def format_evidence(context_chunks):
    """
    Format evidence from chunks with full metadata.
    
    Each chunk citation includes:
    - Section name (e.g., "Risk Factors")
    - Page number
    - Document name
    - Text content
    
    Args:
        context_chunks: List of chunk dictionaries
    
    Returns:
        Formatted evidence string
    """
    evidence = []

    for i, c in enumerate(context_chunks, 1):
        page = c.get("page_number", "?")
        section = c.get("section", "Unknown Section")
        doc = c.get("document_name", "Unknown Document")
        text = c.get("chunk_text", "").replace("\n", " ").strip()

        # Format: [Section: XXX | Page: N | Doc: XXX] Text...
        header = f"[{i}] [Section: {section} | Page: {page} | Doc: {doc}]"
        chunk_evidence = f"{header}\n{text}"
        
        evidence.append(chunk_evidence)

    return "\n\n".join(evidence)


def build_prompt(question: str, context_chunks: list[dict]) -> str:
    """
    Build professional analyst prompt with full context and metadata.
    
    Args:
        question: User's question
        context_chunks: Retrieved and reranked chunks
    
    Returns:
        Complete prompt for LLM
    """
    intent = classify_intent(question)
    style_rules = STYLE_RULES[intent.value]
    evidence_context = format_evidence(context_chunks)

    # Enhanced prompt with metadata awareness
    prompt = f"""You are answering strictly from a Draft Red Herring Prospectus (DRHP) or IPO filing document.

CRITICAL GUIDELINES:
1. Base EVERY factual statement on the provided evidence
2. Always cite the section and page number from the context
3. If information is not in the evidence, explicitly state: "The document does not disclose this"
4. Do not speculate or infer beyond what is explicitly stated
5. Flag any contradictions found in different sections
6. Disclose the document name when referencing information

FORMATTING RULES:
- Use professional financial language
- Do NOT use markdown, bullet points, or heading symbols
- Write in clear, professional analyst tone
- Structure answer logically with clear transitions

ANSWER STYLE GUIDELINES:
{style_rules}

REFERENCE MATERIALS:
{evidence_context}

QUESTION TO ANSWER:
{question}

RESPONSE FORMAT:
Return your answer in this JSON structure:

{{
  "answer": "Your comprehensive answer here, with inline section references like [Section: Risk Factors | Page: 33]",
  "citations": [
    {{"section": "Risk Factors", "page": 33}},
    {{"section": "Business Overview", "page": 12}}
  ],
  "confidence": "high|medium|low",
  "sources_referenced": ["Document Name 1", "Document Name 2"]
}}

Now provide your answer:"""
    
    return prompt

