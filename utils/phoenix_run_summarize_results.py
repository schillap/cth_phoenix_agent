#!/usr/bin/env python3
"""
Work FCDSO Results Summary Script
=================================
This script navigates to runs/$block_name/$tech/$apr_fc/work_fcdso and searches
through compile_1, clock_1, and route_1 directories for .run* subdirectories,
then greps "QoR Summary" from their logs/ directories.
"""

import os
import sys
import glob
import argparse
from datetime import datetime

class WorkFcdsoSummarizer:
    """
    A class to handle work_fcdso results summary extraction and logging.
    """
    
    def __init__(self, reference_dir, output_dir, block_name, tech, apr_fc):
        """
        Initialize the WorkFcdsoSummarizer.
        
        Args:
            reference_dir: The reference directory to analyze
            output_dir: Directory where work_fcdso_summary.log will be created 
            block_name: Block name for navigating to specific work_fcdso directory
            tech: Technology node for directory path
            apr_fc: APR_FC directory name
        """
        self.reference_dir = os.path.abspath(reference_dir)
        self.output_dir = output_dir 
        self.log_file = os.path.join(self.output_dir, f"{block_name}_phoenix_summary.log")
        self.block_name = block_name
        self.tech = tech
        self.apr_fc = apr_fc
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize log file
        self._initialize_log()
    
    def _initialize_log(self):
        """Initialize the work_fcdso_summary.log file with header information."""
        with open(self.log_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("WORK_FCDSO RESULTS SUMMARY ANALYSIS\n")
            f.write("="*80 + "\n")
            f.write(f"Analysis started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Reference directory: {self.reference_dir}\n")
            f.write(f"Output directory: {self.output_dir}\n")
            if self.block_name:
                f.write(f"Block name: {self.block_name}\n")
            if self.tech:
                f.write(f"Technology: {self.tech}\n")
            if self.apr_fc:
                f.write(f"APR_FC directory: {self.apr_fc}\n")
            f.write("="*80 + "\n\n")
    
    def log_message(self, message, section="WORK_FCDSO", console_output=True):
        """
        Log a message to work_fcdso_summary.log file.
        
        Args:
            message: Message to log
            section: Section header for organization
            console_output: Whether to print to console (default: True)
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted_message = f"[{timestamp}] [{section}] {message}"
        
        with open(self.log_file, 'a') as f:
            f.write(formatted_message + '\n')
        
        # Only print to console if requested
        if console_output:
            print(formatted_message)
    
    def log_silent(self, message, section="WORK_FCDSO"):
        """Log message without console output."""
        self.log_message(message, section, console_output=False)

    def print_status(self, message, status_type="INFO"):
        """Print a clean status message to console only."""
        symbols = {
            "INFO": "ℹ",
            "SUCCESS": "✓", 
            "WARNING": "⚠",
            "ERROR": "✗",
            "PROCESSING": "→"
        }
        symbol = symbols.get(status_type, "•")
        print(f"{symbol} {message}")
    
    def find_run_directories(self, stage_dir):
        """
        Find all .run* directories in the given stage directory.
        
        Args:
            stage_dir: Path to the stage directory (compile_1, clock_1, or route_1)
            
        Returns:
            List of .run* directory paths
        """
        if not os.path.exists(stage_dir):
            return []
        
        run_dirs = []
        try:
            # Look for directories that start with .run
            for item in os.listdir(stage_dir):
                item_path = os.path.join(stage_dir, item)
                if os.path.isdir(item_path) and item.startswith('.run'):
                    run_dirs.append(item_path)
            
            # Sort for consistent ordering
            run_dirs.sort()
            
        except Exception as e:
            self.log_message(f"Error listing directories in {stage_dir}: {e}", "ERROR")
        
        return run_dirs
    def extract_qor_from_run_dir(self, run_dir, stage_name):
        """
        Extract QoR Summary from logs in a .run* directory.
        (Silent processing - only logs to file)
        """
        run_id = os.path.basename(run_dir)
        logs_dir = os.path.join(run_dir, "logs")
        
        if not os.path.exists(logs_dir):
            with open(self.log_file, 'a') as log_f:
                log_f.write(f"STAGE: {stage_name}, RUN_ID: {run_id} - NO LOGS DIRECTORY\n\n")
            return False
        
        # Define target log files based on stage
        target_log_files = {
            "compile_1": ["fc.compile_initial_opto.log", "fc.compile_final_opto.log"],
            "clock_1": ["fc.clock_route_opt.log"],
            "route_1": ["fc.route_opt.log"]
        }
        
        # Get the specific log files to search for this stage
        if stage_name in target_log_files:
            required_log_files = target_log_files[stage_name]
        elif stage_name.startswith("BEST_"):
            # For best run analysis, determine from stage name
            if "COMPILE" in stage_name:
                required_log_files = target_log_files["compile_1"]
            elif "CLOCK" in stage_name:
                required_log_files = target_log_files["clock_1"]
            elif "ROUTE" in stage_name:
                required_log_files = target_log_files["route_1"]
            else:
                required_log_files = ["fc.compile_initial_opto.log", "fc.compile_final_opto.log", 
                                     "fc.clock_route_opt.log", "fc.route_opt.log"]
        else:
            # Fallback for any other stage name
            required_log_files = ["fc.compile_initial_opto.log", "fc.compile_final_opto.log", 
                                 "fc.clock_route_opt.log", "fc.route_opt.log"]
        
        # Find the target log files that actually exist
        found_log_files = []
        try:
            available_files = os.listdir(logs_dir)
            for required_file in required_log_files:
                if required_file in available_files:
                    file_path = os.path.join(logs_dir, required_file)
                    if os.path.isfile(file_path):
                        found_log_files.append(required_file)
        
            # found_log_files.sort()
        except Exception as e:
            self.log_silent(f"Error listing log files in {logs_dir}: {e}", "ERROR")
            return False
        
        if not found_log_files:
            with open(self.log_file, 'a') as log_f:
                log_f.write(f"STAGE: {stage_name}, RUN_ID: {run_id} - NO TARGET LOG FILES\n")
                log_f.write(f"REQUIRED_FILES: {', '.join(required_log_files)}\n\n")
            return False
        
        # Check if this is a best run analysis
        is_best_run = stage_name.startswith("BEST_")
        
        # Write section header to log file (silent)
        with open(self.log_file, 'a') as log_f:
            log_f.write(f"\n{'='*80}\n")
            log_f.write(f"STAGE: {stage_name}\n")
            log_f.write(f"RUN_ID: {run_id}\n")
            log_f.write(f"LOGS_PATH: {logs_dir}\n")
            log_f.write(f"REQUIRED_LOG_FILES: {', '.join(required_log_files)}\n")
            log_f.write(f"FOUND_LOG_FILES: {', '.join(found_log_files)}\n")
            log_f.write(f"PROCESSED_ON: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_f.write(f"{'='*80}\n\n")
        
        qor_found = False
        
        # Process each target log file (silent processing)
        for log_file in found_log_files:
            log_file_path = os.path.join(logs_dir, log_file)
            
            try:
                qor_lines = []
                with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        if "QoR Summary" in line:
                            qor_lines.append((line_num, line.strip()))
                
                if qor_lines:
                    qor_found = True
                    
                    # Write to summary log (silent)
                    with open(self.log_file, 'a') as log_f:
                        log_f.write(f"LOG_FILE: {log_file}\n")
                        log_f.write(f"FULL_PATH: {log_file_path}\n")
                        log_f.write(f"QOR_MATCHES: {len(qor_lines)}\n")
                        log_f.write("-" * 60 + "\n")
                        
                        for line_num, line_content in qor_lines:
                            # Append run_id to each QoR line for best runs
                            if is_best_run:
                                log_f.write(f"Line {line_num}: {line_content} | RUN_ID: {run_id}\n")
                            else:
                                log_f.write(f"Line {line_num}: {line_content}\n")
                        
                        log_f.write("\n")
                else:
                    # Log files without QoR Summary (silent)
                    with open(self.log_file, 'a') as log_f:
                        log_f.write(f"LOG_FILE: {log_file} - NO QoR SUMMARY FOUND\n")
                        
            except Exception as e:
                with open(self.log_file, 'a') as log_f:
                    log_f.write(f"LOG_FILE: {log_file} - ERROR READING: {e}\n")
    
        # Write end section to log file (silent)
        with open(self.log_file, 'a') as log_f:
            log_f.write(f"\n{'-'*80}\n")
            log_f.write(f"END OF {stage_name}/{run_id} ANALYSIS\n")
            log_f.write(f"{'-'*80}\n\n")
    
        return qor_found
    
    def extract_work_fcdso_results(self):
        """
        Navigate to work_fcdso directory and extract QoR summaries from all stages.
        """
        if not all([self.block_name, self.tech, self.apr_fc]):
            self.print_status("Missing required parameters", "ERROR")
            return False
        
        # Construct the path to the work_fcdso directory
        work_fcdso_dir = os.path.join(self.reference_dir, "runs", self.block_name, self.tech, self.apr_fc, "work_fcdso")
        
        # Define the stage directories to search
        stage_dirs = ["compile_1", "clock_1", "route_1"]
        
        self.print_status("Analyzing work_fcdso results...", "PROCESSING")
        
        # Check if work_fcdso directory exists
        if not os.path.exists(work_fcdso_dir):
            self.print_status(f"work_fcdso directory not found: {work_fcdso_dir}", "ERROR")
            return False
        
        overall_success = False
        stage_results = []
        
        # Process each stage directory
        for stage_name in stage_dirs:
            stage_dir = os.path.join(work_fcdso_dir, stage_name, "dso_work_dir")
            
            if not os.path.exists(stage_dir):
                self.log_silent(f"Stage directory not found: {stage_dir}", "STAGE_ANALYSIS")
                stage_results.append(f"{stage_name}: no data")
                continue
            
            # Find all .run* directories in this stage
            run_dirs = self.find_run_directories(stage_dir)
            
            if not run_dirs:
                self.log_silent(f"No .run* directories found in {stage_name}", "STAGE_ANALYSIS")
                stage_results.append(f"{stage_name}: no runs")
                continue
            
            run_count = len(run_dirs)
            
            # Write stage summary to log (silent)
            with open(self.log_file, 'a') as log_f:
                log_f.write(f"\n{'='*80}\n")
                log_f.write(f"STAGE DIRECTORY: {stage_name}\n")
                log_f.write(f"STAGE PATH: {stage_dir}\n")
                log_f.write(f"RUN_DIRECTORIES_FOUND: {run_count}\n")
                run_ids = [os.path.basename(run_dir) for run_dir in run_dirs]
                log_f.write(f"RUN_IDS: {', '.join(run_ids)}\n")
                log_f.write(f"ANALYSIS_STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                log_f.write(f"{'='*80}\n")
        
            # Process each .run* directory
            stage_success = False
            successful_runs = 0
            
            for run_dir in run_dirs:
                run_success = self.extract_qor_from_run_dir(run_dir, stage_name)
                if run_success:
                    stage_success = True
                    successful_runs += 1
                    overall_success = True
            
            if stage_success:
                stage_results.append(f"{stage_name}: {successful_runs}/{run_count} runs")
            else:
                stage_results.append(f"{stage_name}: 0/{run_count} runs")
        
        # Print summary
        if stage_results:
            self.print_status(f"Stage analysis: {' | '.join(stage_results)}", "INFO")
    
        return overall_success
    
    def extract_best_run_ids(self):
        """
        Extract run IDs from soft links in work_fcdso/best_run/ directory.
        
        Returns:
            Dict containing best run IDs for each stage, or None if errors occur
        """
        if not all([self.block_name, self.tech, self.apr_fc]):
            self.print_status("Missing required parameters", "ERROR")
            return None
        
        # Construct the path to the best_run directory
        best_run_dir = os.path.join(self.reference_dir, "runs", self.block_name, self.tech, self.apr_fc, "work_fcdso", "best_run")
        
        self.print_status("Checking for best run configurations...", "PROCESSING")
        
        # Check if best_run directory exists
        if not os.path.exists(best_run_dir):
            self.print_status("No best_run directory found - skipping best run analysis", "WARNING")
            self.log_silent(f"ERROR: best_run directory does not exist: {best_run_dir}", "ERROR")
            return None
        
        # Define the expected soft link directories
        link_dirs = ["compile", "clock", "route"]
        best_run_ids = {}
        
        # Write best_run analysis header to log (silent)
        with open(self.log_file, 'a') as log_f:
            log_f.write(f"\n{'='*80}\n")
            log_f.write(f"BEST_RUN ANALYSIS\n")
            log_f.write(f"BEST_RUN_PATH: {best_run_dir}\n")
            log_f.write(f"ANALYSIS_STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_f.write(f"{'='*80}\n\n")
        
        found_links = []
        
        # Process each link directory
        for link_name in link_dirs:
            link_path = os.path.join(best_run_dir, link_name)
            
            if not os.path.exists(link_path):
                self.log_silent(f"Link not found: {link_path}", "BEST_RUN")
                best_run_ids[link_name] = None
                continue
            
            # Check if it's a symbolic link
            if os.path.islink(link_path):
                try:
                    target_path = os.readlink(link_path)
                    if not os.path.isabs(target_path):
                        target_path = os.path.abspath(os.path.join(best_run_dir, target_path))
                    
                    target_basename = os.path.basename(target_path);
                    
                    if target_basename.startswith('.run'):
                        run_id = target_basename
                        best_run_ids[link_name] = run_id
                        found_links.append(f"{link_name}→{run_id}")
                        
                        # Write to log file (silent)
                        with open(self.log_file, 'a') as log_f:
                            log_f.write(f"LINK: {link_name}\n")
                            log_f.write(f"LINK_PATH: {link_path}\n")
                            log_f.write(f"TARGET_PATH: {target_path}\n")
                            log_f.write(f"RUN_ID: {run_id}\n")
                            log_f.write(f"LINK_VALID: {os.path.exists(target_path)}\n")
                            log_f.write("-" * 60 + "\n")
                    else:
                        self.log_silent(f"{link_name} target is not a .run* directory: {target_basename}", "BEST_RUN")
                        best_run_ids[link_name] = None
                        
                except Exception as e:
                    self.log_silent(f"Failed to read symbolic link {link_path}: {e}", "ERROR")
                    best_run_ids[link_name] = None
            else:
                self.log_silent(f"{link_name} is not a symbolic link: {link_path}", "BEST_RUN")
                best_run_ids[link_name] = None
        
        # Console summary
        if found_links:
            self.print_status(f"Found best runs: {', '.join(found_links)}", "SUCCESS")
        else:
            self.print_status("No best run configurations found", "WARNING")
        
        # Write summary to log (silent)
        with open(self.log_file, 'a') as log_f:
            log_f.write(f"\nBEST_RUN_SUMMARY:\n")
            log_f.write("-" * 40 + "\n")
            for link_name, run_id in best_run_ids.items():
                log_f.write(f"{link_name.upper()}_BEST_RUN: {run_id or 'NOT_FOUND'}\n")
            log_f.write(f"\nBEST_RUN_IDs_EXTRACTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_f.write(f"{'-'*80}\n\n")
        
        return best_run_ids
    
    def extract_best_run_qor_summaries(self, best_run_ids):
        """
        Extract QoR summaries for the best run IDs identified from soft links.
        
        Args:
            best_run_ids: Dictionary containing best run IDs for each stage
            
        Returns:
            True if any QoR summaries were found, False otherwise
        """
        if not best_run_ids:
            self.log_message("No best run IDs provided", "BEST_RUN_QOR")
            return False
        
        self.log_message("Starting best run QoR summary extraction", "BEST_RUN_QOR")
                
        overall_success = False
        
        # Map stage names to their corresponding directories
        stage_mapping = {
            "compile": "compile_1",
            "clock": "clock_1", 
            "route": "route_1"
        }
        
        # Process each best run
        for link_name, run_id in best_run_ids.items():
            if not run_id:
                self.log_message(f"⚠ No best run ID found for {link_name}", "BEST_RUN_QOR")
                with open(self.log_file, 'a') as log_f:
                    log_f.write(f"BEST_RUN_{link_name.upper()}: NO RUN ID FOUND\n\n")
                continue
            
            # Get the corresponding stage directory name
            stage_name = stage_mapping.get(link_name, link_name)
            
            # Construct path to the run directory
            work_fcdso_dir = os.path.join(self.reference_dir, "runs", self.block_name, self.tech, self.apr_fc, "work_fcdso")
            stage_dir = os.path.join(work_fcdso_dir, stage_name, "dso_work_dir")
            run_dir = os.path.join(stage_dir, run_id)
            
            self.log_message(f"Processing BEST RUN for {link_name.upper()}: {run_id}", "BEST_RUN_QOR")
            
            # Check if the run directory exists
            if not os.path.exists(run_dir):
                self.log_message(f"⚠ Best run directory not found: {run_dir}", "BEST_RUN_QOR")
                with open(self.log_file, 'a') as log_f:
                    log_f.write(f"BEST_RUN_{link_name.upper()}: {run_id} - DIRECTORY NOT FOUND\n")
                    log_f.write(f"EXPECTED_PATH: {run_dir}\n\n")
                continue
            
            # Extract QoR summaries for this best run
            success = self.extract_qor_from_run_dir(run_dir, f"BEST_{link_name.upper()}")
            
            if success:
                overall_success = True
                self.log_message(f"✓ QoR summaries found for BEST {link_name.upper()} run: {run_id}", "BEST_RUN_QOR")
            else:
                self.log_message(f"⚠ No QoR summaries found for BEST {link_name.upper()} run: {run_id}", "BEST_RUN_QOR")
            
            # Write end of best run section
            with open(self.log_file, 'a') as log_f:
                log_f.write(f"\n{'*'*80}\n")
                log_f.write(f"END OF BEST RUN - {link_name.upper()} STAGE\n")
                log_f.write(f"{'*'*80}\n\n")
        
        return overall_success
    
    def generate_summary(self):
        """Generate final summary and close the log."""
        with open(self.log_file, 'a') as log_f:
            log_f.write(f"\n{'='*80}\n")
            log_f.write("WORK_FCDSO ANALYSIS COMPLETED\n")
            log_f.write(f"COMPLETION_TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_f.write(f"{'='*80}\n")
        
        # Add file size info
        try:
            log_size = os.path.getsize(self.log_file)
            self.log_message(f"Summary log file size: {log_size} bytes", "FINAL_SUMMARY")
            self.log_message(f"Summary log location: {self.log_file}", "FINAL_SUMMARY")
        except Exception as e:
            self.log_message(f"Error getting log file size: {e}", "ERROR")
        
        print(f"\nwork_fcdso analysis complete! Check the log file: {self.log_file}")
    
    def run_analysis(self):
        """
        Run the work_fcdso results analysis.
        """
        try:
            print(f"\n{'='*60}")
            print("Starting work_fcdso Analysis")
            print(f"{'='*60}")
            
            # Check if required parameters are provided
            if not all([self.block_name, self.tech, self.apr_fc]):
                self.print_status("Missing required parameters", "ERROR")
                return False
            
            # Extract best run IDs first
            best_run_ids = self.extract_best_run_ids()
            
            # Extract QoR summaries for best runs first
            if best_run_ids and any(best_run_ids.values()):
                self.print_status("Extracting QoR summaries for best runs...", "PROCESSING")
                best_run_success = self.extract_best_run_qor_summaries(best_run_ids)
                if best_run_success:
                    self.print_status("Best run QoR summaries extracted", "SUCCESS")
                else:
                    self.print_status("No QoR summaries found in best runs", "WARNING")
            else:
                best_run_success = False
            
            # Extract work_fcdso results for all runs
            all_runs_success = self.extract_work_fcdso_results()
            
            # Generate final summary
            self.generate_summary()
            
            overall_success = best_run_success or all_runs_success
            
            print(f"\n{'='*60}")
            if overall_success:
                self.print_status("Analysis completed successfully!", "SUCCESS")
                print(f"✓ Results saved to: {self.log_file}")
            else:
                self.print_status("Analysis failed - no QoR summaries found", "ERROR")
            print(f"{'='*60}")
            
            return overall_success
            
        except Exception as e:
            self.print_status(f"Analysis failed: {e}", "ERROR")
            return False


def get_interactive_inputs():
    """Get inputs from user via interactive prompts."""
    print("="*60)
    print("Work_FCDSO Results Summary Analysis Tool")
    print("="*60)
    
    # Get reference directory
    while True:
        reference_dir = input("Enter reference directory path: ").strip()
        if reference_dir:
            if os.path.exists(reference_dir):
                break
            else:
                print(f"ERROR: Directory '{reference_dir}' does not exist. Please try again.")
        else:
            print("ERROR: Reference directory path cannot be empty.")
    
    # Get block name
    while True:
        block_name = input("Enter block name (e.g., par_cbpma, dhm): ").strip()
        if block_name:
            break
        else:
            print("ERROR: Block name cannot be empty.")
    
    # Get technology
    while True:
        tech = input("Enter technology node (e.g., 1278.6): ").strip()
        if tech:
            break
        else:
            print("ERROR: Technology node cannot be empty.")
    
    # Get APR_FC directory name
    while True:
        apr_fc = input("Enter APR_FC directory name: ").strip()
        if apr_fc:
            break
        else:
            print("ERROR: APR_FC directory name cannot be empty.")
    
    # Get output directory
    output_dir = input("Enter output directory path").strip()
    if not output_dir:
        output_dir = None
        print("Using reference directory for output.")
    elif not os.path.exists(os.path.dirname(output_dir)) and os.path.dirname(output_dir):
        print(f"WARNING: Output directory parent '{os.path.dirname(output_dir)}' may not exist.")
        create_output = input("Continue anyway? (y/n): ").strip().lower()
        if create_output != 'y':
            output_dir = None
            print("Using reference directory for output.")
    
    return reference_dir, output_dir, block_name, tech, apr_fc


def validate_args(args):
    """Validate command line arguments."""
    errors = []
    
    if not args.reference_dir:
        errors.append("reference_dir is required")
    elif not os.path.exists(args.reference_dir):
        errors.append(f"reference_dir '{args.reference_dir}' does not exist")
    
    if not args.block_name:
        errors.append("block_name is required")
    if not args.tech:
        errors.append("tech is required")
    if not args.apr_fc:
        errors.append("apr_fc is required")
    
    if args.output_dir and not os.path.exists(os.path.dirname(args.output_dir)) and os.path.dirname(args.output_dir):
        errors.append(f"output_dir parent directory '{os.path.dirname(args.output_dir)}' does not exist")
    
    if errors:
        print("Error: Missing or invalid required arguments:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)


def main():
    """
    Main function with support for both interactive and command-line modes.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Work_FCDSO Results Summary Analysis Tool')
    parser.add_argument('--interactive', action='store_true',
                       help='Run in interactive mode with command line prompts')
    
    # Non-interactive mode arguments
    parser.add_argument('--reference_dir', type=str, required=False,
                       help='Reference directory path to analyze')
    parser.add_argument('--output_dir', type=str, required=False,
                       help='Output directory path')
    parser.add_argument('--block_name', type=str, required=False,
                       help='Block name (e.g., par_cbpma, dhm)')
    parser.add_argument('--tech', type=str, required=False,
                       help='Technology node (e.g., 1278.6)')
    parser.add_argument('--apr_fc', type=str, required=False,
                       help='APR_FC directory name')
    
    args = parser.parse_args()

    # Determine if we're in interactive mode
    if args.interactive:
        # Interactive mode - get inputs via prompts
        reference_dir, output_dir, block_name, tech, apr_fc = get_interactive_inputs()
    else:
        # Non-interactive mode - use command line arguments
        # Check if all required arguments are provided
        missing_args = []
        if not args.reference_dir:
            missing_args.append('--reference_dir')
        if not args.block_name:
            missing_args.append('--block_name')
        if not args.tech:
            missing_args.append('--tech')
        if not args.apr_fc:
            missing_args.append('--apr_fc')
        if not args.output_dir:
            missing_args.append('--output_dir')
        
        if missing_args:
            print("Error: The following required arguments are missing:", file=sys.stderr)
            for arg in missing_args:
                print(f"  {arg}", file=sys.stderr)
            print("\nUse --interactive flag to run in interactive mode, or provide all required arguments.", file=sys.stderr)
            print("Run with --help to see all available options.", file=sys.stderr)
            sys.exit(1)
        
        # Validate arguments
        validate_args(args)
        
        reference_dir = args.reference_dir
        output_dir = args.output_dir
        block_name = args.block_name
        tech = args.tech
        apr_fc = args.apr_fc

    # Display configuration
    print("\n" + "="*60)
    print("Configuration Summary:")
    print("="*60)
    print(f"Reference Directory: {reference_dir}")
    print(f"Output Directory: {output_dir or 'Same as reference directory'}")
    print(f"Block Name: {block_name}")
    print(f"Technology: {tech}")
    print(f"APR_FC Directory: {apr_fc}")
    
    # Show expected paths
    work_fcdso_path = os.path.join(reference_dir, "runs", block_name, tech, apr_fc, "work_fcdso")
    print(f"\nExpected paths:")
    print(f"  work_fcdso directory: {work_fcdso_path}")
    print(f"  Stage directories: compile_1, clock_1, route_1")
    print(f"  Looking for: .run* subdirectories with logs/")
    print("="*60)
    
    # In interactive mode, ask for confirmation
    if args.interactive:
        proceed = input("\nProceed with analysis? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Analysis cancelled.")
            sys.exit(0)
    
    print("\nStarting work_fcdso analysis...")
    print("-" * 50)
    
    # Create summarizer instance
    summarizer = WorkFcdsoSummarizer(reference_dir, output_dir, block_name, tech, apr_fc)
    
    # Run analysis
    success = summarizer.run_analysis()
    
    if success:
        print("\n✓ work_fcdso analysis completed successfully!")
        print(f"Check the summary log: {summarizer.log_file}")
    else:
        print("\n✗ work_fcdso analysis failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()