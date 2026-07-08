from genlayer import *
import json

class WebAndLlmContract(gl.Contract):
    # Persistent storage fields
    last_checked_price: gl.u256
    sentiment_summary: str

    def __init__(self):
        self.last_checked_price = 0
        self.sentiment_summary = ""

    @gl.public.write
    def update_price(self, ticker: str):
        """
        Fetches the price of a stock/crypto ticker from an API and updates storage.
        Uses strict_eq because all validators should agree on the exact price parsed.
        """
        # 1. Define the non-deterministic block
        def fetch_price() -> gl.u256:
            # Query web page
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={ticker}&vs_currencies=usd"
            response_json = gl.nondet.web.get(url)
            data = json.loads(response_json)
            # coingecko returns e.g. {"bitcoin":{"usd":60000}}
            price = data[ticker]["usd"]
            return int(price)

        # 2. Execute via strict equivalence consensus
        # If validators get different prices (due to API updates during blocks),
        # they must agree on a single consensus outcome.
        self.last_checked_price = gl.eq_principle.strict_eq(fetch_price)

    @gl.public.write
    def analyze_web_sentiment(self, search_query: str):
        """
        Searches web data, prompts an LLM for sentiment summary, and stores result.
        Uses prompt_non_comparative for LLM output equivalence verification.
        """
        # 1. Define prompt closure
        def prompt_builder() -> str:
            # Fetch some content
            content = gl.nondet.web.get(f"https://example.com/news?q={search_query}")
            return f"Analyze the sentiment of the following news articles about {search_query} and summarize in 1 sentence:\n{content[:2000]}"

        # 2. Run prompt and verify via semantic criteria
        self.sentiment_summary = gl.eq_principle.prompt_non_comparative(
            prompt_builder,
            task="Analyze news sentiment and return a 1-sentence summary",
            criteria="The summary must be exactly 1 sentence, objectively reflecting the input text sentiment."
        )
