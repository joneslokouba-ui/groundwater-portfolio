# Case Study: Hydrogeology Document Assistant (HybridRAG, Module H2)

## Problem
Hydrogeologists and environmental engineers regularly need to search
across technical references, guidance documents, and reports to answer
specific questions (e.g., "what geochemical evidence supports MNA at
this site?") — a task well suited to retrieval-augmented search, but
rarely built as an actual tool within the industry.

## Approach
Reused the HybridRAG architecture from the AI/ML portfolio's Module 2
(Supervisor Multi-Agent + HybridRAG), applying the same
`α·VectorSim + (1−α)·KeywordScore` blended retrieval formula to a
hydrogeology/remediation knowledge base instead of tax documents.

Two knowledge-source modes:
1. **Built-in notes** covering contaminant transport mechanisms,
   monitored natural attenuation, bioremediation, engineered
   remediation technologies (pump-and-treat, PRBs, ISCO/ISCR, SVE/air
   sparging), and groundwater geochemistry fundamentals.
2. **User-uploaded PDF** — any PDF (a textbook, report, or paper) can
   be uploaded and queried directly in the same session, processed
   in-memory only.

## Result
Tested against representative technical questions (e.g.,
"How does bioaugmentation work for chlorinated solvents?", "What is a
permeable reactive barrier?", "How is redox condition measured in an
aquifer?") — the hybrid retrieval correctly surfaced the most relevant
source document as the top result in every test case, with the
scoring breakdown (vector similarity vs. keyword overlap) shown
transparently for each retrieved passage.

## Honest Scope Note
This module performs extractive retrieval (ranking and returning the
most relevant source passages), not generative question-answering —
it does not synthesize a novel answer unless connected to an LLM API.
This is a deliberate design choice (see ADR-002) to keep the tool
honest about what it does, and to keep the public deployment
lightweight given Streamlit Community Cloud's free-tier resource
limits.

## Copyright Note
The built-in knowledge base consists of original explanatory notes,
not excerpts from any specific copyrighted textbook. The PDF-upload
feature allows querying of any document the user has legal access to,
processed only for that session — the same underlying capability as
any "chat with your document" tool.