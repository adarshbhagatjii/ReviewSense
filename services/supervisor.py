# import os
# import json
# from typing import Any, Dict, List, Tuple

# from dotenv import load_dotenv
# from groq import Groq

# from services.mcp_tools import (
#     tool_get_review_by_id,
#     tool_get_reviews_by_country,
#     tool_get_reviews_by_rating,
#     tool_count_reviews,
#     tool_semantic_search,
#     tool_hybrid_search,
# )

# load_dotenv()


# # ============================================================
# # CONFIGURATION
# # ============================================================

# MODEL = os.getenv(
#     "GROQ_MODEL",
#     "openai/gpt-oss-20b"
# )

# MAX_ROUNDS = 2

# # Keep retrieved text compact to avoid huge Groq requests
# MAX_REVIEW_TEXT_CHARS = 250
# MAX_TOOL_RESULT_CHARS = 8500

# # Hard safety limits
# MAX_COUNTRY_LIMIT = 20
# MAX_SEMANTIC_K = 8
# MAX_HYBRID_K = 8


# # ============================================================
# # GROQ CLIENT
# # ============================================================

# client = Groq(
#     api_key=os.getenv("GROQ_API_KEY")
# )


# # ============================================================
# # TOOL SCHEMAS
# # ============================================================
# #
# # These descriptions are extremely important.
# #
# # The Python code does NOT decide which tool to use.
# # The LLM reads these descriptions and decides.
# #
# # ============================================================

# TOOL_SCHEMAS = [

#     {
#         "type": "function",
#         "function": {
#             "name": "get_review_by_id",
#             "description": (
#                 "Retrieve one exact Amazon review using its review ID. "
#                 "Use this whenever the user explicitly asks about a specific "
#                 "review ID, such as 'review 12283', 'what did review 500 say', "
#                 "or 'show review id 12283'."
#             ),
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "review_id": {
#                         "type": "integer",
#                         "description": "Exact review ID."
#                     }
#                 },
#                 "required": ["review_id"]
#             }
#         }
#     },

#     {
#         "type": "function",
#         "function": {
#             "name": "get_reviews_by_country",
#             "description": (
#                 "Retrieve reviews belonging to a specific country. "
#                 "Use for requests such as 'show US reviews', "
#                 "'show 10 UK reviews', or 'give me reviews from Germany'. "
#                 "If the user asks for multiple countries, make a separate "
#                 "tool call for EACH country in the same assistant response. "
#                 "Do not repeat an identical country call."
#             ),
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "country": {
#                         "type": "string",
#                         "description": "Country code such as US, UK, GB, IN."
#                     },
#                     "limit": {
#                         "type": "integer",
#                         "description": "Maximum number of reviews to return."
#                     }
#                 },
#                 "required": ["country"]
#             }
#         }
#     },

#     {
#         "type": "function",
#         "function": {
#             "name": "get_reviews_by_rating",
#             "description": (
#                 "Retrieve reviews filtered by star rating. "
#                 "Use for requests such as 'show 5 star reviews', "
#                 "'give me 1 star reviews', or 'show reviews rated 3'."
#             ),
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "rating": {
#                         "type": "integer",
#                         "description": "Star rating from 1 to 5."
#                     },
#                     "limit": {
#                         "type": "integer",
#                         "description": "Maximum number of reviews."
#                     }
#                 },
#                 "required": ["rating"]
#             }
#         }
#     },

#     {
#         "type": "function",
#         "function": {
#             "name": "count_reviews",
#             "description": (
#                 "Count reviews in the database. "
#                 "Use when the user asks how many reviews exist, "
#                 "how many reviews belong to a country, "
#                 "how many reviews have a particular rating, "
#                 "or another counting question."
#             ),
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "country": {
#                         "type": ["string", "null"],
#                         "description": (
#                             "Optional country code. "
#                             "Use null when no country filter exists."
#                         )
#                     },
#                     "rating": {
#                         "type": ["integer", "null"],
#                         "description": (
#                             "Optional star rating. "
#                             "Use null when no rating filter exists."
#                         )
#                     }
#                 },
#                 "required": []
#             }
#         }
#     },

#     {
#         "type": "function",
#         "function": {
#             "name": "semantic_search",
#             "description": (
#                 "Perform semantic vector search over Amazon reviews. "
#                 "Use when the user asks about meaning, opinions, experiences, "
#                 "complaints, themes, or topics rather than an exact structured "
#                 "filter. Examples: 'what do customers complain about?', "
#                 "'reviews mentioning bad refunds', "
#                 "'what do customers think about delivery?'"
#             ),
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "query": {
#                         "type": "string",
#                         "description": "Semantic search query."
#                     },
#                     "k": {
#                         "type": "integer",
#                         "description": "Number of relevant reviews."
#                     }
#                 },
#                 "required": ["query"]
#             }
#         }
#     },

#     {
#         "type": "function",
#         "function": {
#             "name": "hybrid_search",
#             "description": (
#                 "Perform hybrid retrieval using semantic similarity plus "
#                 "structured filters such as country or rating. "
#                 "Use when the user asks a semantic question while also "
#                 "specifying a country or rating. Examples: "
#                 "'what do US customers complain about regarding refunds?', "
#                 "'show negative UK reviews about delivery'."
#             ),
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "query": {
#                         "type": "string",
#                         "description": "Semantic search query."
#                     },
#                     "country": {
#                         "type": ["string", "null"],
#                         "description": "Optional country filter."
#                     },
#                     "rating": {
#                         "type": ["integer", "null"],
#                         "description": "Optional rating filter."
#                     },
#                     "k": {
#                         "type": "integer",
#                         "description": "Number of relevant reviews."
#                     }
#                 },
#                 "required": ["query"]
#             }
#         }
#     }
# ]


# # ============================================================
# # TOOL DISPATCH
# # ============================================================

# TOOL_DISPATCH = {
#     "get_review_by_id": tool_get_review_by_id,
#     "get_reviews_by_country": tool_get_reviews_by_country,
#     "get_reviews_by_rating": tool_get_reviews_by_rating,
#     "count_reviews": tool_count_reviews,
#     "semantic_search": tool_semantic_search,
#     "hybrid_search": tool_hybrid_search,
# }


# # ============================================================
# # SUPERVISOR SYSTEM PROMPT
# # ============================================================

# SYSTEM_PROMPT = """
# You are the Supervisor Agent for an Amazon Reviews RAG system.

# Your job is to decide which retrieval tool or tools should be used
# to answer the user's question.

# IMPORTANT:
# You are an agent.
# You must decide dynamically which tool is appropriate.
# Do NOT assume that Python code has already selected the correct tool.

# ============================================================
# CORE RULE
# ============================================================

# You MUST retrieve information before answering.

# Never answer using your own knowledge when the answer depends
# on the Amazon review dataset.

# Your final answer must be based only on retrieved database data.

# ============================================================
# TOOL SELECTION
# ============================================================

# Use get_review_by_id when the user asks about a specific review ID.

# Examples:

# "What did review 12283 say?"
# "Show review 500"
# "Tell me about review 12283"

# ------------------------------------------------------------

# Use get_reviews_by_country when the user asks for reviews
# from a specific country.

# Examples:

# "Show US reviews"
# "Give me 10 UK reviews"

# If the user asks for multiple countries, make separate tool calls
# for each country in the SAME tool-calling response.

# Example:

# "Show 10 UK and 10 US reviews"

# You should produce:

# get_reviews_by_country(country="UK", limit=10)

# AND

# get_reviews_by_country(country="US", limit=10)

# Do NOT call the same tool with the exact same arguments again.

# ------------------------------------------------------------

# Use get_reviews_by_rating when the user asks for reviews
# with a particular star rating.

# Example:

# "Show 10 five-star reviews"

# ------------------------------------------------------------

# Use count_reviews when the user asks for a number/count.

# Examples:

# "How many reviews are there?"
# "How many US reviews?"
# "How many 5 star reviews?"

# ------------------------------------------------------------

# Use semantic_search when the user asks about a topic,
# meaning, opinion, complaint, experience, or theme without
# structured filtering.

# Examples:

# "What are customers complaining about?"
# "What do customers think about refunds?"
# "Find reviews about bad delivery experiences"

# ------------------------------------------------------------

# Use hybrid_search when the user asks a semantic question
# AND includes structured filters.

# Examples:

# "What do US customers complain about regarding refunds?"

# "What do 1-star UK reviews say about delivery?"

# ============================================================
# MULTIPLE TOOL CALLS
# ============================================================

# If the question requires multiple independent datasets,
# call all necessary tools in the same response.

# Example:

# "Show 5 US reviews and 5 UK reviews"

# Call:

# 1. get_reviews_by_country(US, 5)
# 2. get_reviews_by_country(UK, 5)

# Do NOT retrieve US reviews, then retrieve US reviews again.

# ============================================================
# DUPLICATE PREVENTION
# ============================================================

# If a tool was already called with the exact same arguments,
# do not call it again.

# Use the existing retrieved data.

# ============================================================
# FINAL ANSWER
# ============================================================

# After retrieval, answer the user directly.

# Do not mention internal agent rounds.

# Do not mention tool names.

# Do not mention retrieval implementation.

# Do not invent review IDs, countries, ratings, counts,
# or review text.

# If the retrieved data does not contain the requested information,
# say that the requested information was not found.

# When the user asks to "show N reviews", try to show exactly N
# retrieved reviews when that many were returned.

# Keep answers clear and concise.
# """


# # ============================================================
# # REVIEW FORMATTER
# # ============================================================

# def _format_review(review: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Convert a database review into a compact representation.

#     Keeping the review body short helps reduce LLM request size.
#     """

#     review_copy = dict(review)

#     possible_text_fields = [
#         "review_text",
#         "text",
#         "review",
#         "body",
#         "content",
#     ]

#     for field in possible_text_fields:
#         if field in review_copy and review_copy[field]:
#             text = str(review_copy[field])

#             if len(text) > MAX_REVIEW_TEXT_CHARS:
#                 text = text[:MAX_REVIEW_TEXT_CHARS] + "..."

#             review_copy[field] = text

#     return review_copy


# # ============================================================
# # TOOL RESULT FORMATTER
# # ============================================================

# def _format_tool_result(result: Any) -> str:
#     """
#     Convert tool output into compact JSON for the LLM.
#     """

#     # --------------------------------------------------------
#     # COUNT RESULT
#     # --------------------------------------------------------

#     if isinstance(result, int):
#         return json.dumps({
#             "count": result
#         })

#     if isinstance(result, dict):

#         # Count-style response
#         if "count" in result and "rows" not in result:
#             return json.dumps(
#                 result,
#                 ensure_ascii=False
#             )

#         # Review rows
#         if "rows" in result:

#             rows = result.get("rows", [])

#             compact_rows = []

#             for row in rows:
#                 if isinstance(row, dict):
#                     compact_rows.append(
#                         _format_review(row)
#                     )
#                 else:
#                     compact_rows.append(row)

#             formatted = {
#                 "count": result.get(
#                     "count",
#                     len(compact_rows)
#                 ),
#                 "rows": compact_rows
#             }

#             output = json.dumps(
#                 formatted,
#                 ensure_ascii=False
#             )

#             if len(output) > MAX_TOOL_RESULT_CHARS:

#                 # progressively reduce review text
#                 smaller_rows = []

#                 for row in compact_rows:

#                     if isinstance(row, dict):
#                         row_copy = dict(row)

#                         for field in [
#                             "review_text",
#                             "text",
#                             "review",
#                             "body",
#                             "content",
#                         ]:
#                             if field in row_copy:
#                                 value = str(row_copy[field])

#                                 if len(value) > 100:
#                                     row_copy[field] = (
#                                         value[:100] + "..."
#                                     )

#                         smaller_rows.append(row_copy)

#                     else:
#                         smaller_rows.append(row)

#                 formatted["rows"] = smaller_rows

#                 output = json.dumps(
#                     formatted,
#                     ensure_ascii=False
#                 )

#             # Final hard cap
#             if len(output) > MAX_TOOL_RESULT_CHARS:
#                 output = output[:MAX_TOOL_RESULT_CHARS] + "..."

#             return output

#         return json.dumps(
#             result,
#             ensure_ascii=False
#         )

#     # --------------------------------------------------------
#     # LIST RESULT
#     # --------------------------------------------------------

#     if isinstance(result, list):

#         compact = []

#         for item in result:

#             if isinstance(item, dict):
#                 compact.append(
#                     _format_review(item)
#                 )
#             else:
#                 compact.append(item)

#         output = json.dumps(
#             compact,
#             ensure_ascii=False
#         )

#         if len(output) > MAX_TOOL_RESULT_CHARS:
#             output = (
#                 output[:MAX_TOOL_RESULT_CHARS]
#                 + "..."
#             )

#         return output

#     # --------------------------------------------------------
#     # STRING / OTHER
#     # --------------------------------------------------------

#     return str(result)


# # ============================================================
# # TOOL EXECUTION
# # ============================================================

# def _execute_tool_call(
#     tool_name: str,
#     arguments: Dict[str, Any]
# ) -> str:

#     print(
#         f"[tool] calling: {tool_name}({arguments})"
#     )

#     tool = TOOL_DISPATCH.get(tool_name)

#     if tool is None:

#         return json.dumps({
#             "error": f"Unknown tool: {tool_name}"
#         })

#     # --------------------------------------------------------
#     # SERVER-SIDE LIMITS
#     # --------------------------------------------------------

#     if tool_name == "get_reviews_by_country":

#         if "limit" in arguments:

#             arguments["limit"] = min(
#                 int(arguments["limit"]),
#                 MAX_COUNTRY_LIMIT
#             )

#     if tool_name == "get_reviews_by_rating":

#         if "limit" in arguments:

#             arguments["limit"] = min(
#                 int(arguments["limit"]),
#                 MAX_COUNTRY_LIMIT
#             )

#     if tool_name == "semantic_search":

#         if "k" in arguments:

#             arguments["k"] = min(
#                 int(arguments["k"]),
#                 MAX_SEMANTIC_K
#             )

#     if tool_name == "hybrid_search":

#         if "k" in arguments:

#             arguments["k"] = min(
#                 int(arguments["k"]),
#                 MAX_HYBRID_K
#             )

#     # --------------------------------------------------------
#     # EXECUTE
#     # --------------------------------------------------------

#     try:

#         result = tool(**arguments)

#         formatted = _format_tool_result(result)

#         # Logging only.
#         # Nothing here is displayed in the UI.

#         try:

#             parsed = json.loads(formatted)

#             if isinstance(parsed, dict):

#                 if "rows" in parsed:

#                     print(
#                         f"[tool] result: "
#                         f"count={parsed.get('count', 0)}, "
#                         f"rows={len(parsed.get('rows', []))}"
#                     )

#                 else:

#                     print(
#                         f"[tool] result: {parsed}"
#                     )

#             elif isinstance(parsed, list):

#                 print(
#                     f"[tool] result: "
#                     f"rows={len(parsed)}"
#                 )

#             else:

#                 print(
#                     f"[tool] result: {formatted[:500]}"
#                 )

#         except Exception:

#             print(
#                 f"[tool] result: {formatted[:500]}"
#             )

#         return formatted

#     except Exception as exc:

#         print(
#             f"[tool] ERROR in {tool_name}: {exc}"
#         )

#         return json.dumps({
#             "error": str(exc)
#         })


# # ============================================================
# # SAFE TOOL ARGUMENT PARSER
# # ============================================================

# def _parse_arguments(
#     raw_arguments: str
# ) -> Dict[str, Any]:

#     try:

#         parsed = json.loads(raw_arguments)

#         if not isinstance(parsed, dict):
#             return {}

#         return parsed

#     except Exception as exc:

#         print(
#             f"[supervisor] invalid tool arguments: {exc}"
#         )

#         return {}


# # ============================================================
# # MAIN SUPERVISOR
# # ============================================================

# def run_supervisor(
#     user_question: str,
#     chat_history: List[Dict[str, str]] | None = None
# ) -> str:

#     print(
#         f"[supervisor] question: {user_question}"
#     )

#     # --------------------------------------------------------
#     # INITIAL MESSAGES
#     # --------------------------------------------------------

#     messages: List[Dict[str, Any]] = [
#         {
#             "role": "system",
#             "content": SYSTEM_PROMPT
#         }
#     ]

#     # --------------------------------------------------------
#     # OPTIONAL CHAT HISTORY
#     # --------------------------------------------------------

#     if chat_history:

#         # Keep only recent history to control token usage.
#         recent_history = chat_history[-6:]

#         for item in recent_history:

#             role = item.get("role")

#             content = item.get("content")

#             if role in ["user", "assistant"] and content:

#                 messages.append({
#                     "role": role,
#                     "content": content
#                 })

#     # --------------------------------------------------------
#     # CURRENT QUESTION
#     # --------------------------------------------------------

#     messages.append({
#         "role": "user",
#         "content": user_question
#     })

#     # --------------------------------------------------------
#     # DUPLICATE CALL TRACKING
#     # --------------------------------------------------------

#     executed_calls: set[Tuple[str, str]] = set()

#     tools_used: List[str] = []

#     # --------------------------------------------------------
#     # AGENT LOOP
#     # --------------------------------------------------------

#     for round_number in range(
#         1,
#         MAX_ROUNDS + 1
#     ):

#         # ----------------------------------------------------
#         # ROUND 1
#         # ----------------------------------------------------
#         #
#         # Retrieval is mandatory.
#         #
#         # ----------------------------------------------------

#         if round_number == 1:

#             tool_choice = "required"

#         # ----------------------------------------------------
#         # ROUND 2
#         # ----------------------------------------------------
#         #
#         # Model should now use retrieved data and answer.
#         #
#         # "none" prevents another retrieval call.
#         #
#         # ----------------------------------------------------

#         else:

#             tool_choice = "none"

#         print(
#             f"[supervisor] "
#             f"round {round_number}/{MAX_ROUNDS} "
#             f"— tool_choice={tool_choice}"
#         )

#         # ----------------------------------------------------
#         # GROQ REQUEST
#         # ----------------------------------------------------

#         try:

#             response = client.chat.completions.create(

#                 model=MODEL,

#                 messages=messages,

#                 tools=TOOL_SCHEMAS,

#                 tool_choice=tool_choice,

#                 temperature=0,

#                 max_tokens=1000,
#             )

#         except Exception as exc:

#             print(
#                 f"[supervisor] Groq error: {exc}"
#             )

#             return (
#                 "Sorry, I couldn't process the request "
#                 "because the AI service returned an error."
#             )

#         # ----------------------------------------------------
#         # RESPONSE MESSAGE
#         # ----------------------------------------------------

#         message = response.choices[0].message

#         finish_reason = (
#             response.choices[0].finish_reason
#         )

#         tool_calls = (
#             getattr(message, "tool_calls", None)
#             or []
#         )

#         # ----------------------------------------------------
#         # LOGGING
#         # ----------------------------------------------------

#         usage = getattr(
#             response,
#             "usage",
#             None
#         )

#         if usage:

#             print(
#                 f"[llm] finish_reason={finish_reason}, "
#                 f"tool_calls={len(tool_calls)}, "
#                 f"tokens="
#                 f"{getattr(usage, 'prompt_tokens', 0)}/"
#                 f"{getattr(usage, 'completion_tokens', 0)}/"
#                 f"{getattr(usage, 'total_tokens', 0)}"
#             )

#         else:

#             print(
#                 f"[llm] finish_reason={finish_reason}, "
#                 f"tool_calls={len(tool_calls)}"
#             )

#         # ----------------------------------------------------
#         # NO TOOL CALL
#         # ----------------------------------------------------

#         if not tool_calls:

#             final_answer = (
#                 message.content or
#                 "I couldn't generate an answer."
#             )

#             print(
#                 "[supervisor] final answer generated"
#             )

#             return final_answer

#         # ----------------------------------------------------
#         # ADD ASSISTANT TOOL CALL MESSAGE
#         # ----------------------------------------------------

#         assistant_tool_message = {
#             "role": "assistant",
#             "content": message.content or "",
#             "tool_calls": []
#         }

#         # Groq/OpenAI tool-call objects need to be converted
#         # into normal dictionaries before sending them back.

#         for tool_call in tool_calls:

#             assistant_tool_message[
#                 "tool_calls"
#             ].append({

#                 "id": tool_call.id,

#                 "type": "function",

#                 "function": {

#                     "name": tool_call.function.name,

#                     "arguments": (
#                         tool_call.function.arguments
#                     )
#                 }
#             })

#         messages.append(
#             assistant_tool_message
#         )

#         # ----------------------------------------------------
#         # EXECUTE TOOL CALLS
#         # ----------------------------------------------------

#         for tool_call in tool_calls:

#             name = tool_call.function.name

#             raw_arguments = (
#                 tool_call.function.arguments
#             )

#             arguments = _parse_arguments(
#                 raw_arguments
#             )

#             print(
#                 f"[llm] tool call: "
#                 f"{name} args={arguments}"
#             )

#             # ------------------------------------------------
#             # DUPLICATE DETECTION
#             # ------------------------------------------------

#             normalized_arguments = json.dumps(
#                 arguments,
#                 sort_keys=True
#             )

#             call_key = (
#                 name,
#                 normalized_arguments
#             )

#             if call_key in executed_calls:

#                 print(
#                     f"[supervisor] "
#                     f"duplicate tool call skipped: "
#                     f"{name}({arguments})"
#                 )

#                 result = json.dumps({
#                     "error": (
#                         "This exact tool call was already "
#                         "executed. Use the previously retrieved "
#                         "data instead of repeating the call."
#                     )
#                 })

#             else:

#                 executed_calls.add(
#                     call_key
#                 )

#                 result = _execute_tool_call(
#                     name,
#                     arguments
#                 )

#                 if name not in tools_used:

#                     tools_used.append(name)

#             # ------------------------------------------------
#             # RETURN TOOL RESULT TO LLM
#             # ------------------------------------------------

#             messages.append({

#                 "role": "tool",

#                 "tool_call_id": tool_call.id,

#                 "content": result
#             })

#     # ========================================================
#     # SAFETY FALLBACK
#     # ========================================================

#     print(
#         "[supervisor] maximum rounds reached"
#     )

#     return (
#         "I retrieved the relevant information, "
#         "but I couldn't complete the final response."
#     )
















import os
import json
import re
from typing import Any, Dict, List, Tuple, Optional

from dotenv import load_dotenv
from groq import Groq

from services.mcp_tools import (
    tool_get_review_by_id,
    tool_get_reviews_by_country,
    tool_get_reviews_by_rating,
    tool_count_reviews,
    tool_semantic_search,
    tool_hybrid_search,
)

load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)

# Maximum number of LLM -> tool -> LLM cycles
MAX_ROUNDS = 3

# Maximum records requested by the agent
MAX_RECORD_LIMIT = 20

# Semantic retrieval limits
MAX_SEMANTIC_K = 8
MAX_HYBRID_K = 8

# Maximum review text sent to LLM for ANALYSIS requests
MAX_ANALYSIS_TEXT_CHARS = 500

# Maximum total retrieved context sent to LLM
MAX_LLM_CONTEXT_CHARS = 9000


# ============================================================
# GROQ CLIENT
# ============================================================

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# ============================================================
# TOOL SCHEMAS
# ============================================================

TOOL_SCHEMAS = [

    # --------------------------------------------------------
    # GET REVIEW BY ID
    # --------------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "get_review_by_id",
            "description": (
                "Retrieve one exact Amazon review using its review ID. "
                "Use this whenever the user explicitly mentions a review ID "
                "or asks about a specific review."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "review_id": {
                        "type": "integer",
                        "description": "Exact review ID."
                    }
                },
                "required": ["review_id"]
            }
        }
    },

    # --------------------------------------------------------
    # GET REVIEWS BY COUNTRY
    # --------------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "get_reviews_by_country",
            "description": (
                "Retrieve reviews from a specific country. "
                "Use for requests such as 'show US reviews', "
                "'show 10 US reviews', or 'list UK reviews'. "
                "If multiple countries are requested, make one "
                "tool call for each country in the same response."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {
                        "type": "string",
                        "description": (
                            "Country code stored in the database, "
                            "such as US, GB, IN."
                        )
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of reviews requested."
                    }
                },
                "required": ["country"]
            }
        }
    },

    # --------------------------------------------------------
    # GET REVIEWS BY RATING
    # --------------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "get_reviews_by_rating",
            "description": (
                "Retrieve reviews using their star rating. "
                "Use for requests such as 'show 10 five star reviews', "
                "'show 1 star reviews', or 'list 3-star reviews'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "rating": {
                        "type": "integer",
                        "description": "Star rating from 1 to 5."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of reviews requested."
                    }
                },
                "required": ["rating"]
            }
        }
    },

    # --------------------------------------------------------
    # COUNT
    # --------------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "count_reviews",
            "description": (
                "Count reviews in the database. "
                "Use when the user asks how many reviews exist, "
                "how many reviews are from a country, "
                "or how many reviews have a particular rating."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {
                        "type": ["string", "null"],
                        "description": "Optional country code."
                    },
                    "rating": {
                        "type": ["integer", "null"],
                        "description": "Optional star rating."
                    }
                }
            }
        }
    },

    # --------------------------------------------------------
    # SEMANTIC SEARCH
    # --------------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "semantic_search",
            "description": (
                "Perform semantic vector search over Amazon reviews. "
                "Use when the user asks about opinions, complaints, "
                "themes, experiences, or topics without a structured "
                "country/rating filter."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Semantic search query."
                    },
                    "k": {
                        "type": "integer",
                        "description": "Number of results."
                    }
                },
                "required": ["query"]
            }
        }
    },

    # --------------------------------------------------------
    # HYBRID SEARCH
    # --------------------------------------------------------

    {
        "type": "function",
        "function": {
            "name": "hybrid_search",
            "description": (
                "Perform semantic search with structured filtering. "
                "Use when the user asks a semantic question and also "
                "specifies country or rating. "
                "Example: 'What do US customers complain about refunds?'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Semantic search query."
                    },
                    "country": {
                        "type": ["string", "null"],
                        "description": "Optional country filter."
                    },
                    "rating": {
                        "type": ["integer", "null"],
                        "description": "Optional rating filter."
                    },
                    "k": {
                        "type": "integer",
                        "description": "Number of results."
                    }
                },
                "required": ["query"]
            }
        }
    },
]


# ============================================================
# TOOL DISPATCH
# ============================================================

TOOL_DISPATCH = {
    "get_review_by_id": tool_get_review_by_id,
    "get_reviews_by_country": tool_get_reviews_by_country,
    "get_reviews_by_rating": tool_get_reviews_by_rating,
    "count_reviews": tool_count_reviews,
    "semantic_search": tool_semantic_search,
    "hybrid_search": tool_hybrid_search,
}


# ============================================================
# SUPERVISOR PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are the Supervisor Agent for an Amazon Reviews RAG system.

Your responsibility is to decide which retrieval tool or tools
should be used to answer the user's question.

You are an AGENT.

Python does not decide which tool to use.
You must decide dynamically based on the user's intent.

============================================================
GENERAL RULE
============================================================

You MUST retrieve database information before answering.

Never use your own knowledge for information about Amazon reviews.

Your answer must be grounded in retrieved database information.

When a search tool already returns review text,
DO NOT call get_review_by_id unless the user
explicitly requests a specific review.

For analysis questions,
use the retrieved reviews directly and answer.

============================================================
NEVER ASK FOR CLARIFICATION
============================================================

You MUST always call a tool.

Never ask the user to clarify or provide more details.

If the question is vague or broad, make a reasonable
assumption and call the most appropriate tool.

Examples of how to handle vague questions:

- "What do customers from different countries say?"
  → call semantic_search(query="customer reviews", limit=20)
    OR call hybrid_search for a few key countries
  → do NOT ask "which country?"

- "What are people saying?"
  → call semantic_search(query="customer experience", limit=10)

- "Tell me about reviews"
  → call semantic_search(query="Amazon reviews", limit=10)

When in doubt, default to semantic_search with a broad query.

============================================================
TOOL SELECTION
============================================================

1. SPECIFIC REVIEW ID

Use get_review_by_id when the user mentions a specific review ID.

Examples:

"What did review 12283 say?"
"Show review 500"
"Give me details for review 12283"

------------------------------------------------------------

2. COUNTRY

Use get_reviews_by_country when the user asks for reviews
from a particular country.

Examples:

"Show US reviews"
"Show 10 US reviews"
"List UK reviews"

If multiple countries are requested, make separate calls
for each country in the SAME response.

Example:

"Show 10 US and 10 UK reviews"

Call:

get_reviews_by_country(US, 10)

AND

get_reviews_by_country(UK, 10)

Do not call the same tool with identical arguments twice.

------------------------------------------------------------

3. RATING

Use get_reviews_by_rating when the user asks for reviews
with a specific rating.

Example:

"Show 10 five-star reviews"

------------------------------------------------------------

4. COUNT

Use count_reviews when the user asks for a count.

Examples:

"How many reviews are there?"

"How many US reviews?"

"How many 5-star reviews?"

------------------------------------------------------------

5. SEMANTIC SEARCH

Use semantic_search when the user asks about:

- opinions
- complaints
- experiences
- themes
- topics
- meaning

without a country/rating filter.

Example:

"What are customers complaining about?"

"What do customers think about refunds?"

------------------------------------------------------------

6. HYBRID SEARCH

Use hybrid_search when the user asks a semantic question
AND specifies a structured filter such as country or rating.

Example:

"What do US customers complain about refunds?"

"What do 1-star UK customers say about delivery?"

============================================================
DISPLAY REQUESTS
============================================================

A DISPLAY REQUEST means the user asks to:

- show reviews
- list reviews
- display reviews
- give reviews
- show ticket details
- show review details
- list ticket details

For DISPLAY REQUESTS, the application will handle the
full review text outside the LLM.

Therefore, when answering a display request:

The retrieved metadata contains:

- review ID
- rating
- title
- reviewer
- date

Do NOT invent review text.

Do NOT reproduce long review text in your answer.

The application will attach the original review text
after your response.

Your response should contain only the metadata.

Use this format:

**Review ID:** <id>
**Rating:** <rating>★
**Title:** <title>
**Reviewer:** <reviewer>
**Date:** <date>

============================================================
ANALYSIS REQUESTS
============================================================

If the user asks you to:

- summarize
- analyze
- compare
- identify complaints
- identify common issues
- find themes
- explain what customers say

then review text is required.

For analysis requests, use the retrieved review text
provided in the tool context.

============================================================
EXACT NUMBER
============================================================

If the user asks:

"Show 10 US reviews"

and the tool returns 10 reviews,

the final answer must contain all 10 reviews.

Do not silently reduce the number.

============================================================
DUPLICATE CALLS
============================================================

Never repeat an identical tool call.

If:

get_reviews_by_country(US, 10)

was already executed,

do not execute:

get_reviews_by_country(US, 10)

again.

============================================================
FINAL ANSWER
============================================================

Do not mention:

- tool names
- agent rounds
- internal implementation
- retrieval process
- Python
- PostgreSQL
- pgvector

Just answer the user.

Do not add a retrieval footer.
"""


# ============================================================
# DETECT DISPLAY REQUEST
# ============================================================

def _is_display_request(question: str) -> bool:
    """
    Detect whether the user wants records displayed rather than
    analyzed.

    This is NOT tool routing.

    The Supervisor still decides the retrieval tool.

    This only determines how much information we need to give
    the LLM and how the final response should be assembled.
    """

    text = question.lower().strip()

    display_patterns = [
        "show ",
        "show me ",
        "list ",
        "display ",
        "give me ",
        "ticket details",
        "review details",
        "reviews",
    ]

    analysis_patterns = [
        "summarize",
        "summary",
        "analyze",
        "analysis",
        "compare",
        "common issue",
        "common issues",
        "top issues",
        "complaints",
        "themes",
        "what do customers think",
        "what are customers saying",
        "why",
    ]

    has_display = any(
        pattern in text
        for pattern in display_patterns
    )

    has_analysis = any(
        pattern in text
        for pattern in analysis_patterns
    )

    # Analysis takes priority.
    if has_analysis:
        return False

    return has_display


# ============================================================
# EXTRACT REVIEW RECORDS
# ============================================================

def _extract_records(result: Any) -> List[Dict[str, Any]]:
    """
    Extract original database records from tool output.
    """

    if isinstance(result, dict):

        if "results" in result:

            results = result["results"]

            if isinstance(results, list):
                return [
                    item
                    for item in results
                    if isinstance(item, dict)
                ]

        if "rows" in result:

            rows = result["rows"]

            if isinstance(rows, list):
                return [
                    item
                    for item in rows
                    if isinstance(item, dict)
                ]

        # Single review
        if "id" in result:

            return [result]

    elif isinstance(result, list):

        return [
            item
            for item in result
            if isinstance(item, dict)
        ]

    return []


# ============================================================
# METADATA ONLY
# ============================================================

def _metadata_for_llm(
    records: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Remove review_text before sending display-request
    information to the LLM.
    """

    metadata = []

    for record in records:

        metadata.append({

            "id": record.get("id"),

            "rating": record.get("rating"),

            "review_title": record.get(
                "review_title"
            ),

            "reviewer_name": record.get(
                "reviewer_name"
            ),

            "review_date": record.get(
                "review_date"
            ),
        })

    return metadata


# ============================================================
# COMPACT ANALYSIS RECORDS
# ============================================================

def _records_for_analysis(
    records: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    For analysis requests, provide review text to the LLM,
    but keep it bounded to protect the context window.
    """

    output = []

    for record in records:

        item = {

            "id": record.get("id"),

            "country": record.get(
                "country"
            ),

            "rating": record.get(
                "rating"
            ),

            "review_title": record.get(
                "review_title"
            ),

            "review_text": record.get(
                "review_text",
                ""
            ),

        }

        text = str(
            item["review_text"] or ""
        )

        if len(text) > MAX_ANALYSIS_TEXT_CHARS:

            text = (
                text[:MAX_ANALYSIS_TEXT_CHARS]
                + "..."
            )

        item["review_text"] = text

        output.append(item)

    return output


# ============================================================
# FORMAT TOOL RESULT FOR LLM
# ============================================================

def _format_tool_result_for_llm(
    result: Any,
    display_request: bool
) -> str:
    """
    IMPORTANT:

    DISPLAY REQUEST:
        Only metadata goes to LLM.

    ANALYSIS REQUEST:
        Review text is included, but truncated.
    """

    records = _extract_records(result)

    # --------------------------------------------------------
    # COUNT
    # --------------------------------------------------------

    if isinstance(result, int):

        return json.dumps({
            "count": result
        })

    if isinstance(result, dict):

        # Pure count response
        if (
            "count" in result
            and not records
        ):

            return json.dumps(
                {
                    "count": result.get(
                        "count"
                    )
                },
                ensure_ascii=False
            )

    # --------------------------------------------------------
    # DISPLAY REQUEST
    # --------------------------------------------------------

    if display_request:

        metadata = _metadata_for_llm(
            records
        )

        output = {
            "count": len(records),
            "records": metadata
        }

        return json.dumps(
            output,
            ensure_ascii=False
        )

    # --------------------------------------------------------
    # ANALYSIS REQUEST
    # --------------------------------------------------------

    analysis_records = _records_for_analysis(
        records
    )

    output = {
        "count": len(analysis_records),
        "records": analysis_records
    }

    serialized = json.dumps(
        output,
        ensure_ascii=False
    )

    # --------------------------------------------------------
    # HARD CONTEXT LIMIT
    # --------------------------------------------------------

    if len(serialized) > MAX_LLM_CONTEXT_CHARS:

        serialized = serialized[
            :MAX_LLM_CONTEXT_CHARS
        ] + "..."

    return serialized


# ============================================================
# FORMAT FINAL DISPLAY RESPONSE
# ============================================================

def _format_display_records(
    records: List[Dict[str, Any]]
) -> str:
    """
    Build the final UI response from the ORIGINAL database
    records.

    The review text is attached here, NOT generated by LLM.
    """

    if not records:

        return "No reviews were found."

    sections = []

    for record in records:

        review_id = record.get(
            "id",
            "N/A"
        )

        rating = record.get(
            "rating",
            "N/A"
        )

        title = record.get(
            "review_title",
            "N/A"
        )

        reviewer = record.get(
            "reviewer_name",
            "N/A"
        )

        review_date = record.get(
            "review_date",
            "N/A"
        )

        review_text = record.get(
            "review_text",
            ""
        )

        # ----------------------------------------------------
        # DATE
        # ----------------------------------------------------

        if review_date:

            date_string = str(
                review_date
            )

            # Convert:
            # 2024-09-16T13:44:26.000Z
            # ->
            # 2024-09-16

            if "T" in date_string:

                date_string = (
                    date_string.split("T")[0]
                )

        else:

            date_string = "N/A"

        # ----------------------------------------------------
        # BUILD RECORD
        # ----------------------------------------------------

        section = (
            f"**Review ID:** {review_id}\n"
            f"**Rating:** {rating}★\n"
            f"**Title:** {title}\n"
            f"**Reviewer:** {reviewer}\n"
            f"**Date:** {date_string}\n"
            f"**Text:** {review_text}"
        )

        sections.append(section)

    return "\n\n".join(
        sections
    )


# ============================================================
# PARSE TOOL ARGUMENTS
# ============================================================

def _parse_arguments(
    raw_arguments: str
) -> Dict[str, Any]:

    try:

        arguments = json.loads(
            raw_arguments
        )

        if not isinstance(
            arguments,
            dict
        ):
            return {}

        return arguments

    except Exception as exc:

        print(
            f"[supervisor] "
            f"argument parsing error: {exc}"
        )

        return {}


# ============================================================
# NORMALIZE TOOL ARGUMENTS
# ============================================================

def _normalize_arguments(
    tool_name: str,
    arguments: Dict[str, Any]
) -> Dict[str, Any]:

    args = dict(arguments)

    # --------------------------------------------------------
    # COUNTRY
    # --------------------------------------------------------

    if tool_name == "get_reviews_by_country":

        if "country" in args:

            args["country"] = str(
                args["country"]
            ).upper().strip()

        if "limit" in args:

            try:

                args["limit"] = min(
                    int(args["limit"]),
                    MAX_RECORD_LIMIT
                )

            except Exception:

                args["limit"] = 10

    # --------------------------------------------------------
    # RATING
    # --------------------------------------------------------

    elif tool_name == "get_reviews_by_rating":

        if "rating" in args:

            args["rating"] = int(
                args["rating"]
            )

        if "limit" in args:

            try:

                args["limit"] = min(
                    int(args["limit"]),
                    MAX_RECORD_LIMIT
                )

            except Exception:

                args["limit"] = 10

    # --------------------------------------------------------
    # SEMANTIC
    # --------------------------------------------------------

    elif tool_name == "semantic_search":

        if "k" in args:

            try:

                args["k"] = min(
                    int(args["k"]),
                    MAX_SEMANTIC_K
                )

            except Exception:

                args["k"] = MAX_SEMANTIC_K

    # --------------------------------------------------------
    # HYBRID
    # --------------------------------------------------------

    elif tool_name == "hybrid_search":

        if "k" in args:

            try:

                args["k"] = min(
                    int(args["k"]),
                    MAX_HYBRID_K
                )

            except Exception:

                args["k"] = MAX_HYBRID_K

        if args.get("country"):

            args["country"] = str(
                args["country"]
            ).upper().strip()

    return args


# ============================================================
# EXECUTE TOOL
# ============================================================

def _execute_tool(
    tool_name: str,
    arguments: Dict[str, Any]
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Returns:

        (
            raw/serialized result,
            original database records
        )
    """

    print(
        f"[tool] calling: "
        f"{tool_name}({arguments})"
    )

    tool = TOOL_DISPATCH.get(
        tool_name
    )

    if tool is None:

        error = {
            "error": (
                f"Unknown tool: {tool_name}"
            )
        }

        return (
            json.dumps(error),
            []
        )

    try:

        result = tool(
            **arguments
        )

        records = _extract_records(
            result
        )

        print(
            f"[tool] result: "
            f"records={len(records)}"
        )

        return (
            result,
            records
        )

    except Exception as exc:

        print(
            f"[tool] ERROR: "
            f"{tool_name}: {exc}"
        )

        return (
            {
                "error": str(exc)
            },
            []
        )


# ============================================================
# MAIN SUPERVISOR
# ============================================================

def run_supervisor(
    user_question: str,
    chat_history: Optional[
        List[Dict[str, str]]
    ] = None
) -> str:

    print(
        f"[supervisor] "
        f"question: {user_question}"
    )

    # ========================================================
    # DETERMINE PRESENTATION MODE
    # ========================================================
    #
    # This DOES NOT decide the retrieval tool.
    #
    # The LLM still decides the retrieval tool.
    #
    # This only decides whether full review text should be
    # passed to the LLM.
    #
    # ========================================================

    display_request = _is_display_request(
        user_question
    )

    print(
        f"[supervisor] "
        f"display_request={display_request}"
    )

    # ========================================================
    # MESSAGES
    # ========================================================

    messages: List[Dict[str, Any]] = [

        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    # ========================================================
    # CHAT HISTORY
    # ========================================================

    if chat_history:

        recent_history = (
            chat_history[-6:]
        )

        for item in recent_history:

            role = item.get(
                "role"
            )

            content = item.get(
                "content"
            )

            if (
                role in [
                    "user",
                    "assistant"
                ]
                and content
            ):

                messages.append({

                    "role": role,

                    "content": content
                })

    # ========================================================
    # CURRENT QUESTION
    # ========================================================

    messages.append({

        "role": "user",

        "content": user_question
    })

    # ========================================================
    # DUPLICATE TRACKING
    # ========================================================

    executed_calls: set[
        Tuple[str, str]
    ] = set()

    # ========================================================
    # ORIGINAL RECORDS
    # ========================================================
    #
    # These never have to be sent to the LLM for display
    # requests.
    #
    # ========================================================

    retrieved_records: List[
        Dict[str, Any]
    ] = []

    # ========================================================
    # TOOL LOOP
    # ========================================================

    for round_num in range(1, MAX_ROUNDS + 1):

        if round_num == 1:
            tool_choice = "required"
        else:
            tool_choice = "auto"

        print(
            f"[supervisor] "
            f"round {round_num}/{MAX_ROUNDS} "
            f"— tool_choice={tool_choice}"
        )

        # ====================================================
        # LLM CALL
        # ====================================================

        try:

            response = client.chat.completions.create(

                model=MODEL,

                messages=messages,

                tools=TOOL_SCHEMAS,

                tool_choice=tool_choice,

                temperature=0,

                # More room for final metadata,
                # while still keeping the request controlled.
                max_tokens=1800,
            )

        except Exception as exc:

            exc_str = str(exc)

            # ------------------------------------------------
            # GROQ tool_choice=required FAILURE RECOVERY
            #
            # When tool_choice="required" is set and the
            # model decides to ask a clarifying question
            # instead of calling a tool, Groq returns a 400
            # with code "tool_use_failed".
            #
            # Recovery: retry the same round with
            # tool_choice="auto" so the model can either
            # call a tool or answer directly.
            # ------------------------------------------------

            if (
                tool_choice == "required"
                and "tool_use_failed" in exc_str
            ):

                print(
                    f"[supervisor] "
                    f"tool_choice=required rejected by model — "
                    f"retrying round {round_num} with auto"
                )

                try:

                    response = (
                        client.chat.completions.create(

                            model=MODEL,

                            messages=messages,

                            tools=TOOL_SCHEMAS,

                            tool_choice="auto",

                            temperature=0,

                            max_tokens=1800,
                        )
                    )

                except Exception as retry_exc:

                    print(
                        f"[supervisor] "
                        f"retry error: {retry_exc}"
                    )

                    return (
                        "Sorry, I couldn't process "
                        "your request right now."
                    )

            else:

                print(
                    f"[supervisor] "
                    f"Groq error: {exc}"
                )

                return (
                    "Sorry, I couldn't process "
                    "your request right now."
                )

        # ====================================================
        # RESPONSE
        # ====================================================

        message = response.choices[0].message

        tool_calls = (
            getattr(
                message,
                "tool_calls",
                None
            )
            or []
        )

        finish_reason = (
            response.choices[0]
            .finish_reason
        )

        # ====================================================
        # TOKEN LOG
        # ====================================================

        usage = getattr(
            response,
            "usage",
            None
        )

        if usage:

            print(
                f"[llm] "
                f"finish_reason={finish_reason}, "
                f"tool_calls={len(tool_calls)}, "
                f"tokens="
                f"{getattr(usage, 'prompt_tokens', 0)}/"
                f"{getattr(usage, 'completion_tokens', 0)}/"
                f"{getattr(usage, 'total_tokens', 0)}"
            )

        else:

            print(
                f"[llm] "
                f"finish_reason={finish_reason}, "
                f"tool_calls={len(tool_calls)}"
            )

        # ====================================================
        # FINAL ANSWER
        # ====================================================

        if not tool_calls:

            final_answer = (
                message.content or
                ""
            ).strip()

            # ------------------------------------------------
            # DISPLAY REQUEST
            # ------------------------------------------------
            #
            # IMPORTANT:
            #
            # We do NOT use the LLM's generated review text.
            #
            # We use the ORIGINAL database records.
            #
            # Python attaches the full review_text.
            #
            # ------------------------------------------------

            if display_request:

                if retrieved_records:

                    final_answer = (
                        _format_display_records(
                            retrieved_records
                        )
                    )

                else:

                    final_answer = (
                        "No reviews were found."
                    )

            print(
                "[supervisor] "
                "final answer generated"
            )

            return final_answer

        # ====================================================
        # ADD ASSISTANT TOOL MESSAGE
        # ====================================================

        assistant_tool_message = {

            "role": "assistant",

            "content": message.content or "",

            "tool_calls": []
        }

        for tool_call in tool_calls:

            assistant_tool_message[
                "tool_calls"
            ].append({

                "id": tool_call.id,

                "type": "function",

                "function": {

                    "name": (
                        tool_call.function.name
                    ),

                    "arguments": (
                        tool_call.function.arguments
                    )
                }
            })

        messages.append(
            assistant_tool_message
        )

        # ====================================================
        # EXECUTE ALL TOOL CALLS
        # ====================================================

        for tool_call in tool_calls:

            tool_name = (
                tool_call.function.name
            )

            arguments = _parse_arguments(
                tool_call.function.arguments
            )

            arguments = _normalize_arguments(
                tool_name,
                arguments
            )

            print(
                f"[llm] tool call: "
                f"{tool_name} "
                f"args={arguments}"
            )

            # ------------------------------------------------
            # DUPLICATE KEY
            # ------------------------------------------------

            arguments_key = json.dumps(
                arguments,
                sort_keys=True
            )

            call_key = (
                tool_name,
                arguments_key
            )

            # ------------------------------------------------
            # DUPLICATE TOOL CALL
            # ------------------------------------------------

            if call_key in executed_calls:

                print(
                    f"[supervisor] "
                    f"duplicate call skipped: "
                    f"{tool_name}"
                )

                tool_context = json.dumps({
                    "error": (
                        "This exact tool call was "
                        "already executed. "
                        "Use the previously retrieved data."
                    )
                })

            # ------------------------------------------------
            # NEW TOOL CALL
            # ------------------------------------------------

            else:

                executed_calls.add(
                    call_key
                )

                raw_result, records = (
                    _execute_tool(
                        tool_name,
                        arguments
                    )
                )

                # ============================================
                # SAVE ORIGINAL RECORDS
                # ============================================

                if records:

                    retrieved_records.extend(
                        records
                    )

                # ============================================
                # PREPARE LLM CONTEXT
                # ============================================

                tool_context = (
                    _format_tool_result_for_llm(
                        raw_result,
                        display_request
                    )
                )

            # =================================================
            # SEND TOOL RESULT TO LLM
            # =================================================

            messages.append({

                "role": "tool",

                "tool_call_id": tool_call.id,

                "content": tool_context
            })

    # ========================================================
    # FALLBACK
    # ========================================================

    print(
        "[supervisor] "
        "maximum rounds reached"
    )

    # Even if the LLM fails to produce the final response,
    # we can still safely display exact records.

    if (
        display_request
        and retrieved_records
    ):

        return _format_display_records(
            retrieved_records
        )

    return (
        "I retrieved the relevant information, "
        "but I couldn't generate the final response."
    )