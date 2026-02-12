"""
RazorLake Sanity Checker Module for Phoenix Run Setup
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime

# Import centralized logging utilities
from utils import get_logger

# Get module-specific logger
logger = get_logger(__name__)


class CheckStatus(Enum):
    """Enumeration for check result status"""
    PASSED = "PASSED"
    FAILED = "FAILED"
    
@dataclass
class CheckResult:
    """Data class to encapsulate check results"""
    check_name: str
    status: CheckStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class SanityCheck(ABC):
    """Abstract base class for all sanity checks"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def execute(self, ward_path: str, block_name: str, tech: str, **kwargs) -> CheckResult:
        """Execute the sanity check"""
        pass
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"



class SanityChecker:
    """Main sanity checker class for Phoenix run setup validation"""
    
    def __init__(self, ward: str, block_name: str, tech: str, **kwargs):
        """
        Initialize the SanityChecker
        
        Args:
            ward: Path to the ward directory
            block_name: Block name
            tech: Technology node
            **kwargs: Additional arguments to pass to checks
        """
        self.ward = ward
        self.block_name = block_name
        self.tech = tech
        self.kwargs = kwargs  # Store kwargs
        self.checks: List[SanityCheck] = []
        self.results: List[CheckResult] = []
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info(f"Initialized SanityChecker for ward: {ward}")
    
    def add_check(self, check: SanityCheck) -> 'SanityChecker':
        """
        Add a sanity check to the checker
        
        Args:
            check: SanityCheck instance to add
            
        Returns:
            self for method chaining
        """
        self.checks.append(check)
        self.logger.debug(f"Added check: {check.name}")
        return self
    
    def add_default_checks(self) -> 'SanityChecker':
        """
        Add default set of sanity checks
        
        Returns:
            self for method chaining
        """
        # self.add_check(DirectoryStructureCheck())
        # self.add_check(ConfigFileCheck())
        # self.add_check(SymlinkCheck())
        # self.add_check(PermissionsCheck())
        # self.add_check(DiskSpaceCheck())
        self.logger.info("Added default sanity checks")
        return self
    
    def run_check(self, check: SanityCheck, **additional_kwargs) -> CheckResult:
        """
        Run a single sanity check
        
        Args:
            check: SanityCheck instance to execute
            **additional_kwargs: Additional arguments for this specific check
            
        Returns:
            CheckResult object
        """
        self.logger.info(f"Running check: {check.name}")
        # Merge stored kwargs with additional kwargs
        merged_kwargs = {**self.kwargs, **additional_kwargs}
        result = check.execute(self.ward, self.block_name, self.tech, **merged_kwargs)
        self.results.append(result)
        
        log_method = {
            CheckStatus.PASSED: self.logger.info,
            CheckStatus.FAILED: self.logger.error,
        }.get(result.status, self.logger.info)
        
        log_method(f"{result.check_name}: {result.status.value} - {result.message}")
        return result
    
    def run_all_checks(self) -> List[CheckResult]:
        """
        Run all registered sanity checks
        
        Returns:
            List of CheckResult objects
        """
        self.logger.info(f"Running {len(self.checks)} sanity checks for ward: {self.ward}")
        self.results = []
        
        for check in self.checks:
            self.run_check(check)  # Will use stored kwargs
        
        self.logger.info("Completed all sanity checks")
        return self.results
    
    def get_summary(self) -> Dict[str, int]:
        """
        Get a summary of check results
        
        Returns:
            Dictionary with counts per status
        """
        summary = {status.value: 0 for status in CheckStatus}
        for result in self.results:
            summary[result.status.value] += 1
        return summary
    
    def has_failures(self) -> bool:
        """
        Check if any checks failed
        
        Returns:
            True if any checks failed, False otherwise
        """
        return any(r.status == CheckStatus.FAILED for r in self.results)
    
    
    def print_report(self) -> None:
        """Print a formatted report of all check results"""
        print("\n" + "=" * 80)
        print(f"SANITY CHECK REPORT - Ward: {self.ward}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        for result in self.results:
            status_symbol = {
                CheckStatus.PASSED: "✓",
                CheckStatus.FAILED: "✗",
            }.get(result.status, "?")
            
            print(f"\n{status_symbol} {result.check_name}")
            print(f"  Status: {result.status.value}")
            print(f"  Message: {result.message}")
            if result.details:
                print(f"  Details: {result.details}")
            print(f"  Time: {result.timestamp.strftime('%H:%M:%S')}")
        
        print("\n" + "-" * 80)
        summary = self.get_summary()
        print("SUMMARY:")
        for status, count in summary.items():
            print(f"  {status}: {count}")
        print("=" * 80 + "\n")
    
    def clear_results(self) -> None:
        """Clear all stored results"""
        self.results = []
        self.logger.debug("Cleared all results")


