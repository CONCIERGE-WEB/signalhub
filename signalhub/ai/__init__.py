"""AI is NOT part of SignalHub Core.

Any LLM/embeddings consumer must live outside this package and call
Capabilities / REST / MCP as a client. Providers and Rule Engine never
import this module for decisions.
"""

from signalhub.ai.null import NullAI

__all__ = ["NullAI"]
