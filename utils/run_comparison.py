#!/usr/bin/env python3
"""
QoR Comparison Script
====================
This script compares QoR summaries between APR_FC runs and Phoenix best runs
for specific stages (compile, clock, or route).
"""

import os
import sys
import re
import argparse
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class QoRComparator:
    """
    A class to compare QoR summaries between APR_FC and Phoenix best runs.
    """
    
    def __init__(self, apr_fc_summary: str, phoenix_summary: str, output_dir: str, stage: str):
        """
        Initialize the QoRComparator.
        
        Args:
            apr_fc_summary: Path to summary.log file
            phoenix_summary: Path to work_fcdso_summary.log file
            output_dir: Directory where comparison output will be saved
            stage: Stage to compare (compile, clock, or route)
        """
        self.apr_fc_summary = apr_fc_summary
        self.phoenix_summary = phoenix_summary
        self.output_dir = output_dir
        self.stage = stage.lower()
        self.log_file = os.path.join(output_dir, f"qor_comparison_{self.stage}.log")
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize log file
        self._initialize_log()
    
    def _initialize_log(self):
        """Initialize the comparison log file."""
        with open(self.log_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write(f"QOR COMPARISON ANALYSIS - {self.stage.upper()} STAGE\n")
            f.write("="*80 + "\n")
            f.write(f"Analysis started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"APR_FC summary: {self.apr_fc_summary}\n")
            f.write(f"Phoenix summary: {self.phoenix_summary}\n")
            f.write(f"Stage: {self.stage}\n")
            f.write("="*80 + "\n\n")
    
    def log_message(self, message: str):
        """Log a message to the comparison log file."""
        with open(self.log_file, 'a') as f:
            f.write(message + '\n')
        print(message)
    
    def parse_qor_line(self, line: str) -> Optional[Dict[str, str]]:
        """
        Parse a QoR Summary line and extract metrics.
        
        Returns:
            Dictionary with QoR metrics or None if parsing fails
        """
        # Remove the RUN_ID and slice suffixes if present
        line_to_parse = re.sub(r'\s*\|\s*(RUN_ID|stage):.*$', '', line)
        
        # Extract the numerical values from the QoR line
        # More flexible pattern to handle various QoR line formats
        pattern = r'QoR Summary\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s+([\d-]+)\s+([\d.-]+)\s+([\d.-]+)\s+([\d-]+)\s+([\d-]+)\s+([\d-]+)\s+([\d.]+)\s+([\d.]+)\s+([\d]+)'
        
        match = re.search(pattern, line_to_parse)
        if match:
            return {
                'WNS': match.group(1),
                'TNS': match.group(2),
                'R2RTNS': match.group(3),
                'NSV': match.group(4),
                'WHV': match.group(5),
                'THV': match.group(6),
                'NHV': match.group(7),
                'MaxTrnV': match.group(8),
                'MaxCapV': match.group(9),
                'Leakage': match.group(10),
                'Area': match.group(11),
                'InstCnt': match.group(12)
            }
        return None
    
    def extract_best_run_id(self, phoenix_summary: str) -> Optional[str]:
        """Extract the best run ID for the specified stage from Phoenix summary."""
        stage_mapping = {
            'compile': 'COMPILE_BEST_RUN',
            'clock': 'CLOCK_BEST_RUN',
            'route': 'ROUTE_BEST_RUN'
        }
        
        search_key = stage_mapping.get(self.stage)
        if not search_key:
            return None
        
        try:
            with open(phoenix_summary, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if search_key in line:
                        # Extract run ID from line like "COMPILE_BEST_RUN: .run_85f5a31"
                        match = re.search(r'\.run_[a-f0-9]+', line)
                        if match:
                            return match.group(0)
        except Exception as e:
            self.log_message(f"Error extracting best run ID: {e}")
        
        return None
    
    def extract_apr_fc_qor(self) -> Dict[str, List[Tuple[str, Dict[str, str]]]]:
        """Extract QoR data from APR_FC summary for the specified stage."""
        apr_qor_data = {}
        
        # Define log files to search based on stage
        if self.stage == 'compile':
            log_files = {
                'compile_initial_opto': 'fc.compile_initial_opto.log',
                'compile_final_opto': 'fc.compile_final_opto.log'
            }
        elif self.stage == 'clock':
            log_files = {
                'clock_route_opt': 'fc.clock_route_opt.log'
            }
        elif self.stage == 'route':
            log_files = {
                'route_opt': 'fc.route_opt.log'
            }
        else:
            return apr_qor_data
        
        try:
            with open(self.apr_fc_summary, 'r', encoding='utf-8', errors='ignore') as f:
                current_log = None
                for line in f:
                    # Check if we're entering a new log file section
                    for key, log_name in log_files.items():
                        if f"LOG FILE: {log_name}" in line:
                            current_log = key
                            # Only initialize the list if it's not already there
                            if current_log not in apr_qor_data:
                                apr_qor_data[current_log] = []
                            break
                    
                    # Parse QoR Summary lines that match the current stage
                    if current_log and "QoR Summary" in line and f"| stage: {self.stage}" in line:
                        # Extract the QoR description (before the metrics)
                        qor_desc_match = re.search(r'Line \d+: (.+?)\s+[\d.-]+\s+[\d.-]+', line)
                        qor_desc = qor_desc_match.group(1).strip() if qor_desc_match else "QoR Summary"
                        
                        qor_metrics = self.parse_qor_line(line)
                       
                        if qor_metrics:
                            apr_qor_data[current_log].append((qor_desc, qor_metrics))

        except Exception as e:
            self.log_message(f"Error extracting APR_FC QoR: {e}")

        return apr_qor_data
    
    def extract_phoenix_best_qor(self, run_id: str) -> Dict[str, List[Tuple[str, Dict[str, str]]]]:
        """Extract QoR data from Phoenix summary for the best run of specified stage."""
        qor_data = {}
        
        # Define the stage prefix to search for
        stage_prefix = f"BEST_{self.stage.upper()}"
        
        # Define log files based on stage
        if self.stage == 'compile':
            log_files = {
                'compile_initial_opto': 'fc.compile_initial_opto.log',
                'compile_final_opto': 'fc.compile_final_opto.log'
            }
        elif self.stage == 'clock':
            log_files = {
                'clock_route_opt': 'fc.clock_route_opt.log'
            }
        elif self.stage == 'route':
            log_files = {
                'route_opt': 'fc.route_opt.log'
            }
        else:
            return qor_data
        
        try:
            with open(self.phoenix_summary, 'r', encoding='utf-8', errors='ignore') as f:
                in_best_run_section = False
                current_log = None
                
                for line in f:
                    # Check if we're in the BEST_RUN section for our stage
                    if f"STAGE: {stage_prefix}" in line:
                        in_best_run_section = True
                        continue
                    
                    # Check if we've left the section
                    if in_best_run_section and "END OF" in line and stage_prefix in line:
                        in_best_run_section = False
                        continue
                    
                    if in_best_run_section:
                        # Check if we're entering a new log file section
                        for key, log_name in log_files.items():
                            if f"LOG_FILE: {log_name}" in line:
                                current_log = key
                                qor_data[current_log] = []
                                break
                        
                        # Parse QoR Summary lines (Phoenix format has RUN_ID at end)
                        if current_log and "QoR Summary" in line and run_id in line:
                            # Extract the QoR description (before the metrics)
                            qor_desc_match = re.search(r'Line \d+: (.+?)\s+[\d.-]+\s+[\d.-]+', line)
                            qor_desc = qor_desc_match.group(1).strip() if qor_desc_match else "QoR Summary"
                            
                            qor_metrics = self.parse_qor_line(line)
                            if qor_metrics:
                                qor_data[current_log].append((qor_desc, qor_metrics))
                                
        
        except Exception as e:
            self.log_message(f"Error extracting Phoenix best QoR: {e}")
        # print("phoenix", qor_data)
        return qor_data
    
    def create_comparison_table(self, log_type: str, apr_fc_data: List[Tuple[str, Dict[str, str]]], 
                                phoenix_data: List[Tuple[str, Dict[str, str]]]) -> str:
        """Create a formatted comparison table for a specific log type."""
        table = []
        table.append(f"\n{'='*120}")
        table.append(f"{log_type.upper()} COMPARISON")
        table.append(f"{'='*120}")
        
        if not apr_fc_data and not phoenix_data:
            table.append("No data available for comparison")
            return '\n'.join(table)
        
        # Metrics to compare
        metrics = ['WNS', 'TNS', 'R2RTNS', 'NSV', 'WHV', 'THV', 'NHV', 'MaxTrnV', 'MaxCapV', 'Leakage', 'Area', 'InstCnt']
        
        # Compare all QoR entries
        max_entries = max(len(apr_fc_data), len(phoenix_data))
        
        for idx in range(max_entries):
            # Get QoR description and data
            apr_fc_desc, apr_fc_qor = apr_fc_data[idx] if idx < len(apr_fc_data) else ("N/A", {})
            phoenix_desc, phoenix_qor = phoenix_data[idx] if idx < len(phoenix_data) else ("N/A", {})
            
            # Section header
            table.append(f"\n--- QoR Entry #{idx + 1} ---")
            table.append(f"APR_FC:  {apr_fc_desc}")
            table.append(f"Phoenix: {phoenix_desc}")
            table.append("-" * 120)
            
            # Header
            table.append(f"{'Metric':<15} {'APR_FC':<20} {'Phoenix Best':<20} {'Delta':<20} {'Improvement (%)':<20}")
            table.append("-" * 120)
            
            for metric in metrics:
                apr_val = apr_fc_qor.get(metric, 'N/A')
                phoenix_val = phoenix_qor.get(metric, 'N/A')
                
                # Calculate delta and improvement
                delta = 'N/A'
                improvement = 'N/A'
                
                if apr_val != 'N/A' and phoenix_val != 'N/A' and apr_val != '-' and phoenix_val != '-':
                    try:
                        apr_num = float(apr_val)
                        phoenix_num = float(phoenix_val)
                        
                        # Delta calculation: apr - phoenix
                        delta_num = apr_num - phoenix_num
                        delta = f"{delta_num:+.2f}"
                        
                        # Percentage improvement calculation
                        if apr_num != 0:
                            improvement_num = -((delta_num / apr_num) * 100)
                            improvement = f"{improvement_num:+.2f}%"
                    
                    except (ValueError, TypeError):
                        pass
                
                table.append(f"{metric:<15} {str(apr_val):<20} {str(phoenix_val):<20} {delta:<20} {improvement:<20}")
        
        table.append("="*120)
        
        return '\n'.join(table)
    
    def run_comparison(self) -> bool:
        """Run the QoR comparison analysis."""
        try:
            self.log_message(f"\n{'='*60}")
            self.log_message(f"Starting {self.stage.upper()} Stage QoR Comparison")
            self.log_message(f"{'='*60}\n")
            
            # Extract best run ID from Phoenix summary
            self.log_message("Step 1: Extracting best run ID from Phoenix summary...")
            best_run_id = self.extract_best_run_id(self.phoenix_summary)
            
            if not best_run_id:
                self.log_message(f"ERROR: Could not find best run ID for {self.stage} stage")
                return False
            
            self.log_message(f"✓ Best run ID found: {best_run_id}\n")
            
            # Extract APR_FC QoR data
            self.log_message("Step 2: Extracting APR_FC QoR data...")
            apr_fc_qor = self.extract_apr_fc_qor()
            
            
            if not apr_fc_qor:
                self.log_message(f"ERROR: Could not extract APR_FC QoR data for {self.stage} stage")
                return False
            
            # Show extracted counts
            for log_type, data in apr_fc_qor.items():
                self.log_message(f"  {log_type}: {len(data)} QoR entries")
            
            # Extract Phoenix best run QoR data
            self.log_message("\nStep 3: Extracting Phoenix best run QoR data...")
            phoenix_qor = self.extract_phoenix_best_qor(best_run_id)
            
            if not phoenix_qor:
                self.log_message(f"ERROR: Could not extract Phoenix QoR data for {self.stage} stage")
                return False
            
            # Show extracted counts
            for log_type, data in phoenix_qor.items():
                self.log_message(f"  {log_type}: {len(data)} QoR entries")
            
            # Generate comparison tables
            self.log_message("\nStep 4: Generating comparison tables...\n")
            
            # Compare data for each log type
            all_log_types = set(apr_fc_qor.keys()) | set(phoenix_qor.keys())
            
            for log_type in sorted(all_log_types):
                apr_data = apr_fc_qor.get(log_type, [])
                phoenix_data = phoenix_qor.get(log_type, [])
                
                comparison_table = self.create_comparison_table(log_type, apr_data, phoenix_data)
                self.log_message(comparison_table)
            
            # Final summary
            self.log_message(f"\n{'='*60}")
            self.log_message("COMPARISON COMPLETED SUCCESSFULLY")
            self.log_message(f"{'='*60}")
            self.log_message(f"Results saved to: {self.log_file}\n")
            
            return True
            
        except Exception as e:
            self.log_message(f"ERROR: Comparison failed: {e}")
            import traceback
            self.log_message(traceback.format_exc())
            return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='QoR Comparison Tool - Compare APR_FC and Phoenix Best Runs')
    
    parser.add_argument('--apr_fc_summary', type=str, required=True,
                       help='Path to summary.log file from APR_FC run')
    parser.add_argument('--phoenix_summary', type=str, required=True,
                       help='Path to work_fcdso_summary.log file from Phoenix run')
    parser.add_argument('--output_dir', type=str, required=True,
                       help='Output directory for comparison results')
    parser.add_argument('--stage', type=str, required=True, choices=['compile', 'clock', 'route'],
                       help='Stage to compare (compile, clock, or route)')
    
    args = parser.parse_args()
    
    # Validate input files
    if not os.path.exists(args.apr_fc_summary):
        print(f"ERROR: APR_FC summary file not found: {args.apr_fc_summary}", file=sys.stderr)
        sys.exit(1)
    
    if not os.path.exists(args.phoenix_summary):
        print(f"ERROR: Phoenix summary file not found: {args.phoenix_summary}", file=sys.stderr)
        sys.exit(1)
    
    # Display configuration
    print("\n" + "="*60)
    print("QoR Comparison Configuration")
    print("="*60)
    print(f"APR_FC Summary: {args.apr_fc_summary}")
    print(f"Phoenix Summary: {args.phoenix_summary}")
    print(f"Output Directory: {args.output_dir}")
    print(f"Stage: {args.stage}")
    print("="*60 + "\n")
    
    # Create comparator and run analysis
    comparator = QoRComparator(args.apr_fc_summary, args.phoenix_summary, 
                               args.output_dir, args.stage)
    
    success = comparator.run_comparison()
    
    if success:
        print("\n✓ Comparison completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ Comparison failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()