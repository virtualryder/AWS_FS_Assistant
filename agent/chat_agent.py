"""
Financial Services Chat Agent — Orchestrator

Orchestrates two specialized sub-agents:
  1. AWSArchitectAgent  — AWS architecture with full compliance validation
  2. GenAIMLAgent       — GenAI/ML workflow opportunities with AI governance

The orchestrator runs both agents against the user's question (with the same customer
context) and combines their outputs into a unified, structured response.

For simple conversational questions (greetings, clarifications, non-architecture queries)
a lightweight single-pass Claude call is used instead of invoking both agents.
"""

import logging
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import anthropic

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import ANTHROPIC_API_KEY, MODEL_NAME, MAX_TOKENS
from agent.aws_architect_agent import AWSArchitectAgent
from agent.genai_ml_agent import GenAIMLAgent
from agent.tools import TOOLS
from agent.tool_executor import execute_tool

logger = logging.getLogger(__name__)

# ── Classifier system prompt ──────────────────────────────────────────────────
# Used to decide whether to run full dual-agent analysis or a lightweight answer.

CLASSIFIER_SYSTEM = """\
You are a routing classifier for an AWS Financial Services Assistant.
Given a user message, decide which response mode is most appropriate:

MODES:
A) FULL_ANALYSIS — Run both the AWS Architect Agent and the GenAI/ML Agent.
   Use for: architecture questions, design requests, solution recommendations,
   security/compliance questions, technology comparisons, "how do I build X",
   "what AWS services should I use for Y", financial services use cases.

B) QUICK_ANSWER — Answer directly without full dual-agent analysis.
   Use for: simple factual questions, clarifications, greetings, "what does X mean",
   follow-up questions on a topic already answered, very narrow questions
   that don't warrant a full architecture analysis.

Respond with ONLY the mode letter: A or B
"""

# ── Combination prompt ────────────────────────────────────────────────────────

COMBINATION_SYSTEM = """\
You are the final synthesis layer for the AWS Financial Services Assistant. You have
received two expert analyses for the same customer question:

1. AWS Architecture Analysis — from an AWS Solutions Architect specializing in
   financial services compliance (GLBA, PCI DSS, SOX, FFIEC, MRM Guidance, NIST AI RMF)

2. GenAI/ML Recommendations — from a GenAI and ML expert specializing in financial
   services AI governance (Bedrock, AgentCore, SageMaker, NIST AI RMF, Model Risk)

Your job is to produce a SINGLE, COHESIVE response that:
- Opens with an executive summary tying both perspectives together
- Preserves all technical depth from both analyses
- Removes any significant duplication (keep the most detailed version of each topic)
- Ensures the regulatory compliance sections are complete and accurate
- Maintains all source citations
- Ends with a unified discovery questions section (if either agent produced one)

Format the combined response with clear section headers distinguishing the two expert
perspectives. Use the label structure from both agents. Keep the whiteboard-ready
architecture diagram from the AWS Architect. Keep the AI workflow diagrams from the
GenAI/ML agent.

IMPORTANT: Do not lose any compliance requirements, regulatory citations, or
governance frameworks from either agent — these are the most critical parts.
"""

# ── Lightweight direct system prompt ─────────────────────────────────────────

DIRECT_SYSTEM = """\
You are an AWS Financial Services Assistant — a combined AWS Solutions Architect and
GenAI/ML expert specializing in financial services. You help Presidio account teams
with customer questions about AWS architectures, financial services compliance
(GLBA, PCI DSS, SOX, FFIEC, Model Risk Management), and AI/ML opportunities.

Answer the question directly and concisely. If the question touches on compliance,
regulations, or architecture — even briefly — note the relevant regulatory context.
If the question is a greeting or purely administrative, respond warmly but briefly.

Keep responses focused — the user is asking a quick clarifying question, not requesting
a full architecture analysis.
"""

CUSTOMER_CONTEXT_HEADER = """\
## Customer Context
{context}

---

## Question
"""


class FinServChatAgent:
    """
    Financial services assistant orchestrating AWS Architect + GenAI/ML agents.

    Usage:
        agent = FinServChatAgent()
        response = agent.chat(
            user_message="Design a secure document processing pipeline for mortgage...",
            customer_context="Regional bank, 50B AOR, OCC regulated...",
            status_callback=lambda msg: print(msg),
            text_stream_callback=lambda tok: print(tok, end="", flush=True),
        )
    """

    def __init__(self):
        if not ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY is not set. "
                "Copy .env.example to .env and add your key."
            )
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self._aws_agent = AWSArchitectAgent()
        self._genai_agent = GenAIMLAgent()
        self.history: list[dict] = []  # High-level conversation log for context

    # ── Routing ───────────────────────────────────────────────────────────────

    def _classify_message(self, message: str) -> str:
        """Return 'A' for full analysis, 'B' for quick answer."""
        try:
            resp = self.client.messages.create(
                model=MODEL_NAME,
                max_tokens=5,
                system=CLASSIFIER_SYSTEM,
                messages=[{"role": "user", "content": message}],
            )
            text = ""
            for block in resp.content:
                if hasattr(block, "text"):
                    text = block.text.strip().upper()
                    break
            return "A" if "A" in text else "B"
        except Exception as e:
            logger.warning("Classifier failed (%s), defaulting to full analysis.", e)
            return "A"

    # ── Quick direct answer ───────────────────────────────────────────────────

    def _quick_answer(
        self,
        user_message: str,
        customer_context: str,
        status_callback,
        text_stream_callback,
    ) -> str:
        def _emit(msg):
            if status_callback:
                status_callback(msg)

        _emit("💬  Preparing direct response...")
        _emit("⏳  Waiting for Claude to begin streaming…")

        if customer_context and customer_context.strip():
            full_message = (
                CUSTOMER_CONTEXT_HEADER.format(context=customer_context.strip())
                + user_message
            )
        else:
            full_message = user_message

        messages = self.history[:-1] + [{"role": "user", "content": full_message}]

        first_token_received = False
        with self.client.messages.stream(
            model=MODEL_NAME,
            max_tokens=4096,
            system=DIRECT_SYSTEM,
            messages=messages,
        ) as stream:
            for token in stream.text_stream:
                if not first_token_received:
                    _emit("📝  Streaming response…")
                    first_token_received = True
                if text_stream_callback:
                    text_stream_callback(token)
            response = stream.get_final_message()

        text = ""
        for block in response.content:
            if hasattr(block, "text"):
                text = block.text
                break
        return text

    # ── Full dual-agent analysis ──────────────────────────────────────────────

    def _full_analysis(
        self,
        user_message: str,
        customer_context: str,
        status_callback,
        text_stream_callback,
    ) -> str:
        def _emit(msg):
            if status_callback:
                status_callback(msg)

        _emit("🏦  Starting Financial Services dual-agent analysis...")
        _emit("─" * 55)

        # ── Phase 1: AWS Architect Agent ──────────────────────────────────────
        _emit("🏗️  Phase 1 of 2 — AWS Architecture & Compliance Analysis")
        _emit("─" * 55)

        arch_response = self._aws_agent.analyze(
            user_message=user_message,
            customer_context=customer_context,
            status_callback=status_callback,
            text_stream_callback=None,  # No streaming during research phase
        )
        _emit("✅  AWS Architecture analysis complete.")
        _emit("─" * 55)

        # ── Phase 2: GenAI/ML Agent ───────────────────────────────────────────
        _emit("🤖  Phase 2 of 2 — GenAI & ML Opportunities Analysis")
        _emit("─" * 55)

        genai_response = self._genai_agent.analyze(
            user_message=user_message,
            customer_context=customer_context,
            status_callback=status_callback,
            text_stream_callback=None,
        )
        _emit("✅  GenAI/ML analysis complete.")
        _emit("─" * 55)

        # ── Phase 3: Synthesis ────────────────────────────────────────────────
        _emit("✨  Synthesizing combined response...")
        _emit("⏳  Waiting for Claude to begin streaming…")

        combination_prompt = f"""\
Below are two expert analyses of the same customer question. Please synthesize them
into a single cohesive response following the instructions in your system prompt.

---
## AWS ARCHITECT ANALYSIS
{arch_response}

---
## GENAI/ML EXPERT ANALYSIS
{genai_response}
---

Customer Question (for reference): {user_message}
"""

        first_token_received = False
        with self.client.messages.stream(
            model=MODEL_NAME,
            max_tokens=MAX_TOKENS,
            system=COMBINATION_SYSTEM,
            messages=[{"role": "user", "content": combination_prompt}],
        ) as stream:
            for token in stream.text_stream:
                if not first_token_received:
                    _emit("📝  Streaming response…")
                    first_token_received = True
                if text_stream_callback:
                    text_stream_callback(token)
            response = stream.get_final_message()

        combined = ""
        for block in response.content:
            if hasattr(block, "text"):
                combined = block.text
                break
        return combined

    # ── Public chat interface ─────────────────────────────────────────────────

    def chat(
        self,
        user_message: str,
        customer_context: str = "",
        status_callback=None,
        text_stream_callback=None,
    ) -> str:
        """
        Send a message and return the assistant's response.

        For architecture/analysis questions: runs both specialized agents then synthesizes.
        For simple/conversational questions: responds directly.

        Args:
            user_message: The user's question.
            customer_context: Optional customer environment description.
            status_callback: Optional fn(str) called with status updates.
            text_stream_callback: Optional fn(str) called with streamed text tokens.
                Only fires during the final synthesis/direct-answer phase.

        Returns:
            The assistant's full response text.
        """
        def _emit(msg):
            if status_callback:
                status_callback(msg)

        # Checkpoint all three histories so any exception can be rolled back
        orch_checkpoint  = len(self.history)
        aws_checkpoint   = len(self._aws_agent.history)
        genai_checkpoint = len(self._genai_agent.history)

        self.history.append({"role": "user", "content": user_message})

        try:
            # Route: full analysis or quick answer?
            _emit("🔀  Routing question...")
            mode = self._classify_message(user_message)

            if mode == "A":
                response_text = self._full_analysis(
                    user_message, customer_context, status_callback, text_stream_callback
                )
            else:
                response_text = self._quick_answer(
                    user_message, customer_context, status_callback, text_stream_callback
                )

            self.history.append({"role": "assistant", "content": response_text})

            # Keep sub-agent histories in sync: if we ran full analysis, their histories
            # are already updated. For quick answers, sync a summary.
            if mode == "B":
                summary = f"[Quick answer provided for: {user_message[:100]}]"
                self._aws_agent.history.append({"role": "user", "content": summary})
                self._aws_agent.history.append({"role": "assistant", "content": response_text[:500]})
                self._genai_agent.history.append({"role": "user", "content": summary})
                self._genai_agent.history.append({"role": "assistant", "content": response_text[:500]})

        except Exception:
            # Roll back all three histories so no corrupt/partial turn is left behind
            self.history           = self.history[:orch_checkpoint]
            self._aws_agent.history   = self._aws_agent.history[:aws_checkpoint]
            self._genai_agent.history = self._genai_agent.history[:genai_checkpoint]
            raise

        return response_text

    def clear_history(self):
        """Reset all conversation history."""
        self.history = []
        self._aws_agent.clear_history()
        self._genai_agent.clear_history()

    def load_history(self, messages: list[dict]):
        """Load a prior conversation's display history for context continuity."""
        # Reload into high-level history only; sub-agents start fresh each conversation
        for msg in messages:
            if msg.get("role") in ("user", "assistant") and msg.get("display_content"):
                self.history.append({
                    "role": msg["role"],
                    "content": msg["display_content"],
                })

    @property
    def turn_count(self) -> int:
        return len([m for m in self.history if m["role"] == "user"])
