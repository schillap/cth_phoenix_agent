#!/usr/bin/env python3
"""
eouMGR Runner Script
====================
A concise script to execute eouMGR commands for the Phoenix or APR_FC flow.
"""

import sys
import subprocess
import argparse

def execute_eou_manager(block_name, design_name, start_task, end_task, flow):
    """
    Executes the eouMGR command with default flags.
    
    Args:
        block_name (str): The block name/build name for the eouMGR command.
        design_name (str): The design name for the eouMGR command.
        start_task (str): The starting task for the flow.
        end_task (str): The ending task for the flow.
        flow (str): The flow to run ('phoenix' or 'apr_fc').
    
    Returns:
        bool: True if the command was launched successfully, False otherwise.
    """
    try:
        # Build the eouMGR command with hardcoded default flags
        eou_command = [
            "eouMGR",
            "--block", block_name,
            "--design", design_name,
            "--flow", flow,
            "--startTask", start_task,
            "--endTask", end_task,
            "--feeder", block_name,
            "--batch",
            "--reset",
            "--waive_on_error"
            " &"
        ]

        print(f"\nExecuting: {' '.join(eou_command)}")

        # Execute eouMGR in the background
        subprocess.Popen(eou_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
        print(f"✓ eouMGR started successfully")
        return True

    except FileNotFoundError:
        print("✗ Error: 'eouMGR' command not found. Please ensure it is in your PATH.", file=sys.stderr)
        return False
    except Exception as e:
        print(f"✗ An error occurred while launching eouMGR: {e}", file=sys.stderr)
        return False

def get_interactive_inputs():
    """Gets essential inputs from the user interactively, without defaults."""
    print("=== eouMGR Runner - Interactive Mode ===")
    
    while True:
        block_name = input("Enter block name/build name: ").strip()
        if block_name:
            break
        print("Block name/build name cannot be empty.", file=sys.stderr)
    
    while True:
        design_name = input("Enter design name: ").strip()
        if design_name:
            break
        print("Design name cannot be empty.", file=sys.stderr)
    
    while True:
        flow = input("Enter flow type (phoenix/apr_fc): ").strip().lower()
        if flow in ['phoenix', 'apr_fc']:
            break
        print("Invalid input. Please enter 'phoenix' or 'apr_fc'.", file=sys.stderr)

    while True:
        start_task = input("Enter start task: ").strip()
        if start_task:
            break
        print("Start task cannot be empty.", file=sys.stderr)

    while True:
        end_task = input("Enter end task: ").strip()
        if end_task:
            break
        print("End task cannot be empty.", file=sys.stderr)

    return block_name, design_name, start_task, end_task, flow

def main():
    """Parses arguments and runs the eouMGR command."""
    parser = argparse.ArgumentParser(
        description='A script to execute eouMGR for the Phoenix or APR_FC flow.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''Examples:
  # Phoenix flow
  python3 eouMGR_runner.py --flow phoenix --block_name par_saf_ioc --design_name par_saf_ioc --start_task phoenix_compile --end_task phoenix_route

  # APR_FC flow
  python3 eouMGR_runner.py --flow apr_fc --block_name par_saf_ioc --design_name par_saf_ioc --start_task logic_opto --end_task route_opt'''
    )
    
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode.')
    parser.add_argument('--flow', type=str, choices=['phoenix', 'apr_fc'], help='The flow to run.')
    parser.add_argument('--block_name', type=str, help='Block name/build name for the eouMGR command.')
    parser.add_argument('--design_name', type=str, help='Design name for the eouMGR command.')
    parser.add_argument('--start_task', type=str, help='Starting task (e.g., phoenix_compile or logic_opto).')
    parser.add_argument('--end_task', type=str, help='Ending task (e.g., phoenix_route or route_opt).')
    
    args = parser.parse_args()

    if args.interactive:
        block_name, design_name, start_task, end_task, flow = get_interactive_inputs()
    else:
        if not all([args.flow, args.block_name, args.design_name, args.start_task, args.end_task]):
            parser.error("all arguments (--flow, --block_name, --design_name, --start_task, --end_task) are required in non-interactive mode.")
        block_name, design_name, start_task, end_task, flow = args.block_name, args.design_name, args.start_task, args.end_task, args.flow

    if not execute_eou_manager(block_name, design_name, start_task, end_task, flow):
        sys.exit(1)

if __name__ == "__main__":
    main()