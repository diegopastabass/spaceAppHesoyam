# graph.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import TypedDict, List, Tuple, Dict, Any
from dataclasses import dataclass
from langchain.schema import Document
from langgraph.graph import StateGraph, END
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureChatOpenAI

class AgentState(TypedDict, total=False):
    question: str
    in_domain: bool
    domain_label: str
    queries: List[str]
    retrieved: List[Tuple[Document, float]]
    filtered: List[Tuple[Document, float]]
    context_text: str
    answer_md: str
    citations: List[Dict[str, Any]]
    threshold: float
    k_per_query: int
    score_mode: str  # "similarity" | "distance"

def _unique_docs_with_min_score(pairs: List[Tuple[Document, float]]) -> List[Tuple[Document, float]]:
    seen = {}
    for d, s in pairs:
        key = (d.metadata.get("source", ""), d.page_content.strip()[:300])
        if key not in seen or s < seen[key][1]:
            seen[key] = (d, s)
    return sorted(seen.values(), key=lambda x: x[1])

def _build_citations(pairs: List[Tuple[Document, float]]) -> List[Dict[str, Any]]:
    cites = []
    for idx, (d, s) in enumerate(pairs, start=1):
        cites.append({"index": idx, "source": d.metadata.get("source", "Desconocida"), "score": float(s)})
    return cites

def _infer_score_mode(scores):
    if not scores:
        return "similarity"
    if all(0.0 <= s <= 1.0 for s in scores):
        return "similarity"  # alto = mejor
    return "distance"        # bajo = mejor

@dataclass
class Nodes:
    llm: AzureChatOpenAI
    db: FAISS

    def classify_domain(self, state: AgentState) -> AgentState:
        prompt = (
            "Eres un verificador de dominio. ¿La pregunta pertenece a 'Biosciences'?"
            ' Devuelve JSON: {"in_domain": true|false, "label": "NASA_BIO"|"OUT"}\n\n'
            f"Pregunta: {state['question']}"
        )
        rsp = self.llm.invoke(prompt).content.strip()
        in_domain = ("true" in rsp.lower()) and ("false" not in rsp.lower())
        label = "NASA_BIO" if "NASA_BIO" in rsp else ("OUT" if "OUT" in rsp else ("NASA_BIO" if in_domain else "OUT"))
        return {"in_domain": in_domain, "domain_label": label}

    def expand_queries(self, state: AgentState) -> AgentState:
        q = state["question"]
        prompt = (
            "Genera 4-6 reformulaciones en INGLÉS (multi-query) para mejorar recall en denso.\n"
            'Responde SOLO JSON: {"queries": ["..."]}\n\n'
            f"User question: {q}"
        )
        text = self.llm.invoke(prompt).content
        import json, re
        queries: List[str] = []
        try:
            data = json.loads(re.search(r"\{.*\}", text, re.S).group(0))
            queries = [s for s in data.get("queries", []) if isinstance(s, str)]
        except Exception:
            queries = [q, f"scientific findings in microgravity: {q}"]
        if q not in queries:
            queries.insert(0, q)
        queries = list(dict.fromkeys([s.strip() for s in queries if s.strip()]))[:6]
        return {"queries": queries}

    def retrieve(self, state: AgentState) -> AgentState:
        k = state.get("k_per_query", 3)
        pairs: List[Tuple[Document, float]] = []
        for subq in state["queries"]:
            try:
                pairs.extend(self.db.similarity_search_with_score(subq, k=k))
            except Exception:
                pass
        pairs = _unique_docs_with_min_score(pairs)
        return {"retrieved": pairs}

    def threshold_and_context(self, state: AgentState) -> AgentState:
        pairs = state["retrieved"]
        if not pairs:
            return {"filtered": [], "context_text": "", "citations": []}
        scores = [s for _, s in pairs]
        mode = state.get("score_mode") or _infer_score_mode(scores)
        thr = float(state.get("threshold", 0.7 if mode == "similarity" else 0.35))
        def keep(s: float) -> bool:
            return s >= thr if mode == "similarity" else s <= thr
        filtered = [(d, s) for (d, s) in pairs if keep(s)]
        if not filtered and pairs:
            filtered = pairs[:2]
        ctx_chunks = []
        for idx, (d, s) in enumerate(filtered, start=1):
            src = d.metadata.get("source", "Desconocida")
            ctx_chunks.append(f"[{idx}] Source: {src}\n{d.page_content}")
        return {
            "filtered": filtered,
            "context_text": "\n\n---\n\n".join(ctx_chunks),
            "citations": _build_citations(filtered),
            "score_mode": mode,
            "threshold": thr,
        }

    def generate_answer(self, state: AgentState) -> AgentState:
        if not state.get("in_domain", False):
            msg = ("⚠️ La pregunta está fuera del dominio 'NASA biosciences / space life sciences' "
                   "o el clasificador no encontró correspondencia.\n\n**Respuesta:** No tengo suficiente información para responder.")
            return {"answer_md": msg}
        if not state.get("filtered"):
            msg = (f"⚠️ No se encontraron evidencias suficientes bajo el umbral ({state.get('threshold', 0):.2f}).\n\n"
                   "**Respuesta:** No tengo suficiente información para responder.")
            return {"answer_md": msg}

        cites = "\n".join([f"- [{c['index']}] {c['source']} (score={c['score']:.4f})" for c in state["citations"]])
        prompt = f"""
Eres un asistente científico. Responde **solo** con el CONTEXTO.
Si no alcanza, di: "No tengo suficiente información para responder."

Formato Markdown:
- Explicación clara con subtítulos/bullets.
- Resalta *proteínas/genes/vías* con itálicas o **negritas**.
- Usa citas [n] coherentes con el CONTEXTO.
- Cierra con **Resumen** (2-3 líneas).

CONTEXT:
{state['context_text']}

QUESTION:
{state['question']}
"""
        ans = self.llm.invoke(prompt).content
        ans += f"\n\n---\n**Citas**\n{cites}"
        return {"answer_md": ans}

def build_agentic_graph(llm: AzureChatOpenAI, db: FAISS):
    nodes = Nodes(llm=llm, db=db)
    workflow = StateGraph(AgentState)
    workflow.add_node("classify_domain", nodes.classify_domain)
    workflow.add_node("expand_queries", nodes.expand_queries)
    workflow.add_node("retrieve", nodes.retrieve)
    workflow.add_node("threshold_and_context", nodes.threshold_and_context)
    workflow.add_node("generate_answer", nodes.generate_answer)
    workflow.set_entry_point("classify_domain")

    def route(state: AgentState) -> str:
        return "expand_queries" if state.get("in_domain", False) else "generate_answer"

    workflow.add_conditional_edges(
        "classify_domain",
        route,
        {"expand_queries": "expand_queries", "generate_answer": "generate_answer"}
    )
    workflow.add_edge("expand_queries", "retrieve")
    workflow.add_edge("retrieve", "threshold_and_context")
    workflow.add_edge("threshold_and_context", "generate_answer")
    workflow.add_edge("generate_answer", END)
    return workflow.compile()
