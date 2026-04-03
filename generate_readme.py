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
Today is {current_date}. 
Search for the latest updates in the Python, DevOps, and Data Engineering ecosystems 
specifically for Linux (WSL2, Docker, or Native) and macOS.

Generate a high-quality, professional README.md content. 
Focus on:
- Releases in Python (e.g., UV, Ruff, or FastAPI).
- Trends in Data Engineering (e.g., Polars, DuckDB, or Orchestrators like Dagster/Prefect).
- DevOps tools for 2026 (e.g., OpenTofu, Dagger, or new Docker features).

Format with professional Markdown: use tables, bold terms, and clear sections.
Ensure 'Last Updated: {current_date}' is at the top.
"""

# 4. Generate content with Google Search Grounding
print(f"Fetching updates for {current_date} using {latest_pro}")

response = client.models.generate_content(
    model=latest_pro,
    contents=prompt,
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearchRetrieval())],
        # Optional: You can tell the model to "think harder" 
        # for complex technical stack analysis
        thinking_config={'include_thoughts': True} if "pro" in "gemini-3.1-pro" else None
    )
)

# 5. Save to README.md
with open("README.md", "w", encoding="utf-8") as f:
    f.write(response.text)

print("Successfully updated README.md.")
