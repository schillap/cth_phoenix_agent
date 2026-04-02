#!/usr/bin/env python3
"""
Runtime Memory Summary Script
============================
This script navigates to runs/$block_name/$tech/$apr_fc/reports/ 
and appends $block_name.RUNTIME_MEM_summary.txt contents to summary.log
"""

import os
import sys
import argparse
from datetime import datetime
from utils import log_with_timestamp

class DirectorySummarizer:
    """
    A class to handle runtime memory summary extraction and logging.
    """
    
    def __init__(self, reference_dir, output_dir, block_name, tech, apr_fc):
        """
        Initialize the DirectorySummarizer.
        
        Args:
            reference_dir: The reference directory to analyze
            output_dir: Directory where summary.log will be created
            block_name: Block name for navigating to specific reports directory
            tech: Technology node for directory path
            apr_fc: APR_FC directory name
        """
        self.reference_dir = os.path.abspath(reference_dir)
        self.output_dir = output_dir
        self.log_file = os.path.join(self.output_dir, f"{block_name}_apr_fc_summary.log")
        self.summary_data = {}
        self.block_name = block_name
        self.tech = tech
        self.apr_fc = apr_fc
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize log file
        self._initialize_log()
    
    def _initialize_log(self):
        """Initialize the summary.log file with header information."""
        with open(self.log_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("RUNTIME MEMORY SUMMARY ANALYSIS\n")
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
    
    def log_message(self, message, section="RUNTIME_MEMORY"):
        """
        Log a message to summary.log file.
        
        Args:
            message: Message to log
            section: Section header for organization
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted_message = f"[{timestamp}] [{section}] {message}"
        
        with open(self.log_file, 'a') as f:
            f.write(formatted_message + '\n')

    
    def append_runtime_memory_summary(self):
        """
        Navigate to runs/$block_name/$tech/$apr_fc/reports/ and append 
        $block_name.RUNTIME_MEM_summary.txt contents to the summary log.
        """
        if not all([self.block_name, self.tech, self.apr_fc]):
            self.log_message("ERROR: Missing required parameters (block_name, tech, apr_fc) for runtime memory summary", "RUNTIME_MEMORY")
            return False
        
        # Construct the path to the reports directory
        reports_dir = os.path.join(self.reference_dir, "runs", self.block_name, self.tech, self.apr_fc, "reports")
        runtime_mem_file = os.path.join(reports_dir, f"{self.block_name}.RUNTIME_MEM_summary.txt")
        
        self.log_message("Starting runtime memory summary analysis", "RUNTIME_MEMORY")
        self.log_message(f"Looking for reports directory: {reports_dir}", "RUNTIME_MEMORY")
        self.log_message(f"Target file: {self.block_name}.RUNTIME_MEM_summary.txt", "RUNTIME_MEMORY")
        
        # Check if reports directory exists
        if not os.path.exists(reports_dir):
            self.log_message(f"ERROR: Reports directory does not exist: {reports_dir}", "RUNTIME_MEMORY")
            return False
        
        self.log_message(f"✓ Reports directory found: {reports_dir}", "RUNTIME_MEMORY")
        
        # Check if the runtime memory summary file exists
        if not os.path.exists(runtime_mem_file):
            self.log_message(f"ERROR: Runtime memory summary file does not exist: {runtime_mem_file}", "RUNTIME_MEMORY")
            
            # List available files in reports directory for troubleshooting
            try:
                available_files = os.listdir(reports_dir)
                self.log_message(f"Available files in reports directory:", "RUNTIME_MEMORY")
                for file_name in available_files:
                    if file_name.endswith('.txt') or 'RUNTIME' in file_name or 'MEM' in file_name:
                        self.log_message(f"  - {file_name}", "RUNTIME_MEMORY")
            except Exception as e:
                self.log_message(f"Error listing files in reports directory: {e}", "RUNTIME_MEMORY")
            
            return False
        
        self.log_message(f"✓ Runtime memory summary file found: {runtime_mem_file}", "RUNTIME_MEMORY")
        
        # Get file info
        try:
            file_size = os.path.getsize(runtime_mem_file)
            file_mtime = datetime.fromtimestamp(os.path.getmtime(runtime_mem_file)).strftime('%Y-%m-%d %H:%M:%S')
            self.log_message(f"File size: {file_size} bytes, Last modified: {file_mtime}", "RUNTIME_MEMORY")
        except Exception as e:
            self.log_message(f"Warning: Could not get file info: {e}", "RUNTIME_MEMORY")
        
        # Read and append the runtime memory summary file contents
        try:
            self.log_message("Reading runtime memory summary file contents...", "RUNTIME_MEMORY")
            
            with open(runtime_mem_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                self.log_message("WARNING: Runtime memory summary file is empty", "RUNTIME_MEMORY")
                return False
            
            # Write separator and content to log file
            with open(self.log_file, 'a') as log_f:
                log_f.write("\n" + "="*80 + "\n")
                log_f.write(f"RUNTIME MEMORY SUMMARY - {self.block_name}.RUNTIME_MEM_summary.txt\n")
                log_f.write(f"Source: {runtime_mem_file}\n")
                log_f.write(f"Appended on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                log_f.write("="*80 + "\n\n")
                log_f.write(content)
                if not content.endswith('\n'):
                    log_f.write('\n')
                log_f.write("\n" + "="*80 + "\n")
                log_f.write("END OF RUNTIME MEMORY SUMMARY\n")
                log_f.write("="*80 + "\n\n")
            
            # Count lines for summary
            all_lines = content.split('\n')
            # Remove trailing empty line if content ends with newline
            if all_lines and not all_lines[-1].strip():
                all_lines = all_lines[:-1]
            line_count = len(all_lines)
            self.log_message(f"✓ Successfully appended runtime memory summary ({line_count} lines)", "RUNTIME_MEMORY")
            
            return True
            
        except Exception as e:
            self.log_message(f"ERROR: Failed to read/append runtime memory summary file: {e}", "RUNTIME_MEMORY")
            return False
    
    def extract_qor_summary(self):
        """
        Navigate to runs/$block_name/$tech/$apr_fc/logs/ and grep 
        "QoR Summary" from specified log files.
        """
        if not all([self.block_name, self.tech, self.apr_fc]):
            self.log_message("ERROR: Missing required parameters (block_name, tech, apr_fc) for QoR summary extraction", "QOR_SUMMARY")
            return False
        
        # Construct the path to the logs directory
        logs_dir = os.path.join(self.reference_dir, "runs", self.block_name, self.tech, self.apr_fc, "logs") 
        
        # Define the log files to search with their slice type
        log_files = [
            ("fc.compile_initial_opto.log", "compile"),
            ("fc.compile_final_opto.log", "compile"),
            ("fc.clock_route_opt.log", "clock"),
            ("fc.route_opt.log", "route")
        ]
        
        self.log_message("Starting QoR Summary extraction", "QOR_SUMMARY")
        self.log_message(f"Looking for logs directory: {logs_dir}", "QOR_SUMMARY")
        
        # Check if logs directory exists
        if not os.path.exists(logs_dir):
            self.log_message(f"ERROR: Logs directory does not exist: {logs_dir}", "QOR_SUMMARY")
            return False
        
        self.log_message(f"✓ Logs directory found: {logs_dir}", "QOR_SUMMARY")
        
        # Write QoR Summary section header to log file
        with open(self.log_file, 'a') as log_f:
            log_f.write("\n" + "="*80 + "\n")
            log_f.write("QOR SUMMARY EXTRACTION\n")
            log_f.write(f"Source directory: {logs_dir}\n")
            log_f.write(f"Extracted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_f.write("="*80 + "\n\n")
        
        qor_found = False
        
        # Process each log file
        for log_file, slice_type in log_files:
            log_file_path = os.path.join(logs_dir, log_file)
            
            self.log_message(f"Processing log file: {log_file}", "QOR_SUMMARY")
            
            if not os.path.exists(log_file_path):
                self.log_message(f"⚠ Log file not found: {log_file}", "QOR_SUMMARY")
                with open(self.log_file, 'a') as log_f:
                    log_f.write(f"LOG FILE: {log_file} - NOT FOUND\n\n")
                continue
            
            # Get file info
            try:
                file_size = os.path.getsize(log_file_path)
                file_mtime = datetime.fromtimestamp(os.path.getmtime(log_file_path)).strftime('%Y-%m-%d %H:%M:%S')
                self.log_message(f"File size: {file_size} bytes, Last modified: {file_mtime}", "QOR_SUMMARY")
            except Exception as e:
                self.log_message(f"Warning: Could not get file info for {log_file}: {e}", "QOR_SUMMARY")
            
            # Search for "QoR Summary" in the log file
            try:
                qor_lines = []
                with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        if "QoR Summary" in line:
                            # Add slice type to the end of the line
                            line_with_slice = f"{line.strip()} | stage: {slice_type}"
                            qor_lines.append((line_num, line_with_slice))
                
                if qor_lines:
                    qor_found = True
                    self.log_message(f"✓ Found {len(qor_lines)} QoR Summary matches in {log_file}", "QOR_SUMMARY")
                    
                    # Write to summary log
                    with open(self.log_file, 'a') as log_f:
                        log_f.write(f"LOG FILE: {log_file}\n")
                        log_f.write(f"Path: {log_file_path}\n")
                        log_f.write(f"QoR Summary matches found: {len(qor_lines)}\n")
                        log_f.write(f"Slice: {slice_type}\n")
                        log_f.write("-" * 60 + "\n")
                        
                        for line_num, line_content in qor_lines:
                            log_f.write(f"Line {line_num}: {line_content}\n")
                        
                        log_f.write("\n")
                    
                else:
                    self.log_message(f"⚠ No QoR Summary found in {log_file}", "QOR_SUMMARY")
                    with open(self.log_file, 'a') as log_f:
                        log_f.write(f"LOG FILE: {log_file} - NO QoR SUMMARY FOUND\n\n")
                        
            except Exception as e:
                self.log_message(f"ERROR: Failed to read log file {log_file}: {e}", "QOR_SUMMARY")
                with open(self.log_file, 'a') as log_f:
                    log_f.write(f"LOG FILE: {log_file} - ERROR READING FILE: {e}\n\n")
        
        # Write end section to log file
        with open(self.log_file, 'a') as log_f:
            log_f.write("\n" + "="*80 + "\n")
            log_f.write("END OF QOR SUMMARY EXTRACTION\n")
            log_f.write("="*80 + "\n\n")
        
        if qor_found:
            self.log_message("✓ QoR Summary extraction completed successfully", "QOR_SUMMARY")
        else:
            self.log_message("⚠ No QoR Summary found in any log files", "QOR_SUMMARY")
        
        return True
    
    def extract_tool_versions(self):
        """
        Navigate to runs/$block_name/$tech/$apr_fc/logs/ and grep 
        "tool" from specified log files, then extract "-version=" information.
        """
        if not all([self.block_name, self.tech, self.apr_fc]):
            self.log_message("ERROR: Missing required parameters (block_name, tech, apr_fc) for tool version extraction", "TOOL_VERSION")
            return False
        
        # Construct the path to the logs directory
        logs_dir = os.path.join(self.reference_dir, "runs", self.block_name, self.tech, self.apr_fc, "logs")
        
        # Define the log files to search
        log_files = [
            "fc.compile_initial_opto.log",
            "fc.compile_final_opto.log",
            "fc.clock_route_opt.log", 
            "fc.route_opt.log"
        ]
        
        self.log_message("Starting tool version extraction", "TOOL_VERSION")
        self.log_message(f"Looking for logs directory: {logs_dir}", "TOOL_VERSION")
        
        # Check if logs directory exists
        if not os.path.exists(logs_dir):
            self.log_message(f"ERROR: Logs directory does not exist: {logs_dir}", "TOOL_VERSION")
            return False
        
        self.log_message(f"✓ Logs directory found: {logs_dir}", "TOOL_VERSION")
        
        # Write Tool Version section header to log file
        with open(self.log_file, 'a') as log_f:
            log_f.write("\n" + "="*80 + "\n")
            log_f.write("TOOL VERSION EXTRACTION\n")
            log_f.write(f"Source directory: {logs_dir}\n")
            log_f.write(f"Extracted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_f.write("="*80 + "\n\n")
        
        versions_found = False
        
        # Process each log file
        for log_file in log_files:
            log_file_path = os.path.join(logs_dir, log_file)
            
            self.log_message(f"Processing log file: {log_file}", "TOOL_VERSION")
            
            if not os.path.exists(log_file_path):
                self.log_message(f"⚠ Log file not found: {log_file}", "TOOL_VERSION")
                with open(self.log_file, 'a') as log_f:
                    log_f.write(f"LOG FILE: {log_file} - NOT FOUND\n\n")
                continue
            
            # Search for "tool" lines and extract version information
            try:
                tool_lines = []
                version_info = []
                
                with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        if "tool=" in line.lower():
                            tool_lines.append((line_num, line.strip()))
                            
                            # Look for -version= in the line
                            if "-version=" in line:
                                # Extract the version information
                                import re
                                version_match = re.search(r'-version=([^\s]+)', line)
                                if version_match:
                                    version = version_match.group(1)
                                    # Extract tool name (assuming it's fc_shell or similar)
                                    tool_match = re.search(r'(\w*fc\w*|\w*shell\w*)', line, re.IGNORECASE)
                                    tool_name = tool_match.group(1) if tool_match else "fc_shell"
                                    version_info.append((line_num, tool_name, version, log_file))
                
                if tool_lines:
                    self.log_message(f"✓ Found {len(tool_lines)} tool-related lines in {log_file}", "TOOL_VERSION")
                    
                    # Write tool lines to summary log
                    with open(self.log_file, 'a') as log_f:
                        log_f.write(f"LOG FILE: {log_file}\n")
                        log_f.write(f"Path: {log_file_path}\n")
                        log_f.write(f"Tool-related lines found: {len(tool_lines)}\n")
                        log_f.write("-" * 60 + "\n")
                        
                        for line_num, line_content in tool_lines:
                            log_f.write(f"Line {line_num}: {line_content}\n")
                        
                        log_f.write("\n")
                    
                    # Log version information in the requested format
                    if version_info:
                        versions_found = True
                        self.log_message(f"✓ Found {len(version_info)} version entries in {log_file}", "TOOL_VERSION")
                        
                        with open(self.log_file, 'a') as log_f:
                            log_f.write("VERSION INFORMATION:\n")
                            for line_num, tool_name, version, source_file in version_info:
                                version_line = f"{tool_name} - {source_file}"
                                log_f.write(f"{version_line}: {version}\n")
                                self.log_message(f"  {version_line}: {version}", "TOOL_VERSION")
                            log_f.write("\n")
                    else:
                        self.log_message(f"⚠ No version information found in tool lines from {log_file}", "TOOL_VERSION")
                        with open(self.log_file, 'a') as log_f:
                            log_f.write("VERSION INFORMATION: No -version= found in tool lines\n\n")
                
                else:
                    self.log_message(f"⚠ No tool-related lines found in {log_file}", "TOOL_VERSION")
                    with open(self.log_file, 'a') as log_f:
                        log_f.write(f"LOG FILE: {log_file} - NO TOOL LINES FOUND\n\n")
                        
            except Exception as e:
                self.log_message(f"ERROR: Failed to read log file {log_file}: {e}", "TOOL_VERSION")
                with open(self.log_file, 'a') as log_f:
                    log_f.write(f"LOG FILE: {log_file} - ERROR READING FILE: {e}\n\n")
        
        # Write end section to log file
        with open(self.log_file, 'a') as log_f:
            log_f.write("\n" + "="*80 + "\n")
            log_f.write("END OF TOOL VERSION EXTRACTION\n")
            log_f.write("="*80 + "\n\n")
        
        if versions_found:
            self.log_message("✓ Tool version extraction completed successfully", "TOOL_VERSION")
        else:
            self.log_message("⚠ No tool versions found in any log files", "TOOL_VERSION")
        
        return True
    
    def generate_summary(self):
        """Generate final summary and close the log."""
        self.log_message("="*80, "FINAL_SUMMARY")
        self.log_message("ANALYSIS COMPLETED", "FINAL_SUMMARY")
        self.log_message("="*80, "FINAL_SUMMARY")
        
        # Add file size info
        try:
            log_size = os.path.getsize(self.log_file)
            self.log_message(f"Summary log file size: {log_size} bytes", "FINAL_SUMMARY")
            self.log_message(f"Summary log location: {self.log_file}", "FINAL_SUMMARY")
        except Exception as e:
            self.log_message(f"Error getting log file size: {e}", "FINAL_SUMMARY")
        
        print(f"\nSummary complete! Check the log file: {self.log_file}")
    
    def run_analysis(self):
        """
        Run the runtime memory summary and QoR summary analysis.
        """
        try:
            self.log_message("Starting analysis workflow", "WORKFLOW")
            
            # Check if required parameters are provided
            if not all([self.block_name, self.tech, self.apr_fc]):
                self.log_message("ERROR: Missing required parameters (block_name, tech, apr_fc)", "ERROR")
                return False
            
            # Step 1: Append runtime memory summary
            self.log_message("Step 1: Extracting runtime memory summary", "WORKFLOW")
            runtime_success = self.append_runtime_memory_summary()
            
            # Step 2: Extract QoR summaries from log files
            self.log_message("Step 2: Extracting QoR summaries from log files", "WORKFLOW")
            qor_success = self.extract_qor_summary()

            # Step 3: Extract tool version information
            self.log_message("Step 3: Extracting tool version information", "WORKFLOW")
            version_success = self.extract_tool_versions()
            
            # Generate final summary
            self.generate_summary()
            
            # Return True if at least one extraction was successful
            overall_success = runtime_success or qor_success or version_success
            
            if runtime_success and qor_success and version_success:
                self.log_message("✓ All extractions (runtime memory, QoR summary, and tool versions) completed successfully", "WORKFLOW")
            elif overall_success:
                successes = []
                if runtime_success: successes.append("runtime memory")
                if qor_success: successes.append("QoR summary")
                if version_success: successes.append("tool versions")
                self.log_message(f"✓ Partial success: {', '.join(successes)} extraction(s) completed", "WORKFLOW")
            else:
                self.log_message("✗ All extractions failed", "WORKFLOW")
            
            return overall_success
            
        except Exception as e:
            self.log_message(f"Error during analysis: {e}", "ERROR")
            return False


def get_interactive_inputs():
    """Get inputs from user via interactive prompts."""
    print("="*60)
    print("Runtime Memory & QoR Summary Analysis Tool")
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
    
    # Get block name/build name
    while True:
        block_name = input("Enter block name/build name (e.g., par_cbpma, dhm): ").strip()
        if block_name:
            break
        else:
            print("ERROR: Block name/build name cannot be empty.")
    
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
    output_dir = input("Enter output directory path: ").strip()
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
    if not args.output_dir:
        errors.append("output_dir is required")
    
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
    parser = argparse.ArgumentParser(description='Runtime Memory & QoR Summary Analysis Tool')
    parser.add_argument('--interactive', action='store_true',
                       help='Run in interactive mode with command line prompts')
    
    # Non-interactive mode arguments
    parser.add_argument('--reference_dir', type=str,
                       help='Reference directory path to analyze')
    parser.add_argument('--output_dir', type=str,
                       help='Output directory path')
    parser.add_argument('--block_name', type=str,
                       help='Block name (e.g., par_cbpma, dhm)')
    parser.add_argument('--tech', type=str,
                       help='Technology node (e.g., 1278.6)')
    parser.add_argument('--apr_fc', type=str,
                       help='APR_FC directory name')
    
    args = parser.parse_args()

    # Determine if we're in interactive mode
    if args.interactive:
        # Interactive mode
        reference_dir, output_dir, block_name, tech, apr_fc = get_interactive_inputs()
    else:
        # Non-interactive mode - validate all required arguments are provided
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
    reports_path = os.path.join(reference_dir, "runs", block_name, tech, apr_fc, "reports")
    logs_path = os.path.join(reference_dir, "runs", block_name, tech, apr_fc, "logs")
    print(f"\nExpected paths:")
    print(f"  Reports directory: {reports_path}")
    print(f"  Logs directory: {logs_path}")
    print("="*60)
    
    # In interactive mode, ask for confirmation
    if args.interactive:
        proceed = input("\nProceed with analysis? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Analysis cancelled.")
            sys.exit(0)
    
    print("\nStarting analysis...")
    print("-" * 50)
    
    # Create summarizer instance
    summarizer = DirectorySummarizer(reference_dir, output_dir, block_name, tech, apr_fc)
    
    # Run analysis
    success = summarizer.run_analysis()
    
    if success:
        print("\n✓ Analysis completed successfully!")
        print(f"Check the summary log: {summarizer.log_file}")
    else:
        print("\n✗ Analysis failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()