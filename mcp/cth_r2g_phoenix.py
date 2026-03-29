#!/usr/bin/env python3
"""
FastMCP Server for file_access - Various Usage Examples
"""
import sys
import os
import shutil
import re
import subprocess
from typing import List, Dict

autobots_sdk_tool_path = os.environ.get("AUTOBOTS_SDK_TOOL_PATH")
if autobots_sdk_tool_path:
    sys.path.insert(0, autobots_sdk_tool_path)

from autobots_base.mcp.servers.base_server import (
    AutobotsMCPStdioServer,
    Context,  # Use the base Context instead
)

mcp_phoenix_run_agent = AutobotsMCPStdioServer(name="cth_r2g_phoenix_tool")

@mcp_phoenix_run_agent.tool()
def generate_eouMGR_command(block_name: str, start_task: str, end_task: str) -> str:
    """`
    Generates the command line to run eouMGR.
    **MUST ASK THE USER FOR THE REQUIRED INPUTS BEFORE CALLING THIS TOOL**
    Parameters:
        block_name (str): The block name for the eouMGR command.
        start_task (str): The starting task for the flow.
        end_task (str): The ending task for the flow.
    
    Returns:
        str: Command line string to execute eouMGR.
    """
    flow:str = "phoenix"

    command = (
        f"eouMGR --block {block_name} --flow {flow} --startTask {start_task} "
        f"--endTask {end_task} --feeder {flow}_{block_name} --gui --reset &"
    )
    
    return command


@mcp_phoenix_run_agent.tool()
def phoenix_setup_helper(ref_ward: str, block_name: str, technology: str, 
                     apr_fc_dir_name: str,
                     destination_dir: str, design_name: str) -> str:
    """
    Generate and execute the command line to run the Phoenix setup script.
    **MUST ASK THE USER FOR THE REQUIRED INPUTS BEFORE CALLING THIS TOOL**
    Parameters:
        ref_ward (str): Reference ward directory path
        block_name (str): Block name (e.g., par_cbpma, dhm)
        technology (str): Technology version (e.g., 1278.6)
        apr_fc_dir_name (str): APR_FC directory name
        destination_dir (str): Destination directory path
        design_name (str): Design name
    Returns:
        str: Execution result including stdout and stderr
    """
    
    script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "utils", "fc_setup_auto_main.py")
    
    command = f"python3 {script_path}"
    command += f" --destination_dir {destination_dir}"
    command += f" --ref_wa {ref_ward}"
    command += f" --block_name {block_name}"
    command += f" --technology {technology}"
    command += f" --apr_fc_dir_name {apr_fc_dir_name}"
    command += f" --design_name {design_name}"
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return f"Command executed successfully:\n{command}\n\nOutput:\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Command failed:\n{command}\n\nError:\n{e.stderr}\nOutput:\n{e.stdout}"

@mcp_phoenix_run_agent.tool()
def generate_and_compare_summaries(
    apr_fc_reference_dir: str, 
    apr_fc_block_name: str, 
    apr_fc_technology: str, 
    apr_fc_dir_name: str,
    phoenix_reference_dir: str,
    phoenix_block_name: str,
    phoenix_technology: str,
    phoenix_apr_fc_dir_name: str,
    output_dir: str, 
    stage: str
) -> str:
    """
    scripts and comparison script.
    **MUST ASK THE USER FOR THE REQUIRED INPUTS BEFORE CALLING THIS TOOL**
    This tool runs three command lines:
    1. apr_fc_run_summarize.py: To create a summary for the APR_FC run.
    2. phoenix_run_summarize_results.py: To create a summary for the Phoenix run.
    3. run_comparison.py: To compare the two generated summaries for a specific stage.

    Parameters:
        apr_fc_reference_dir (str): The base directory for the APR_FC run.
        apr_fc_block_name (str): The block name for the APR_FC run.
        apr_fc_technology (str): The technology node for the APR_FC run.
        apr_fc_dir_name (str): The APR_FC run directory name for the APR_FC run.
        phoenix_reference_dir (str): The base directory for the Phoenix run.
        phoenix_block_name (str): The block name for the Phoenix run.
        phoenix_technology (str): The technology node for the Phoenix run.
        phoenix_apr_fc_dir_name (str): The APR_FC directory name for the Phoenix run.
        output_dir (str): The directory to save the summary and comparison logs.
        stage (str): The specific stage to compare ('compile', 'clock', or 'route').

    Returns:
        str: Execution logs for the scripts.
    """
    script_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "utils")
    
    # APR_FC summary command
    apr_fc_summary_log = os.path.join(output_dir, f"{apr_fc_block_name}_apr_fc_summary.log")
    apr_fc_cmd = f"python3 {script_dir}/apr_fc_run_summarize.py"
    apr_fc_cmd += f" --reference_dir {apr_fc_reference_dir}"
    apr_fc_cmd += f" --output_dir {output_dir}"
    apr_fc_cmd += f" --block_name {apr_fc_block_name}"
    apr_fc_cmd += f" --tech {apr_fc_technology}"
    apr_fc_cmd += f" --apr_fc {apr_fc_dir_name}"
    
    # Phoenix summary command
    phoenix_summary_log = os.path.join(output_dir, f"{phoenix_block_name}_phoenix_summary.log")
    phoenix_cmd = f"python3 {script_dir}/phoenix_run_summarize_results.py"
    phoenix_cmd += f" --reference_dir {phoenix_reference_dir}"
    phoenix_cmd += f" --output_dir {output_dir}"
    phoenix_cmd += f" --block_name {phoenix_block_name}"
    phoenix_cmd += f" --tech {phoenix_technology}"
    phoenix_cmd += f" --apr_fc {phoenix_apr_fc_dir_name}"
    
    # Comparison command
    comparison_log = os.path.join(output_dir, f"qor_comparison_{stage}.log")
    comparison_cmd = f"python3 {script_dir}/run_comparison.py"
    comparison_cmd += f" --apr_fc_summary {apr_fc_summary_log}"
    comparison_cmd += f" --phoenix_summary {phoenix_summary_log}"
    comparison_cmd += f" --output_dir {output_dir}"
    comparison_cmd += f" --stage {stage}"
    
    commands = [
        ("APR_FC Summary", apr_fc_cmd),
        ("Phoenix Summary", phoenix_cmd),
        ("Comparison", comparison_cmd)
    ]
    
    execution_log = []
    
    for name, cmd in commands:
        try:
            execution_log.append(f"Executing {name}...")
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
            execution_log.append(f"Success:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            execution_log.append(f"Failed {name}:\n{e.stderr}\n{e.stdout}")
            return "\n".join(execution_log)
            
    return "\n".join(execution_log)


@mcp_phoenix_run_agent.tool()
def check_vars_tcl_phoenix_intent(destination_dir: str, block_name: str,
                                   technology: str, intent: str = "") -> str:
    """
    Check vars.tcl for 'set ivar(phoenix_int)' after Phoenix setup.
    If the variable exists, returns its current value.
    If it does not exist and intent is provided ('power' or 'timing'), appends it.
    If it does not exist and no intent is provided, asks the user to specify.

    **MUST BE CALLED AFTER PHOENIX SETUP IS COMPLETE**

    Parameters:
        destination_dir (str): The destination directory used during setup.
        block_name (str): Block name (e.g., par_cbpma, dhm).
        technology (str): Technology node (e.g., 1278.6).
        intent (str): Optional. The intent to set — 'power' or 'timing'.
                       Leave empty to just check.

    Returns:
        str: Status message describing what was found or done.
    """
    utils_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "utils")
    sys.path.insert(0, utils_dir)
    from utils import check_phoenix_intent

    vars_tcl_path = os.path.join(
        destination_dir, "runs", block_name, technology, "apr_fc", "scripts", "vars.tcl"
    )

    intent_arg = intent.strip() if intent else None
    result = check_phoenix_intent(vars_tcl_path, intent=intent_arg)

    if result['found']:
        return f"✓ phoenix_int is already set in vars.tcl: {result['value']}"
    elif result['needs_input']:
        return (
            "⚠ 'set ivar(phoenix_int)' was NOT found in vars.tcl.\n"
            "Please ask the user: What intent would you like to set — 'power' or 'timing'?\n"
            "Then call this tool again with the intent parameter."
        )
    else:
        return f"✓ {result['action']}"


if __name__ == "__main__":
    mcp_phoenix_run_agent.run()  # Run the MCP server
