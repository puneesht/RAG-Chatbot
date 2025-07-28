from dotenv import load_dotenv
import os
import pandas as pd
from llama_index.experimental.query_engine import PandasQueryEngine


from prompts import new_prompt, instruction_str, coffee_context, context
from note_engine import note_engine
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from pdf import canada_engine

load_dotenv()

population_path = os.path.join("data", "Heatmap.csv")
population_df = pd.read_csv(population_path)

population_query_engine = PandasQueryEngine(df=population_df, verbose=True, instruction_str=instruction_str)
population_query_engine.update_prompts({"pandas_prompt": new_prompt})

# --- REMOVE OR COMMENT OUT ALL coffee_scraper USAGE ---
# coffee_scraper.scrape_nearby_coffee()
# coffee_query_engine = coffee_scraper.get_query_engine()

tools = [
    note_engine,
    QueryEngineTool(
        query_engine=population_query_engine,
        metadata=ToolMetadata(
            name="population_data",
            description="his gives itnformation about the countries and its population",
        ),
    ),
    QueryEngineTool(
        query_engine=canada_engine,
        metadata=ToolMetadata(
            name="canada_pdf",
            description="Use this tool to answer any question about the uploaded insurance policy PDF document, including sum insured, coverage, exclusions, renewal, and policyholder details",
        ),
    ),
    # --- REMOVE THIS TOOL IF IT RELIES ON coffee_query_engine ---
    # QueryEngineTool(
    #     query_engine=coffee_query_engine,
    #     metadata=ToolMetadata(
    #         name="ottawa_coffee",
    #         description=(
    #             "Coffee shops near National Gallery of Canada. "
    #             "Includes price levels (1-3), ratings (1-5) and distances."
    #         )
    #     )
    # )
]
# llm = OpenAI(model="gpt-3.5-turbo")
llm = OpenAI(model="gpt-4o-mini-2024-07-18")
agent = ReActAgent.from_tools(tools, llm=llm, verbose=True, context=context + "\n" + coffee_context)

while (prompt := input("Enter a prompt (q to quit): ")) != "q":
    result = agent.query(prompt)
    print(result)
