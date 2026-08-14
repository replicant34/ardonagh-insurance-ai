import os
import time
import uuid
from typing import TypedDict

from dotenv import load_dotenv
from openai import OpenAI
from langgraph.graph import StateGraph, START, END

from app.observability.logger import logger

import json
from typing import Any, List

from app.ai.agent import (
    TOOLS,
    execute_tool,
)


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


# ------------------------------------------------------------------
# Graph state
# ------------------------------------------------------------------

class AgentState(TypedDict):
    question: str
    answer: str
    request_id: str
    response_id: str
    tool_calls: List[Any]
    tool_outputs: List[dict]
    tools_used: list[str]


# ------------------------------------------------------------------
# Nodes
# ------------------------------------------------------------------

def receive_question(state: AgentState) -> AgentState:
    """
    Entry node for the insurance AI workflow.
    """

    logger.info(
        "GRAPH_NODE | request_id=%s | node=receive_question",
        state["request_id"],
    )

    return state


def agent_node(state: AgentState) -> AgentState:
    """
    Let the LLM decide whether to answer or request tools.
    """

    logger.info(
        "GRAPH_NODE | request_id=%s | node=agent",
        state["request_id"],
    )

    start_time = time.perf_counter()

    # First pass: user question
    if not state["tool_outputs"]:

        response = client.responses.create(
            model="gpt-5-mini",
            instructions=(
                "You are an internal insurance analytics AI assistant. "

                "Use the available tools whenever company data or internal "
                "knowledge is required. "

                "Use database tools for structured insurance facts such as "
                "claims, policies, premiums and risk indicators. "

                "Use search_internal_knowledge when the question requires "
                "internal procedures, rules, requirements, governance guidance "
                "or other document-based knowledge. "

                "You may use multiple tools across multiple steps when a question "
                "requires combining structured company data with internal knowledge. "

                "Never invent company statistics, claim information, policy "
                "information, procedures, documents, currencies or system capabilities. "

                "Fraud probabilities and risk indicators are decision-support "
                "signals only and must never be presented as proof of fraud."
            ),
            input=state["question"],
            tools=TOOLS,
        )

    # Subsequent pass: tool results are available
    else:

        response = client.responses.create(
            model="gpt-5-mini",
            instructions=(
                "Continue answering the user's question using the available "
                "tool results. "

                "If additional company data or internal knowledge is required, "
                "use another available tool before answering. "

                "Use database tools for structured facts and "
                "search_internal_knowledge for internal procedures and rules. "

                "Do not invent missing facts, procedures, evidence or currencies. "

                "When internal knowledge is used, identify the supporting "
                "document ID, version and section when available. "

                "If the available evidence is insufficient to determine the "
                "answer, clearly state what cannot be confirmed. "

                "When a risk-analysis tool is used, include the material risk "
                "outputs returned by the tool in the final answer, including the "
                "fraud probability, review priority and identified risk indicators "
                "when those fields are available. "

                "Do not omit or alter material numeric values returned by tools. "

                "Risk indicators and fraud probabilities are decision-support "
                "signals only and must not be presented as proof of fraud."
            ),
            previous_response_id=state["response_id"],
            input=state["tool_outputs"],
            tools=TOOLS,
        )

    duration_ms = (
        time.perf_counter() - start_time
    ) * 1000

    tool_calls = [
        item
        for item in response.output
        if item.type == "function_call"
    ]

    logger.info(
        "GRAPH_LLM_CALL | request_id=%s "
        "| duration_ms=%.2f | tool_calls=%d",
        state["request_id"],
        duration_ms,
        len(tool_calls),
    )

    return {
        **state,
        "response_id": response.id,
        "tool_calls": tool_calls,
        "answer": response.output_text or "",
    }

def tool_node(state: AgentState) -> AgentState:
    """
    Execute tools requested by the LLM.
    """

    logger.info(
        "GRAPH_NODE | request_id=%s | node=tools",
        state["request_id"],
    )

    outputs = []

    # Keep history of every tool executed by the graph
    tools_used = list(
        state.get("tools_used", [])
    )

    for tool_call in state["tool_calls"]:

        arguments = json.loads(
            tool_call.arguments
        )

        # Record the tool BEFORE executing it
        tools_used.append(tool_call.name)

        result = execute_tool(
            tool_name=tool_call.name,
            arguments=arguments,
            request_id=state["request_id"],
        )

        outputs.append(
            {
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": json.dumps(
                    {
                        "tool": tool_call.name,
                        "result": result,
                    }
                ),
            }
        )

    return {
        **state,
        "tool_outputs": outputs,
        "tool_calls": [],
        "tools_used": tools_used,
    }

def route_after_agent(state: AgentState) -> str:
    """
    Decide whether the graph should execute tools
    or finish with the current answer.
    """

    if state.get("tool_calls"):
        return "tools"

    return "end"

# ------------------------------------------------------------------
# Build graph
# ------------------------------------------------------------------

builder = StateGraph(AgentState)

builder.add_node(
    "receive_question",
    receive_question,
)

builder.add_node(
    "agent",
    agent_node,
)

builder.add_node(
    "tools",
    tool_node,
)


builder.add_edge(
    START,
    "receive_question",
)

builder.add_edge(
    "receive_question",
    "agent",
)


builder.add_conditional_edges(
    "agent",
    route_after_agent,
    {
        "tools": "tools",
        "end": END,
    },
)


builder.add_edge(
    "tools",
    "agent",
)


insurance_graph = builder.compile()

# ------------------------------------------------------------------
# Public interface
# ------------------------------------------------------------------

def run_graph(question: str) -> str:

    request_id = str(uuid.uuid4())

    logger.info(
        "GRAPH_REQUEST_START | request_id=%s",
        request_id,
    )

    result = insurance_graph.invoke(
        {
            "question": question,
            "answer": "",
            "request_id": request_id,
            "response_id": "",
            "tool_calls": [],
            "tool_outputs": [],
            "tools_used": [],
        }
    )

    logger.info(
        "GRAPH_REQUEST_COMPLETE | request_id=%s",
        request_id,
    )

    answer = result["answer"]

    if not answer or not answer.strip():
        return (
            "I cannot answer this question from the "
            "information available through the current tools."
        )

    return answer

def run_graph_with_metadata(question: str) -> dict:
    """
    Run the LangGraph workflow and return the final
    answer together with evaluation metadata.
    """

    request_id = str(uuid.uuid4())

    logger.info(
        "GRAPH_REQUEST_START | request_id=%s",
        request_id,
    )

    result = insurance_graph.invoke(
        {
            "question": question,
            "answer": "",
            "request_id": request_id,
            "response_id": "",
            "tool_calls": [],
            "tool_outputs": [],
            "tools_used": [],
        }
    )

    logger.info(
        "GRAPH_REQUEST_COMPLETE | request_id=%s",
        request_id,
    )

    answer = result.get("answer", "")

    if not answer or not answer.strip():
        answer = (
            "I cannot answer this question from the "
            "information available through the current tools."
        )

    return {
        "answer": answer,
        "tools_used": result.get(
            "tools_used",
            [],
        ),
        "request_id": request_id,
    }
