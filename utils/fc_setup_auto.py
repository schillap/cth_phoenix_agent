#!/usr/bin/env python3

import os
import subprocess
import sys
from utils import log_with_timestamp, copy_directory, copy_file, create_directory_structure

def setup_apr_fc_flow(destination_dir, ref_WA, block_name, technology, apr_fc_dir_name, design_name):
    """
    Main function to set up APR_FC flow.
    
    Args:
        destination_dir: User's ward directory
        ref_WA: Reference ward directory
        block_name: Block name/build name (e.g., par_cbpma, dhm)
        technology: Technology node (e.g., 1278.6)
        apr_fc_dir_name: APR_FC directory name
        design_name: Design name
    
    Returns:
        bool: True if successful, False otherwise
    """
    print("=== APR_FC FLOW SETUP IN PROGRESS ===\n")

    # Setup logging
    try:
        # Create destination directory using subprocess
        subprocess.run(['mkdir', '-p', destination_dir], 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                      universal_newlines=True, check=True)
        log_file = os.path.join(destination_dir, f"fc_setup_auto_{block_name}.log")
        print(f"Setting up logging to: {log_file}")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error creating destination directory: {e.stderr}")
        return False
    except Exception as e:
        print(f"✗ Error creating destination directory or log file: {e}")
        return False

    log_with_timestamp("=== APR_FC FLOW SETUP ===", log_file)
    log_with_timestamp(f"User directory: {destination_dir}", log_file)
    log_with_timestamp(f"Reference ward directory: {ref_WA}", log_file)
    log_with_timestamp(f"Block name: {block_name}", log_file)
    log_with_timestamp(f"Technology: {technology}", log_file)
    log_with_timestamp(f"APR_FC directory name: {apr_fc_dir_name}", log_file)
    log_with_timestamp(f"Design name: {design_name}", log_file)
    
    print("\n=== Executing Operations ===")

    # Navigate to user directory
    print(f"Navigating to user directory: {destination_dir}")
    try:
        os.chdir(destination_dir)
        log_with_timestamp(f"Successfully navigated to: {destination_dir}", log_file)
    except Exception as e:
        error_msg = f"✗ Failed to navigate to destination directory: {e}"
        print(error_msg)
        log_with_timestamp(error_msg, log_file)
        return False

    # Create necessary directory structure
    file_structure = [
        f"runs/{block_name}/{technology}/release/latest",
        f"runs/{block_name}/{technology}/apr_fc/outputs/insert_dft"
    ]
    
    print("Creating directory structure...")
    if not create_directory_structure(destination_dir, file_structure, log_file):
        error_msg = "✗ Failed to create required directory structure"
        print(error_msg)
        log_with_timestamp(error_msg, log_file)
        return False

    print("\n=== Copying Files from Reference Ward Directory ===")

    # Copy hip_data - check for errors
    print("Copying hip_data...")
    if not copy_directory(
        os.path.join(ref_WA, f"runs/{block_name}/{technology}/hip_data"),
        os.path.join(destination_dir, f"runs/{block_name}/{technology}/hip_data"),
        "hip_data",
        log_file
    ):
        error_msg = "✗ Error Please Check: Failed to copy hip_data"
        print(error_msg)
        log_with_timestamp(error_msg, log_file)
        # return False

    # Copy scripts - check for errors
    print("Copying scripts (bscripts)...")
    if not copy_directory(
        os.path.join(ref_WA, f"runs/{block_name}/{technology}/scripts"),
        os.path.join(destination_dir, f"runs/{block_name}/{technology}/scripts"),
        "scripts",
        log_file
    ):
        error_msg = "✗ Error Please Check: Failed to copy scripts"
        print(error_msg)
        log_with_timestamp(error_msg, log_file)
        # return False

    # Copy apr_fc/scripts - check for errors
    print("Copying apr_fc/scripts (fscripts) ...")
    if not copy_directory(
        os.path.join(ref_WA, f"runs/{block_name}/{technology}/{apr_fc_dir_name}/scripts"),
        os.path.join(destination_dir, f"runs/{block_name}/{technology}/apr_fc/scripts"),
        f"{apr_fc_dir_name}/scripts",
        log_file
    ):
        error_msg = "✗ Error Please Check: Failed to copy apr_fc/scripts"
        print(error_msg)
        log_with_timestamp(error_msg, log_file)
        #return False

    # Copy release/latest collaterals
    print("Copying release/latest collaterals...")
    release_latest_path = os.path.join(ref_WA, f"runs/{block_name}/{technology}/release/latest")
    if os.path.isdir(release_latest_path):
        collateral_found = False
        try:
            for item in os.listdir(release_latest_path):
                item_path = os.path.join(release_latest_path, item)
                if os.path.isdir(item_path) and (item.endswith("_collateral") or item == "io_constraints"):
                    collateral_found = True
                    if not copy_directory(
                        item_path,
                        os.path.join(destination_dir, f"runs/{block_name}/{technology}/release/latest/{item}"),
                        item,
                        log_file
                    ):
                        error_msg = f"✗ Error Please Check: Failed to copy {item}"
                        print(error_msg)
                        log_with_timestamp(error_msg, log_file)
                        #return False
            if not collateral_found:
                message = f"⚠ No collateral directories found in {release_latest_path}"
                print(message)
                log_with_timestamp(message, log_file)
        except Exception as e:
            error_msg = f"✗ Error accessing release/latest directory: {e}"
            print(error_msg)
            log_with_timestamp(error_msg, log_file)
            #return False
    else:
        message = f"⚠ Reference release/latest directory not found: {release_latest_path}"
        print(message)
        log_with_timestamp(message, log_file)

    # Copy insert_dft.ndm folder - check for errors
    print(f"Copying {design_name}.ndm folder...")
    ndm_dir = os.path.join(ref_WA, f"runs/{block_name}/{technology}/{apr_fc_dir_name}/outputs/insert_dft/{design_name}.ndm")
    ndm_dest = os.path.join(destination_dir, f"runs/{block_name}/{technology}/apr_fc/outputs/insert_dft/{design_name}.ndm")
    
    if not copy_directory(ndm_dir, ndm_dest, f"{design_name}.ndm", log_file):
        error_msg = f"✗ Error Please Check: Failed to copy {design_name}.ndm directory"
        print(error_msg)
        log_with_timestamp(error_msg, log_file)
        #return False

    # Check and copy runs/common - check for errors
    print("Copying runs/common...")
    common_src = os.path.join(ref_WA, "runs/common")
    common_dest = os.path.join(destination_dir, "runs/common")
    if not copy_directory(common_src, common_dest, "runs/common", log_file):
        # This is not critical, so we'll warn but not fail
        message = "⚠ Warning: Failed to copy runs/common (not critical)"
        print(message)
        log_with_timestamp(message, log_file)

    # Validate that critical files and directories exist after copying
    print("\n=== Validating Setup ===")
    critical_paths = [
        os.path.join(destination_dir, f"runs/{block_name}/{technology}/hip_data"),
        os.path.join(destination_dir, f"runs/{block_name}/{technology}/scripts"),
        os.path.join(destination_dir, f"runs/{block_name}/{technology}/apr_fc/scripts"),
        os.path.join(destination_dir, f"runs/{block_name}/{technology}/apr_fc/outputs/insert_dft/{design_name}.ndm")
    ]
    
    for path in critical_paths:
        if not os.path.exists(path):
            error_msg = f"✗ Validation failed: Critical path missing: {path}"
            print(error_msg)
            log_with_timestamp(error_msg, log_file)
            return False
        else:
            print(f"✓ Validated: {os.path.relpath(path, destination_dir)}")

    # Final summary
    print("\n=== Operation Completed Successfully ===")
    print("All directories have been created and files copied successfully!")
    print(f"- Log file created at: {log_file}")
    log_with_timestamp("=== APR_FC script execution completed successfully ===", log_file)
    
    return True

