import random
from comma_agents.hub.agents.cloai.mlx import MLXAgent
from comma_agents.prompts import Llama31PromptTemplate
from comma_agents.flows import SequentialFlow
from strategies import DirectoryAndFileSummaryStrategy
SEED = 4497
# Set the seed of the program to keep the results reproducible and consistent
random.seed(SEED)

file_summary_agent = MLXAgent(
    name="File Summary Agent",
    prompt_template=Llama31PromptTemplate(),
    config={
        "model_path": "mlx-community/Meta-Llama-3.1-8B-Instruct-8bit",
        "seed": SEED,
        "max_tokens": 2048,
        "temp": 0.0
    }
)

summarize_folder = DirectoryAndFileSummaryStrategy(
    strategy_params={
        "directory_path": "./data/base_case_financials/Q1",
        "file_summary_agent": file_summary_agent
    }
)

develop_balance_sheet_agent = MLXAgent(
    name="Develop Balance Sheet Agent",
    prompt_template=Llama31PromptTemplate(
        parameters={
            "system_message": """
Environment: ipython

You are a agent capable of generating a balance sheet for a company.
You will be given a list of financial files and their summaries.
You will will determine what files are needed for the balance sheet.
You can use Python to help you generate the balance sheet and read the files.
"""
        }
    ),
    config={
        "model_path": "mlx-community/Meta-Llama-3.1-8B-Instruct-8bit",
        "seed": SEED,
        "max_tokens": 2048,
        "temp": 0.0
    }
)

balance_sheet_generator_flow = SequentialFlow(
    name="Balance Sheet Generator Flow",
    flows=[
        summarize_folder,
        develop_balance_sheet_agent
    ]
)

print(balance_sheet_generator_flow.run_flow("Summarize the file provided the context"))