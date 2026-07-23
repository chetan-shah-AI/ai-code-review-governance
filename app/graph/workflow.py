from langgraph import graph
from langgraph.graph import END, StateGraph

from app.graph.nodes import (
    ai_review_node,
    deterministic_review_node,
    governance_review_node,
    merge_findings_node,
    summary_node,
    triage_node,
    verdict_node,
)
from app.graph.state import ReviewGraphState
from app.schemas.review import ReviewInput


def build_review_workflow():
    """
    Build the LangGraph workflow.
    """

    graph = StateGraph(ReviewGraphState)

    graph.add_node("triage", triage_node)
    graph.add_node("deterministic_review", deterministic_review_node)
    graph.add_node("ai_review", ai_review_node)
    graph.add_node("governance_review", governance_review_node,)
    graph.add_node("merge_findings", merge_findings_node)
    graph.add_node("verdict", verdict_node)
    graph.add_node("summary", summary_node)


    graph.set_entry_point("triage")

    graph.add_edge("triage", "deterministic_review")
    graph.add_edge("deterministic_review", "ai_review")
    graph.add_edge("ai_review", "governance_review")
    graph.add_edge("governance_review", "merge_findings")
    graph.add_edge("merge_findings", "verdict")
    graph.add_edge("verdict", "summary")
    graph.add_edge("summary", END)
    

    return graph.compile()


def run_review_workflow(review_input: ReviewInput) -> ReviewGraphState:
    """
    Run the full review workflow for one PR.
    """

    workflow = build_review_workflow()

    initial_state: ReviewGraphState = {
        "review_input": review_input,
        "errors": [],
    }

    return workflow.invoke(initial_state)