# Thesis Diagrams (Mermaid)

## Figure 4.1: High-Level Architecture (Fact Checker MAS)
*Source: apps/agent/README.md*

```mermaid
graph LR
    A[extract_claims] --> B{dispatch_claims_for_verification}
    B -- Claims to verify --> C[claim_verifier_node]
    B -- No claims --> E[END]
    C --> D[generate_report_node]
    D --> E
```

## Figure 4.2: Claim Extractor Workflow
*Source: apps/agent/claim_extractor/README.md*

```mermaid
graph LR
    A[sentence_splitter_node] --> B[selection_node]
    B --> C[disambiguation_node]
    C --> D[decomposition_node]
    D --> E[validation_node]
```

## Figure 4.3: Claim Verifier Workflow
*Source: apps/agent/claim_verifier/README.md*

```mermaid
graph LR
    A[generate_search_queries_node] --> B{query_distributor}
    B -- Queries exist --> C[retrieve_evidence_node]
    B -- No queries --> Z[END]
    C --> D[evaluate_evidence_node]
    D -- Insufficient & Retries < Max --> A
    D -- Sufficient or Max Retries --> Z
```
