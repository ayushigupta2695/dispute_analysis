from langgraph.graph import StateGraph
from typing import TypedDict
from core.receipt_agent import analyze_receipt
from core.validation_agent import validate_receipt


class FinanceState(TypedDict, total=False):
    file_path: str
    llm_provider: str
    receipt_id: int
    receipt_data: dict
    validation: dict


def receipt_node(state: FinanceState) -> FinanceState:
    result = analyze_receipt(
        state["file_path"],
        state["llm_provider"]
    )
    return {**state, **result}


def validation_node(state: FinanceState) -> FinanceState:
    validation = validate_receipt(
        receipt_id=state["receipt_id"],
        receipt_data=state["receipt_data"]
    )
    return {**state, "validation": validation}


graph = StateGraph(
    FinanceState,
    input_keys=["file_path", "llm_provider"]
)

graph.add_node("receipt", receipt_node)
graph.add_node("validate", validation_node)

graph.set_entry_point("receipt")
graph.add_edge("receipt", "validate")

finance_graph = graph.compile()
