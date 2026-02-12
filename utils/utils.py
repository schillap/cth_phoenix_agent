#!/usr/bin/env python3

import os
import subprocess
from datetime import datetime

def log_with_timestamp(message, log_file):
    """Log message with timestamp to both console and file."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    with open(log_file, 'a') as log:
        log.write(log_message + '\n')

def copy_directory(src, dest, description, log_file=None):
    """Helper function to copy directories using subprocess with logging."""
    try:
        if os.path.isdir(src):
            # Use cp -r command to copy directory recursively
            result = subprocess.run(['cp', '-rLf', src, dest], 
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                  universal_newlines=True, check=True)
            message = f"✓ Successfully copied {description} from {src} to {dest}"
            print(message)
            if log_file:
                log_with_timestamp(message, log_file)
            return True
        else:
            message = f"⚠ {description} not found at {src}"
            print(message)
            if log_file:
                log_with_timestamp(message, log_file)
            return False
    except subprocess.CalledProcessError as e:
        message = f"✗ Error copying {description} from {src} to {dest}: {e.stderr}"
        print(message)
        if log_file:
            log_with_timestamp(message, log_file)
        return False
    except Exception as e:
        message = f"✗ Error copying {description} from {src} to {dest}: {e}"
        print(message)
        if log_file:
            log_with_timestamp(message, log_file)
        return False
    
def copy_file(src, dest, file, log_file=None):
    """Helper function to copy files using subprocess with logging."""
    try:
        if os.path.isfile(src):
            # Create destination directory if it doesn't exist
            dest_dir = os.path.dirname(dest)
            if dest_dir:
                subprocess.run(['mkdir', '-p', dest_dir], 
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             universal_newlines=True, check=True)
            
            # Use cp command to copy file
            result = subprocess.run(['cp', src, dest], 
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  universal_newlines=True, check=True)
            message = f"✓ Successfully copied {file} from {src} to {dest}"
            print(message)
            if log_file:
                log_with_timestamp(message, log_file)
            return True
        else:
            message = f"⚠ {file} not found at {src}"
            print(message)
            if log_file:
                log_with_timestamp(message, log_file)
            return False
    except subprocess.CalledProcessError as e:
        message = f"✗ Error copying {file} from {src} to {dest}: {e.stderr}"
        print(message)
        if log_file:
            log_with_timestamp(message, log_file)
        return False
    except Exception as e:
        message = f"✗ Error copying {file} from {src} to {dest}: {e}"
        print(message)
        if log_file:
            log_with_timestamp(message, log_file)
        return False

def create_directory_structure(base_path, structure, log_file=None):
    """Create multiple directory paths using subprocess."""
    for path in structure:
        try:
            full_path = os.path.join(base_path, path)
            print(f"Creating directory structure: {path}")
            # Use mkdir -p to create directory structure
            subprocess.run(['mkdir', '-p', full_path], 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         universal_newlines=True, check=True)
            if log_file:
                log_with_timestamp(f"Created directory: {full_path}", log_file)
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to create directory {full_path}: {e.stderr}"
            print(error_msg)
            if log_file:
                log_with_timestamp(error_msg, log_file)
            return False
        except Exception as e:
            error_msg = f"Failed to create directory {full_path}: {e}"
            print(error_msg)
            if log_file:
                log_with_timestamp(error_msg, log_file)
            return False
    return True

"""
Includes centralized logging configuration and common helpers
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
    date_format: Optional[str] = None
) -> logging.Logger:
    """
    Configure centralized logging for the entire application
    
    Args:
        level: Logging level (default: INFO)
        log_file: Optional file path to write logs
        log_format: Custom log format string
        date_format: Custom date format string
        
    Returns:
        Root logger instance
    """
    if log_format is None:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    if date_format is None:
        date_format = '%Y-%m-%d %H:%M:%S'
    
    # Create formatter
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        root_logger.info(f"Logging to file: {log_file}")
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def setup_production_logging(log_dir: str = "logs") -> logging.Logger:
    """
    Setup production-grade logging with rotation
    
    Args:
        log_dir: Directory to store log files
        
    Returns:
        Root logger instance
    """
    from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
    
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Rotating file handler for general logs (10MB per file, keep 5 backups)
    general_log = log_path / f"phoenix_{datetime.now().strftime('%Y%m%d')}.log"
    rotating_handler = RotatingFileHandler(
        general_log,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    rotating_handler.setLevel(logging.DEBUG)
    rotating_handler.setFormatter(formatter)
    root_logger.addHandler(rotating_handler)
    
    # Separate error log
    error_log = log_path / "error.log"
    error_handler = RotatingFileHandler(
        error_log,
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    root_logger.info("Production logging initialized")
    return root_logger


class LoggerAdapter(logging.LoggerAdapter):
    """
    Custom logger adapter to add contextual information
    Useful for adding request IDs, user info, etc.
    """
    def process(self, msg, kwargs):
        return f"[{self.extra.get('context', 'N/A')}] {msg}", kwargs