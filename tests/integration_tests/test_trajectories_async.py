"""
Tests that LLMs follows the right trajectories for certain critical task.
Follows LangChain AgentEvals method.
See https://github.com/langchain-ai/agentevals/blob/main/python/tests/test_trajectory_async.py
"""

import json
import pytest
from pathlib import Path
import sys
import asyncio

from agentevals.trajectory.match import create_async_trajectory_match_evaluator
from agentevals.types import EvaluatorResult

from simple_testing_agent import agent

# Add project root directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_compound_interest_trajectory():

    reference_outputs = [
        {
            "role": "user",
            "content": (
                "Can you tell me how much money will I get if I start with an initial balance of "
                "100 euros, and invest 50 euros monthly for 3 years at an interest rate of 8%?"
            ),
        },
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "function": {
                        "name": "compound_interest_calculator",
                        "arguments": json.dumps(
                            {
                                "initial_balance": 100,
                                "periodic_deposit": 50,
                                "deposit_frequency": "monthly",
                                "interest_rate": 8,
                                "years": 3,
                            }
                        ),
                    }
                }
            ],
        },
        {
            "role": "tool",
            "content": "",
        },
        {
            "role": "assistant",
            "content": "Resumen del cálculo de interés compuesto",
        },
    ]

    evaluator = create_async_trajectory_match_evaluator(
        trajectory_match_mode="superset"
    )

    inputs = {} #Not used, but needed in the api call. Leave empty.

    prompt = ("Can you tell me how much money will I get if I start with an initial balance of "
            "100 euros, and invest 50 euros monthly for 3 years at an interest rate of 8%?")

    result = agent.invoke({"messages": [{"role": "user", "content": prompt}]})
    print(f"RESULT: {result}")

    # Convert LangChain messages to AgentEvals format, which uses OpenAI style.
    def to_openai_dict(msg):
        role = msg.type if hasattr(msg, "type") else msg.__class__.__name__
        if role == "human":
            return {"role": "user", "content": msg.content}
        if role == "ai":
            tool_calls = None
            # LangChain stores possible tool_calls in additional_kwargs
            if hasattr(msg, "additional_kwargs") and msg.additional_kwargs:
                tool_calls = msg.additional_kwargs.get("tool_calls")
            d = {"role": "assistant", "content": msg.content or ""}
            if tool_calls:
                d["tool_calls"] = tool_calls
            return d
        if role == "tool":
            return {"role": "tool", "content": msg.content}
        # Generic allback
        return {"role": getattr(msg, "role", "assistant"), "content": getattr(msg, "content", "")}

    outputs = [to_openai_dict(m) for m in result["messages"]]
    print(f"OUTPUTS: {outputs}")

    evaluation = asyncio.run(
        evaluator(
            inputs={},
            outputs=outputs,
            reference_outputs=reference_outputs,
        )
    )
    print(f"EVALUATION: {evaluation}")

    assert evaluation.get("score") is True, f"Trajectory does not coincide."