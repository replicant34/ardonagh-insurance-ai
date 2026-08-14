import json
import os
import time
import uuid


from dotenv import load_dotenv
from openai import OpenAI
from app.observability.logger import logger
from app.tools.insurance_tools import (
    get_active_policy_count,
    get_total_premium,
    get_total_claims,
    get_loss_ratio,
    get_policy_by_number,
    get_claim_by_id,
    analyze_claim_risk,
    search_internal_knowledge,
)


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ------------------------------------------------------------------
# Tool definitions exposed to the LLM
# ------------------------------------------------------------------

TOOLS = [
    {
        "type": "function",
        "name": "get_active_policy_count",
        "description": (
            "Returns the current number of active insurance policies "
            "from the company's Azure SQL database."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_total_premium",
        "description": (
            "Returns the total written premium amount across all "
            "insurance policies."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_total_claims",
        "description": (
            "Returns the total claim amount across all insurance claims."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_loss_ratio",
        "description": (
            "Returns the company's current simplified loss ratio as a "
            "percentage, calculated as total claim amount divided by "
            "total written premium."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_policy_by_number",
        "description": (
            "Retrieves information about a specific insurance policy "
            "using its policy number."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "policy_number": {
                    "type": "string",
                    "description": (
                        "The exact insurance policy number, "
                        "for example POL-00000005."
                    ),
                }
            },
            "required": ["policy_number"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_claim_by_id",
        "description": (
            "Retrieves detailed information about a specific insurance claim. "
            "Use this when the user asks for claim details such as status, "
            "amount, type, description, approval amount, or processing time."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "claim_id": {
                    "type": "integer",
                    "description": (
                        "The numeric ClaimID, for example 16."
                    ),
                }
            },
            "required": ["claim_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "analyze_claim_risk",
        "description": (
            "Calculates deterministic review-risk indicators for a specific "
            "insurance claim. Use this when the user asks to investigate a "
            "claim, assess risk, identify suspicious indicators, or determine "
            "whether a claim should receive additional human review. "
            "This tool provides decision-support signals and does not determine fraud."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "claim_id": {
                    "type": "integer",
                    "description": (
                        "The numeric ClaimID to analyse, for example 16."
                    ),
                }
            },
            "required": ["claim_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },

    {
        "type": "function",
        "name": "search_internal_knowledge",
        "description": (
            "Search approved internal insurance knowledge documents, "
            "including claims procedures and operational policies. "
            "Use this tool when a question requires internal rules, "
            "procedures, requirements, governance guidance, or other "
            "document-based knowledge."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "A focused semantic search query describing "
                        "the internal information required."
                    ),
                },
                "top_k": {
                    "type": "integer",
                    "description": (
                        "Number of relevant knowledge chunks to retrieve."
                    ),
                    "minimum": 1,
                    "maximum": 5,
                },
            },
            "required": [
                "query",
            ],
            "additionalProperties": False,
        },
    }
]


# ------------------------------------------------------------------
# Internal tool registry
# ------------------------------------------------------------------

TOOL_REGISTRY = {
    "get_active_policy_count": get_active_policy_count,
    "get_total_premium": get_total_premium,
    "get_total_claims": get_total_claims,
    "get_loss_ratio": get_loss_ratio,
    "get_policy_by_number": get_policy_by_number,
    "get_claim_by_id": get_claim_by_id,
    "analyze_claim_risk": analyze_claim_risk,
    "search_internal_knowledge": search_internal_knowledge,
}


def execute_tool(
    tool_name: str,
    arguments: dict,
    request_id: str,
):
    """
    Execute an approved tool and record execution metrics.
    """

    tool_function = TOOL_REGISTRY.get(tool_name)

    if tool_function is None:
        logger.error(
            "TOOL_UNKNOWN | request_id=%s | tool=%s",
            request_id,
            tool_name,
        )

        raise ValueError(
            f"Unknown tool requested: {tool_name}"
        )

    logger.info(
        "TOOL_CALL | request_id=%s | tool=%s | arguments=%s",
        request_id,
        tool_name,
        arguments,
    )

    start_time = time.perf_counter()

    try:
        result = tool_function(**arguments)

        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        logger.info(
            "TOOL_RESULT | request_id=%s | tool=%s "
            "| duration_ms=%.2f | success=True",
            request_id,
            tool_name,
            duration_ms,
        )

        return result

    except Exception as exc:

        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        logger.exception(
            "TOOL_RESULT | request_id=%s | tool=%s "
            "| duration_ms=%.2f | success=False | error=%s",
            request_id,
            tool_name,
            duration_ms,
            str(exc),
        )

        raise

def get_token_usage(response) -> dict:
    """
    Safely extract token usage from an OpenAI response.
    """

    usage = getattr(response, "usage", None)

    if usage is None:
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }

    return {
        "input_tokens": getattr(
            usage,
            "input_tokens",
            0,
        ),
        "output_tokens": getattr(
            usage,
            "output_tokens",
            0,
        ),
        "total_tokens": getattr(
            usage,
            "total_tokens",
            0,
        ),
    }

def ask_agent(question: str) -> str:
    """
    Answer an insurance analytics question using approved tools
    and record observability metrics.
    """

    request_id = str(uuid.uuid4())
    request_start = time.perf_counter()

    logger.info(
        "REQUEST_START | request_id=%s | question=%s",
        request_id,
        question,
    )

    # --------------------------------------------------------------
    # First LLM call - tool selection
    # --------------------------------------------------------------

    llm_start = time.perf_counter()

    response = client.responses.create(
        model="gpt-5-mini",
        instructions=(
            "You are an internal insurance analytics AI assistant. "

            "Use the available tools whenever company data is required. "
            "Never invent company statistics, claim information, policy "
            "information, procedures, documents, currencies, or system "
            "capabilities. "

            "Only claim access to information that is explicitly available "
            "through the provided tools. "

            "Do not assume a currency when the tool result does not "
            "provide one. "

            "Fraud probability and risk indicators are decision-support "
            "signals only and must never be presented as proof of fraud. "

            "If the user's question requires information that is not "
            "available through the provided tools, do not attempt to "
            "answer it. Clearly explain what information is missing."
        ),
        input=question,
        tools=TOOLS,
    )

    # IMPORTANT: this comes AFTER the API call
    first_usage = get_token_usage(response)

    llm_duration = (
        time.perf_counter() - llm_start
    ) * 1000

    logger.info(
        "LLM_CALL | request_id=%s | stage=tool_selection "
        "| duration_ms=%.2f | input_tokens=%d "
        "| output_tokens=%d | total_tokens=%d",
        request_id,
        llm_duration,
        first_usage["input_tokens"],
        first_usage["output_tokens"],
        first_usage["total_tokens"],
    )

    tool_calls = [
        item
        for item in response.output
        if item.type == "function_call"
    ]

    # --------------------------------------------------------------
    # No tool required
    # --------------------------------------------------------------

    if not tool_calls:

        answer = response.output_text

        if not answer or not answer.strip():
            answer = (
                "I cannot answer this question from the information "
                "available through the current tools."
            )

        total_duration = (
            time.perf_counter() - request_start
        ) * 1000

        logger.info(
            "REQUEST_COMPLETE | request_id=%s | duration_ms=%.2f "
            "| tool_count=0 | input_tokens=%d "
            "| output_tokens=%d | total_tokens=%d "
            "| success=True",
            request_id,
            total_duration,
            first_usage["input_tokens"],
            first_usage["output_tokens"],
            first_usage["total_tokens"],
        )

        return answer

    # --------------------------------------------------------------
    # Execute requested tools
    # --------------------------------------------------------------

    tool_outputs = []

    for tool_call in tool_calls:

        arguments = json.loads(
            tool_call.arguments
        )

        result = execute_tool(
            tool_name=tool_call.name,
            arguments=arguments,
            request_id=request_id,
        )

        tool_outputs.append(
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

    # --------------------------------------------------------------
    # Final LLM response
    # --------------------------------------------------------------

    llm_start = time.perf_counter()

    final_response = client.responses.create(
        model="gpt-5-mini",
        instructions=(
            "Answer the user's question using only information contained "
            "in the provided tool results. "

            "Do not invent or assume facts that are not present in those "
            "results. "

            "Do not invent company procedures, documents, currencies, "
            "teams, systems, or capabilities. "

            "If currency is not explicitly provided by a tool, display "
            "monetary values without a currency symbol. "

            "Clearly distinguish database facts from calculated risk "
            "indicators. "

            "Fraud probabilities and risk indicators are decision-support "
            "signals, not proof of fraud."
        ),
        previous_response_id=response.id,
        input=tool_outputs,
        tools=TOOLS,
    )

    # IMPORTANT: this also comes AFTER the API call
    final_usage = get_token_usage(final_response)

    final_llm_duration = (
        time.perf_counter() - llm_start
    ) * 1000

    logger.info(
        "LLM_CALL | request_id=%s | stage=final_response "
        "| duration_ms=%.2f | input_tokens=%d "
        "| output_tokens=%d | total_tokens=%d",
        request_id,
        final_llm_duration,
        final_usage["input_tokens"],
        final_usage["output_tokens"],
        final_usage["total_tokens"],
    )

    # --------------------------------------------------------------
    # Build final answer
    # --------------------------------------------------------------

    final_text = final_response.output_text

    if not final_text or not final_text.strip():
        final_text = (
            "I cannot answer this question from the information "
            "available through the current tools."
        )

    # --------------------------------------------------------------
    # Calculate total usage
    # --------------------------------------------------------------

    total_input_tokens = (
        first_usage["input_tokens"]
        + final_usage["input_tokens"]
    )

    total_output_tokens = (
        first_usage["output_tokens"]
        + final_usage["output_tokens"]
    )

    total_tokens = (
        first_usage["total_tokens"]
        + final_usage["total_tokens"]
    )

    total_duration = (
        time.perf_counter() - request_start
    ) * 1000

    # --------------------------------------------------------------
    # Final request log
    # --------------------------------------------------------------

    logger.info(
        "REQUEST_COMPLETE | request_id=%s | duration_ms=%.2f "
        "| tool_count=%d | input_tokens=%d "
        "| output_tokens=%d | total_tokens=%d "
        "| success=True",
        request_id,
        total_duration,
        len(tool_calls),
        total_input_tokens,
        total_output_tokens,
        total_tokens,
    )

    return final_text