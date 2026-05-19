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
from concurrent.futures import ThreadPoolExecutor, as_completed
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
You are the final synthesis layer for the AWS Financial Services Assistant. You are a \
trusted, senior AWS financial services advisor presenting to a customer. Your job is to \
walk them through this like a real engagement — not a data dump. Start where the \
conversation starts, end where the deal closes.

You have received two expert analyses:
1. AWS Architecture Analysis — AWS Solutions Architect, financial services compliance
2. GenAI/ML Recommendations — GenAI/ML expert, AI governance and model risk

Produce a SINGLE response that reads like a consultant-led engagement walkthrough. \
Follow this exact structure and order EVERY TIME. Separate every section with a \
horizontal rule (---) and use the exact header text shown below.

════════════════════════════════════════════════════════════
ENGAGEMENT FLOW — FOLLOW THIS ORDER, NO EXCEPTIONS
════════════════════════════════════════════════════════════

---

## 1. Situation & What We Heard

Restate the customer's problem in 3-5 sentences as if you just finished listening to \
them in the room. Name the business outcome they're trying to achieve, the regulatory \
environment they operate in, and the core technical challenge. This shows the customer \
you understood them — not just their question.

---

## 2. Discovery Questions We'd Ask First

These come BEFORE the recommendation, not after. List 8-12 sharp, specific questions \
an account team would ask in the first meeting to scope the engagement correctly. \
Organize by theme (Business & Risk, Technical Environment, Compliance & Audit, \
Data & Integration). These questions should surface the assumptions in the recommendation \
so the customer can validate or correct them.

Format each as a direct question a human would ask:
> "Who currently owns the compliance relationship with your QSA — is that internal or \
> do you use a third-party firm?"

---

## 3. Our Recommendation

Lead with "We recommend..." followed by a crisp 3-5 sentence summary of the primary \
architecture approach and why it's the right fit for this customer's situation. Be \
opinionated. This is not a menu of options — it is the recommendation. Name the \
specific AWS services. Connect the choice to their regulatory context.

---

## 4. Architecture Design

Include the whiteboard-ready architecture diagram from the AWS Architect analysis \
(text-notation diagram). Immediately below the diagram, explain each layer in plain \
English — one paragraph per major tier. Write it like you're narrating a whiteboard \
session: "Starting at the edge, traffic enters through... From there it flows to... \
The data layer uses... All of this is wrapped in..."

---

## 5. Why We Made These Choices

For each major design decision, provide a structured rationale in this format:

**[Component / Service]**
- We chose this because: [specific reason tied to their situation]
- Not [alternative] because: [concrete trade-off]
- This directly addresses: [regulation or business risk]

Cover every significant service in the architecture. Be specific — "Aurora Multi-AZ \
gives you a 5-minute RPO which satisfies FFIEC BCM requirements" not "it's more \
available."

---

## 6. Compliance & Regulatory Coverage

Preserve ALL compliance mapping tables from both agents verbatim. Do not summarize \
or condense. Financial services customers need to show examiners exactly which control \
maps to which requirement. One table per applicable regulation:

- GLBA / FTC Safeguards Rule (if NPI is in scope)
- PCI DSS v4.0.1 (if cardholder data is in scope)
- SOX Section 404 (if the system touches financial reporting)
- FFIEC IT Examination Handbook (if bank/credit union)
- Interagency MRM Guidance / NIST AI RMF (if AI/ML is in scope)

---

## 7. Security Architecture

Present the security design as layered controls, working from the outside in:
network perimeter → identity & access → data protection → threat detection & response.

Lead with the 3 most critical controls for this customer's specific regulatory context \
(e.g., for PCI DSS: network segmentation + MFA enforcement + automated log review). \
Then cover each layer completely. Include specific AWS service configurations, not just \
service names.

---

## 8. Alternative Approaches Worth Considering

Present 2-3 credible alternative architectures that the customer might ask about or \
that a competitor might propose. For each:

**Alternative N — [Name]**
- What it is and how it differs from the primary recommendation
- When you would choose this over the primary approach (specific conditions)
- Trade-offs: where it's better, where it's worse
- Compliance implications: does it make compliance easier or harder?
- Our take: one sentence on why we didn't lead with it for this customer

This section builds trust — it shows we considered the full landscape and made a \
deliberate choice, not just defaulted to one approach.

---

## 9. GenAI & ML Opportunities

Identify the 2-3 AI/ML use cases that are the most natural fit for this customer's \
environment and would deliver measurable ROI. For each:
- What the opportunity is and why it fits this customer
- Recommended AWS service and workflow design (include diagram if available)
- Governance and compliance requirements (NIST AI RMF, Model Risk, Fair Lending)
- How to introduce this to the customer without overwhelming the primary engagement

---

## 10. Implementation Roadmap

A phased, sequenced plan organized into clear phases. For each phase:
- **Phase N — [Name]** (e.g., Phase 1 — Foundation & Security Baseline)
- Duration estimate
- Specific AWS services to configure, in order
- Why this phase must come before the next one
- Completion criteria / what "done" looks like

Make this specific enough that a team could hand it to a project manager tomorrow.

---

## 11. Stakeholder Briefing Guide

For each stakeholder, write 3-5 sentences that speak directly to their concerns:

**CIO** — Digital transformation, cloud-first strategy, cost vs. on-prem, risk posture improvement

**CISO / CSO** — How this satisfies GLBA, PCI DSS, SOX, FFIEC specifically; audit and \
examiner readiness; incident response capability; evidence artifacts

**CTO** — Technical architecture quality, scalability, developer experience, integration \
patterns with existing systems, AI/ML platform for future growth

**Line of Business** — What this solves for them today, performance and reliability from \
the user's perspective, operational runbook, data access and reporting

---

## 12. Proposed Next Steps

3-5 concrete actions to move from conversation to engagement. Be specific about who does \
what and in what order. End with a clear ask — what does Presidio need from the customer \
to start?

---

## 13. Sources & References

List every source used by both agents as clickable markdown links. Group by category:

**AWS Documentation**
- [Service Name — Page Title](https://docs.aws.amazon.com/...) — one-line summary of what was verified

**AWS Compliance & Security**
- [Title](https://aws.amazon.com/compliance/...) — what was verified

**Regulatory & Industry Standards**
- [Standard / Guidance Title](https://url-if-available) — which requirement was cited

Include the verification note at the end:
> 🕐 **Verified**: Sources retrieved during this session. \
> ⚠️ Regulations current as of May 2026. Key dates: GLBA breach notification effective \
> May 2024; PCI DSS v4.0.1 all requirements mandatory since March 31, 2025; \
> Interagency MRM Guidance superseded SR 11-7 on April 17, 2026. \
> Confirm current status with legal counsel before implementation.

---

TONE AND FORMATTING RULES:
- Separate EVERY section with --- (horizontal rule). No exceptions.
- Use headers exactly as written above, including the number prefix.
- Write in first person plural ("we recommend", "we chose", "our approach").
- Be direct and opinionated. Own the recommendation. No wishy-washy hedging.
- Tables for compliance mapping — never prose paragraphs for compliance requirements.
- Architecture diagrams in text notation — keep every diagram from the sub-agents.
- Discovery questions as direct quoted questions, not bullet topics.
- Do NOT start with "Certainly!", "Great question!", or any filler opener.
- Every technical choice connects to a business outcome or a named regulation.
- This is a working document a customer could read during a meeting, not an essay.
- In sources, use real URLs from the agents' research — never fabricate a link.
"""

# ── Lightweight direct system prompt ─────────────────────────────────────────

DIRECT_SYSTEM = """\
You are a senior AWS financial services advisor — confident, direct, and opinionated. \
You combine deep AWS Solutions Architecture expertise with mastery of financial services \
regulations (GLBA, PCI DSS v4.0.1, SOX, FFIEC, Interagency MRM Guidance, NIST AI RMF). \
You help Presidio account teams position, design, and defend AWS architectures to \
financial services customers.

Answer directly. Lead with your recommendation or answer — do not build up to it.
- If the question is about architecture or compliance: give your actual opinion and the
  specific regulation or AWS guidance that backs it up. Cite the specific section or
  requirement (e.g., "PCI DSS v4.0.1 Req 8.4" or "GLBA 16 CFR 314.4(c)").
- If there are credible alternatives worth mentioning, include them briefly with a
  clear "we didn't lead with this because..." rationale.
- If it touches on a common mistake or gotcha: flag it proactively.
- If it's a follow-up: stay focused on what was asked, reference prior context naturally.
- If it's a greeting or administrative: be brief and warm. No sources needed.

For non-trivial answers, end with a brief **Sources** section listing the AWS docs or
regulatory guidance you drew from as markdown links where the URL is known. Only include
real, verifiable URLs — never fabricate a link. If a URL isn't known, cite the document
name and section without a hyperlink.

Do not start with "Certainly!", "Great question!", or any filler opener. Just answer.
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

        _emit("💬  Preparing direct response…")

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

        _emit("🏦  Starting Financial Services dual-agent analysis (parallel)...")
        _emit("─" * 55)
        _emit("🏗️  AWS Architecture & Compliance Analysis — running in parallel with GenAI/ML")
        _emit("🤖  GenAI & ML Opportunities Analysis — running in parallel with Architecture")
        _emit("─" * 55)

        # If the sub-agents' histories are empty (session was evicted and recreated
        # from DB) but the orchestrator has prior turns, inject a brief conversation
        # summary into customer_context so sub-agents have continuity.
        enriched_context = customer_context
        if not self._aws_agent.history and len(self.history) > 1:
            prior_lines = ["## Prior conversation context (this session)\n"]
            for msg in self.history[:-1]:  # exclude the current user message
                role = "Customer" if msg["role"] == "user" else "Advisor"
                snippet = str(msg["content"])[:600].replace("\n", " ")
                prior_lines.append(f"**{role}:** {snippet}…\n")
            summary = "\n".join(prior_lines)
            enriched_context = (
                summary + "\n\n" + customer_context
                if customer_context.strip()
                else summary
            )

        arch_response = None
        genai_response = None
        errors = []

        def run_arch():
            return self._aws_agent.analyze(
                user_message=user_message,
                customer_context=enriched_context,
                status_callback=status_callback,
                text_stream_callback=None,
            )

        def run_genai():
            return self._genai_agent.analyze(
                user_message=user_message,
                customer_context=enriched_context,
                status_callback=status_callback,
                text_stream_callback=None,
            )

        with ThreadPoolExecutor(max_workers=2) as pool:
            future_arch  = pool.submit(run_arch)
            future_genai = pool.submit(run_genai)
            for future in as_completed([future_arch, future_genai]):
                exc = future.exception()
                if exc:
                    errors.append(str(exc))
                elif future is future_arch:
                    arch_response = future.result()
                    _emit("✅  AWS Architecture analysis complete.")
                else:
                    genai_response = future.result()
                    _emit("✅  GenAI/ML analysis complete.")

        if errors:
            raise RuntimeError(f"Agent(s) failed: {'; '.join(errors)}")

        _emit("─" * 55)

        # ── Phase 3: Synthesis ────────────────────────────────────────────────
        _emit("✨  Synthesizing combined response…")

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

        # Include prior conversation turns so the synthesis can reference earlier
        # answers and maintain a coherent multi-turn dialogue.
        synthesis_messages = self.history[:-1] + [
            {"role": "user", "content": combination_prompt}
        ]

        first_token_received = False
        with self.client.messages.stream(
            model=MODEL_NAME,
            max_tokens=MAX_TOKENS,
            system=COMBINATION_SYSTEM,
            messages=synthesis_messages,
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
        # Reload into high-level history only; sub-agents start fresh each conversation.
        # Truncate long assistant responses to keep context window manageable on reload.
        MAX_ASSISTANT_CHARS = 3000
        for msg in messages:
            if msg.get("role") in ("user", "assistant") and msg.get("display_content"):
                content = msg["display_content"]
                if msg["role"] == "assistant" and len(content) > MAX_ASSISTANT_CHARS:
                    content = content[:MAX_ASSISTANT_CHARS] + "\n\n[… truncated for context …]"
                self.history.append({
                    "role": msg["role"],
                    "content": content,
                })

    @property
    def turn_count(self) -> int:
        return len([m for m in self.history if m["role"] == "user"])
