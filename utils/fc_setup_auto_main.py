import os
import sys
import argparse
# Import the modules
from fc_setup_auto import setup_apr_fc_flow
from fc_setup_auto_server import setup_apr_fc_flow_server

def get_interactive_inputs():
    """Get inputs from user via interactive prompts."""
    print("=== PHOENIX FLOW SETUP ===")
    print("Interactive mode - please provide the following information:")
    print()
    
    # Step 1: Get design type
    design_type = ""
    while design_type not in ("server", "client"):
        design_type = input("Step 1: Please provide the design type (server/client): ").strip().lower()
        if design_type not in ("server", "client"):
            print("Invalid input. Please enter 'server' or 'client'.")

    # Step 2-7: Get user inputs
    destination_dir = input("Step 2: Please provide the destination directory (your ward directory): ").strip()
    ref_WA = input("Step 3: Please provide the reference ward directory to copy files from: ").strip()
    block_name = input("Step 4: Please provide the block name/build name (matches the directory name within 'runs/<block_name>', e.g., par_cbpma, dhm): ").strip()
    technology = input("Step 5: Please provide the technology (e.g., 1278.6, n2p_htall_conf7): ").strip()
    apr_fc_dir_name = input("Step 6: Please provide the APR_FC directory name: ").strip()
    design_name = input("Step 7: Please provide the design name (matches the .ndm file name, e.g., <design_name>.ndm): ").strip()
    
    return design_type, destination_dir, ref_WA, block_name, technology, apr_fc_dir_name, design_name


def validate_args(args):
    """Validate command line arguments."""
    errors = []
    
    if not args.design_type:
        errors.append("design_type is required (server or client)")
    elif args.design_type not in ("server", "client"):
        errors.append("design_type must be 'server' or 'client'")
    if not args.destination_dir:
        errors.append("destination_dir is required")
    if not args.ref_wa:
        errors.append("ref_wa is required")
    if not args.block_name:
        errors.append("block_name is required")
    if not args.technology:
        errors.append("technology is required")
    if not args.apr_fc_dir_name:
        errors.append("apr_fc_dir_name is required")
    if not args.design_name:
        errors.append("design_name is required")
    
    if errors:
        print("Error: Missing or invalid required arguments:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)


def main():
    """
    Main function to gather user inputs, set up environment,
    and call other scripts.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Phoenix Flow Setup')
    parser.add_argument('--interactive', action='store_true',
                       help='Run in interactive mode with command line prompts')
    
    # Non-interactive mode arguments
    parser.add_argument('--design_type', type=str, choices=['server', 'client'],
                       help='Design type: server or client')
    parser.add_argument('--destination_dir', type=str,
                       help='Destination directory (your ward directory)')
    parser.add_argument('--ref_wa', type=str,
                       help='Reference ward directory to copy files from')
    parser.add_argument('--block_name', type=str,
                       help='Block name/build name (e.g., par_cbpma, dhm)')
    parser.add_argument('--technology', type=str,
                       help='Technology (e.g., 1278.6)')
    parser.add_argument('--apr_fc_dir_name', type=str,
                       help='APR_FC directory name')
    parser.add_argument('--design_name', type=str,
                       help='Design name')
    
    args = parser.parse_args()

    # Determine if we're in interactive mode
    if args.interactive:
        # Interactive mode
        design_type, destination_dir, ref_WA, block_name, technology, apr_fc_dir_name, design_name = get_interactive_inputs()
    else:
        # Non-interactive mode - validate all required arguments are provided
        validate_args(args)
        design_type = args.design_type
        destination_dir = args.destination_dir
        ref_WA = args.ref_wa
        block_name = args.block_name
        technology = args.technology
        apr_fc_dir_name = args.apr_fc_dir_name
        design_name = args.design_name


    # Display configuration
    print("\n=== Configuration ===")
    print(f"Design type: {design_type}")
    print(f"Destination directory: {destination_dir}")
    print(f"Reference ward directory: {ref_WA}")
    print(f"Block name/build name: {block_name}")
    print(f"Technology: {technology}")
    print(f"APR_FC directory name: {apr_fc_dir_name}")
    print(f"Design name: {design_name}")
    print()
    
    # In interactive mode, ask for confirmation
    if args.interactive:
        confirm = input("Do you want to proceed with these settings? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            sys.exit(1)
        
    # --- Script Execution ---  
    print("\nExecuting Phoenix flow...")
    
    # Step 1: Execute APR_FC flow (prerequisite)
    print(f"=== Step 1: Running Phoenix setup ({design_type} design) ===")
    try:
        if design_type == "server":
            apr_fc_success = setup_apr_fc_flow_server(
                destination_dir=destination_dir,
                ref_WA=ref_WA,
                block_name=block_name,
                technology=technology,
                apr_fc_dir_name=apr_fc_dir_name,
                design_name=design_name
            )
        else:
            apr_fc_success = setup_apr_fc_flow(
                destination_dir=destination_dir,
                ref_WA=ref_WA,
                block_name=block_name,
                technology=technology,
                apr_fc_dir_name=apr_fc_dir_name,
                design_name=design_name
            )
        if not apr_fc_success:
            print("✗ Phoenix setup failed! Cannot proceed with Phoenix flow.")
            sys.exit(1)
        else:
            print("✓ Phoenix setup completed successfully!")
    except Exception as e:
        print(f"✗ Error executing Phoenix setup: {e}")
        sys.exit(1)
    print("\n=== Main script finished successfully. ===")


if __name__ == "__main__":
    main()