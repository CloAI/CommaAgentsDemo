from typing import List, TypedDict, Union
from comma_agents.flows import BaseFlow, SequentialFlow, CycleFlow
from comma_agents.strategies.strategy import Strategy
from comma_agents.agents import BaseAgent, UserAgent
from comma_agents.utils.print_formats import print_cycle_flow_format
from functools import partial

import seedir
import os

class CycleCumulativeFlow(CycleFlow):
    def __init__(self, 
                 flow_name: str = "Cycle Cumulative Flow", 
                 cycles: int = 1, 
                 flows: Union[List[Union[BaseAgent, BaseFlow]], BaseFlow] = []
        ):
        super().__init__(flow_name=flow_name, cycles=cycles, flows=flows)
        self.responses = []
    
    def _run_flow(self, message=""):
        """
        Runs the flow with the specified message.

        Parameters:
        message (str): The message to be used for the flow.

        Returns:
        List[str]: A list of responses from each agent in the flow.
        """
        responses = []
        for cycle in range(self.cycles):
            # Print cycle information if verbose mode is enabled
            if self.verbose_level >= 1:
                print_cycle_flow_format(self.flow_name, self.cycles, cycle + 1, prompt=message)
            
            for flow in self.flows:
                responses.append(flow.call(message) if isinstance(flow, BaseAgent) else flow.run_flow(message))
        
        return "\n".join(responses) #TODO: make this configurable for concatenation or list of responses

    def _defined_flow(self, flow_params: dict) -> BaseFlow:
        self._cycle_count += 1
        return self.flow

FILE_SUMMARY_PROMPT_TEMPLATE = """
Given the file_name: {file_name} file is located at {file_path} and has the following head and tail content:
{head_content}
...
{tail_content}

- Provide a single sentence summary of the file.
- Summarize the content of the file in a concise manner.
- Make sure to describe the headers of CSV exactly as they INCLUDING capitalization.
- Avoid repeating the content of the file in the summary.
- Respond ONLY in the following format, <file_name>: <summary>
"""

file_directory_summary_prompts = []

class DirectoryAndFileSummaryStrategy(Strategy):
    class DirectoryAndFileSummaryStrategyParams(TypedDict, total=True):
        file_summary_agent: BaseAgent
        directory_path: str

    def __init__(self, strategy_params: DirectoryAndFileSummaryStrategyParams):
        super().__init__(
            strategy_name="Directory and File Summary", 
            strategy_params=strategy_params)
        self.flows = [self._defined_strategy(strategy_params)]
    
    def _defined_strategy(self, strategy_params: DirectoryAndFileSummaryStrategyParams) -> Union[List[BaseFlow], BaseFlow]:
        # get the tree output of the directory
        directory_path = strategy_params["directory_path"]
        # get the list of all files under the directory
        file_list = []
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_list.append(os.path.join(root, file))

        for file in file_list:
            # read the first 5 lines and last 5 line of the file
            with open(file, "r") as f:
                head_content = "".join(f.readlines()[:5])
                f.seek(0)
                tail_content = "".join(f.readlines()[-5:])
            
            # get the file name
            file_name = os.path.basename(file)
            
            # prompt the agent for a single sentence summary of the file
            templates = FILE_SUMMARY_PROMPT_TEMPLATE.format(
                file_name=file_name,
                file_path=file,
                head_content=head_content,
                tail_content=tail_content
            )

            file_directory_summary_prompts.append(templates)

        # Alter the system prompt to focus on summarizing the file
        strategy_params["file_summary_agent"].add_hook("before_call", before_file_summary_prompt_call_message)
        strategy_params["file_summary_agent"].add_hook("before_initial_call", before_file_summary_prompt_call_message)
        tree = seedir.seedir(directory_path, style="lines", printout=False)
        
        return SequentialFlow(
            name="Directory and File Summary Flow",
            flows=[
                CycleCumulativeFlow(
                    flow_name="File Summary Cycle",
                    cycles=len(file_list),
                    flows=strategy_params["file_summary_agent"]
                )
            ],
            hooks={
                "alter_message_after_flow": partial(alter_file_summary_message_after_cycle, tree=tree)
            }
        )



def alter_file_summary_message_after_cycle(message: str="", tree: str = None):
    full_context = """
Here is summary of the current directory:
{tree}

File Summaries:
{file_summaries}
    """.format(
        tree=tree,
        file_summaries=message
    )

    return full_context

CURRENT_PROMPT_TEMPLATE_INDEX = 0

def before_file_summary_prompt_call_message(agent: BaseAgent):
    global CURRENT_PROMPT_TEMPLATE_INDEX
    agent.prompt_template.parameters["system_message"] = file_directory_summary_prompts[CURRENT_PROMPT_TEMPLATE_INDEX]
    CURRENT_PROMPT_TEMPLATE_INDEX += 1