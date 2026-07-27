import os
import glob
import streamlit as st
from pypdf import PdfReader

from hydro_rag import build_retriever_from_texts, chunk_text, HybridRetriever

st.set_page_config(page_title="Hydrogeology Document Assistant", layout="wide")

st.title("Hydrogeology Document Assistant")
st.caption(
    "HybridRAG retrieval over groundwater contamination & remediation notes — "
    "reusing the same α·VectorSim + (1−α)·KeywordScore formula as the "
    "AI/ML portfolio's Module 2 (Supervisor Multi-Agent + HybridRAG). "
    "Upload your own PDF (e.g., a textbook, report, or paper) to query it "
    "directly — nothing you upload is stored beyond this session."
)

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "corpus")


@st.cache_resource(show_spinner=False)
def load_default_retriever():
    texts = []
    for path in sorted(glob.glob(os.path.join(CORPUS_DIR, "*.md"))):
        with open(path, "r", encoding="utf-8") as f:
            texts.append((f.read(), os.path.basename(path)))
    return build_retriever_from_texts(texts)


def extract_pdf_text(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    text_parts = []
    for page in reader.pages:
        text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts)


# ---------------- Sidebar ----------------
st.sidebar.header("Knowledge Source")
source_mode = st.sidebar.radio(
    "Query against:",
    ["Built-in remediation/geochemistry notes", "My uploaded PDF"],
)

uploaded_pdf = None
if source_mode == "My uploaded PDF":
    uploaded_pdf = st.sidebar.file_uploader("Upload a PDF", type=["pdf"])
    st.sidebar.caption(
        "Processed in-memory for this session only — not saved to disk, "
        "not sent anywhere beyond this app's own retrieval index."
    )

st.sidebar.header("Retrieval Settings")
alpha = st.sidebar.slider(
    "α — weight on vector similarity vs. keyword match", 0.0, 1.0, 0.6, 0.05
)
top_k = st.sidebar.slider("Number of passages to retrieve", 1, 8, 4)

# ---------------- Build retriever based on mode ----------------
retriever = None
active_label = ""

if source_mode == "Built-in remediation/geochemistry notes":
    retriever = load_default_retriever()
    active_label = "built-in notes (contaminant transport, MNA, bioremediation, engineered remediation, geochemistry)"
elif uploaded_pdf is not None:
    with st.spinner("Extracting and indexing PDF..."):
        pdf_text = extract_pdf_text(uploaded_pdf)
        if len(pdf_text.strip()) < 50:
            st.warning(
                "Very little text could be extracted — this PDF may be a "
                "scanned image without a text layer, which this tool can't read."
            )
        else:
            chunks = chunk_text(pdf_text, source=uploaded_pdf.name)
            retriever = HybridRetriever(chunks)
            active_label = f"'{uploaded_pdf.name}' ({len(chunks)} chunks indexed)"

# ---------------- Query ----------------
st.subheader("Ask a question")
if retriever:
    st.caption(f"Currently querying: {active_label}")

query = st.text_input(
    "Your question",
    placeholder="e.g., How does bioaugmentation work for chlorinated solvents?",
)

if query and retriever:
    results = retriever.retrieve(query, top_k=top_k, alpha=alpha)

    st.subheader("Retrieved Passages (ranked by hybrid score)")
    for i, r in enumerate(results, 1):
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            c1.markdown(f"**#{i} — {r['chunk'].source}**")
            c2.metric("Hybrid", f"{r['hybrid_score']:.3f}")
            c3.metric("Vector sim", f"{r['vector_sim']:.3f}")
            c4.metric("Keyword", f"{r['keyword_score']:.3f}")
            st.write(r["chunk"].text)

    st.caption(
        "This tool returns and ranks the most relevant source passages "
        "(extractive retrieval). It does not generate a synthesized answer "
        "unless connected to an LLM API — see the architecture notes for "
        "how a generation step would plug in on top of this retrieval layer."
    )
elif query and not retriever:
    st.info("Upload a PDF first, or switch to the built-in notes.")

with st.expander("How the hybrid score works"):
    st.markdown(
        """
        Each retrieved passage is scored as:

        `hybrid_score = α × vector_similarity + (1 − α) × keyword_score`

        - **vector_similarity**: TF-IDF cosine similarity between your question and the passage
        - **keyword_score**: fraction of your question's meaningful terms found literally in the passage
        - **α** (adjustable in the sidebar): how much to trust semantic similarity vs. exact term overlap

        This is the same blended-retrieval formula used in Module 2 of the
        AI/ML engineering portfolio (Supervisor Multi-Agent + HybridRAG),
        applied here to hydrogeology/remediation content instead of tax
        documents — same architecture, different domain.
        """
    )