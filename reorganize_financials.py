import random
from comma_agents.hub.agents.cloai.mlx import MLXAgent
from comma_agents.prompts import Llama31PromptTemplate
from comma_agents.flows import SequentialFlow
from comma_agents.code_interpreters import CodeInterpreter
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

develop_metadata_agent = MLXAgent(
    name="Develop Balance Sheet Agent",
    prompt_template=Llama31PromptTemplate(
        parameters={
            "system_message": """
Environment: ipython

# Operation Instructions
0. Determine the files needed for completing the Balance Sheet Requirements.
1. Use Python to determine the files format and data availability.
2. Print headers, confirmation of data types and column headings, and account for errors.
3. Output ONLY the headers for the files and format it with <file_name>: <data headers>, <meta_data>

# Balance Sheet Requirements
- Net revenue
- Cost of sales
- Amortization of acquisition-related intangibles
- Total cost of sales
- Gross profit
- Research and development
- Marketing, general and administrative
- Amortization of acquisition-related intangibles
- Licensing gain
- Operating income (loss) 
- Interest expense
- Other income (expense)
- Income (loss) before income taxes and equity income
- Income tax provision (benefit)
- Equity income in investee
- Net income (loss)

# Errors
- If there is an error with scripts notify and come up with a solution.

write a python program that helps accomplish the above requirements.
"""
        }
    ),
    config={
        "model_path": "mlx-community/Meta-Llama-3.1-8B-Instruct-8bit",
        "seed": SEED,
        "max_tokens": 2048 * 2,
        "temp": 0.0,
        "stream": True
    },
    interpret_code=True,
    code_interpreter=CodeInterpreter(
        execution_directory="./data/base_case_financials/Q1",
        output_format="""<|start_header_id|>ipython<|end_header_id|>
        
{code_output}<|eot_id|>
"""
    )
)

develop_balance_sheet_agent = MLXAgent(
    name="Develop Balance Sheet Agent",
    prompt_template=Llama31PromptTemplate(
        parameters={
            "system_message": """
Environment: ipython

# Operation Instructions
0. Determine the files needed for completing the Balance Sheet Requirements. DO NOT REDO CODE THAT HAS ALREADY BEEN WRITTEN.
1. Once you have the necessary files load them and extract needed information.
2. Generate a balance sheet for the company.
3. If data needed is not available set the value to -1.

# Balance Sheet Requirements
- Net revenue
- Cost of sales
- Amortization of acquisition-related intangibles
- Total cost of sales
- Gross profit
- Research and development
- Marketing, general and administrative
- Amortization of acquisition-related intangibles
- Licensing gain
- Operating income (loss) 
- Interest expense
- Other income (expense)
- Income (loss) before income taxes and equity income
- Income tax provision (benefit)
- Equity income in investee
- Net income (loss)

# Errors
- If there is an error with scripts notify and come up with a solution.

The user will give you output from a agents response, this is to be used as context. 
Given the output of details from a script and the requirements above, write a python program that will generate a balance sheet for the company do not reimplement functionality requirements from previous output.
Use the ```python or <|python_tag|> tags to start the code section.
"""
        }
    ),
    config={
        "model_path": "mlx-community/Meta-Llama-3.1-8B-Instruct-8bit",
        "seed": SEED,
        "max_tokens": 2048 * 2,
        "temp": 0.0,
        "stream": True
    },
    interpret_code=True,
    code_interpreter=CodeInterpreter(
        execution_directory="./data/base_case_financials/Q1",
        output_format="""<|start_header_id|>ipython<|end_header_id|>
        
{code_output}<|eot_id|>
"""
    )
)

balance_sheet_generator_flow = SequentialFlow(
    name="Balance Sheet Generator Flow",
    flows=[
        summarize_folder,
        develop_metadata_agent,
        develop_balance_sheet_agent
    ]
)

print(balance_sheet_generator_flow.run_flow("Summarize the file provided the context"))