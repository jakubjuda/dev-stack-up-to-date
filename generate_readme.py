import os
import datetime
from google import genai
from google.genai import types

# 1. Setup API Client
# Try to get the key from either common environment variable name

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

client = genai.Client(api_key=api_key)

# 2. Filter for 'pro' models and sort to find the latest
models = client.models.list()
pro_models = [
    getattr(m, 'name', '') for m in models
    if getattr(m, 'name', '').startswith('models/gemini')
    and 'pro' in getattr(m, 'name', '').lower()
    and not any(x in getattr(m, 'name', '').lower() for x in ['image', 'lyria', 'banana'])
]
latest_pro = sorted(pro_models)[-1] if pro_models else "gemini-2.5-pro"

# 3. Define the context
current_date = datetime.datetime.now().strftime("%Y-%m-%d")

prompt = f"""
Act as a Senior Principal Engineer and Technical Writer. 
Today is {current_date}. 

Your task is to perform a deep-scan synthesis of the {current_date[:4]} tech landscape and generate an elite-level README.md.

### GOAL
Create the definitive "State of the Stack" guide for developers on Linux (WSL2/Docker/Native) and macOS.

### CRITICAL FOCUS AREAS:
1. **Python Ecosystem (The "Speed & Tooling" Era):** Detail updates on high-performance tooling (UV, Ruff, Mojo interop) and modern frameworks like FastAPI or Pydantic.
2. **AI/LLM Integration (The "Agentic Framework" Era):** Focus on production-grade AI tools like PydanticAI, LangChain/LangGraph, and local LLM orchestration (Ollama/vLLM) for developers.
3. **Data Engineering (The "Local-First & OLAP" Trend):** Focus on the shift toward Polars, DuckDB, and modern orchestration (Dagster/Prefect/Temporal).
4. **DevOps & Infrastructure (The "Platform Engineering" Shift):** Cover OpenTofu, Dagger.io, and the latest Docker/Podman features for local development.
5. **Data Platform Engineering (The "Open Lakehouse & Interoperability" Era):** Focus on the infrastructure underpinning modern analytics, specifically multi-engine table formats (Apache Iceberg, Delta Lake), unified REST catalog standards (Apache Polaris, Unity Catalog), and high-performance in-memory data movement (Apache Arrow/Flight).

### REQUIRED SECTION STRUCTURE:
Each of the 5 focus areas MUST contain the following elements in order:
- High-level overview of current paradigm shifts.
- **Legacy vs. Modern Table** with columns: `Legacy Tool` | `Modern Alternative` | `Key Advantage`.
- **Top Trend to Watch** formatted as a blockquote (`> ...`).
- **1-Line Setup Snippet** providing a concise, copy-pasteable CLI command suitable for macOS/WSL2.

### FORMATTING REQUIREMENTS:
- **Header:** Start with `# 🚀 Developer Stack: {current_date[:4]} Edition` followed by `> Last Updated: {current_date}`.
- **Comparison Tables:** Include a "Legacy vs. Modern" table for each section (e.g., Pip vs. UV, Airflow vs. Dagster).
- **Setup Snippets:** Provide 1-line CLI examples for the most important new tool in each category.
- **Visual hierarchy:** Use bold terms for emphasis, callout quotes for "Top Trend to Watch," and clear nested lists.

### TONE:
Professional, authoritative, and concise. Avoid fluff; provide actionable technical insights
"""

# 4. Generate content with Google Search Grounding
print(f"Fetching updates for {current_date} using {latest_pro}")

response = client.models.generate_content(
    model=latest_pro,
    contents=prompt,
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearchRetrieval())],
    )
)

# 5. Save to README.md
with open("README.md", "w", encoding="utf-8") as f:
    f.write(response.text)

print("Successfully updated README.md.")
