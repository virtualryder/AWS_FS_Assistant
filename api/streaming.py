"""
SSE Streaming Helpers

Bridges the synchronous Anthropic SDK (which runs in a ThreadPoolExecutor thread)
to FastAPI's async EventSourceResponse.

Pattern:
  1. Create an asyncio.Queue in the async context.
  2. Submit the synchronous agent call to the executor.
  3. The sync callbacks use run_coroutine_threadsafe to push events onto the queue.
  4. The async generator reads from the queue and yields SSE events.
  5. A "done" or "error" event signals the generator to stop.
"""

import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Shared thread pool — fine for I/O-bound agent calls
_executor = ThreadPoolExecutor(max_workers=8, thread_name_prefix="agent-worker")


def get_executor() -> ThreadPoolExecutor:
    return _executor


def make_callbacks(queue: asyncio.Queue, loop: asyncio.AbstractEventLoop):
    """
    Build status_callback and text_stream_callback that push SSE events
    onto an asyncio Queue from a background thread.
    """

    def status_callback(msg: str) -> None:
        asyncio.run_coroutine_threadsafe(
            queue.put({"type": "status", "text": msg}), loop
        )

    def text_stream_callback(token: str) -> None:
        asyncio.run_coroutine_threadsafe(
            queue.put({"type": "token", "text": token}), loop
        )

    return status_callback, text_stream_callback


async def run_in_executor_with_queue(
    fn,
    queue: asyncio.Queue,
    loop: asyncio.AbstractEventLoop,
    timeout: float = 300.0,
):
    """
    Run a synchronous callable in the thread pool.
    The callable should push its result (or an error) onto the queue itself
    using run_coroutine_threadsafe before returning.

    This coroutine drains the queue and yields SSE-compatible dicts until
    a "done" or "error" event is received.
    """
    _executor.submit(fn)

    while True:
        try:
            item = await asyncio.wait_for(queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            yield {"data": json.dumps({"type": "error", "text": "Request timed out"})}
            return

        yield {"data": json.dumps(item)}

        if item.get("type") in ("done", "error"):
            return


def build_agent_runner(agent, user_message: str, customer_context: str, queue, loop):
    """
    Build the synchronous function to submit to the executor.
    Puts a "done" or "error" event on the queue when finished.
    """

    def run():
        try:
            status_cb, token_cb = make_callbacks(queue, loop)
            result = agent.chat(
                user_message=user_message,
                customer_context=customer_context,
                status_callback=status_cb,
                text_stream_callback=token_cb,
            )
            asyncio.run_coroutine_threadsafe(
                queue.put({"type": "done", "text": result}), loop
            )
        except Exception as exc:
            logger.exception("Agent error for message: %.80s", user_message)
            asyncio.run_coroutine_threadsafe(
                queue.put({"type": "error", "text": str(exc)}), loop
            )

    return run


def build_discovery_runner(agent, customer_name, industry, website, notes, arch_context, queue, loop):
    """
    Build the synchronous function for the discovery agent to submit to the executor.
    """

    def run():
        try:
            status_cb, token_cb = make_callbacks(queue, loop)
            result = agent.generate_brief(
                customer_name=customer_name,
                industry=industry,
                website=website,
                notes=notes,
                arch_context=arch_context,
                status_callback=status_cb,
                text_stream_callback=token_cb,
            )
            asyncio.run_coroutine_threadsafe(
                queue.put({"type": "done", "text": result}), loop
            )
        except Exception as exc:
            logger.exception("Discovery agent error for: %s", customer_name)
            asyncio.run_coroutine_threadsafe(
                queue.put({"type": "error", "text": str(exc)}), loop
            )

    return run
