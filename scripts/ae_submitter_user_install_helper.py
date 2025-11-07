# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#!/usr/bin/env python3
import os
import sys
import argparse
import shutil
import stat

def validate_path_access(path, operation="access"):
    """
    Validate path exists and is accessible with detailed error messages.
    
    Args:
        path (str): Path to validate
        operation (str): Type of operation (access, read, write)
    """
    if not path or path.strip() == "":
        raise ValueError(f"Empty or invalid path provided for {operation}")
    
    # Expand user path and resolve any symbolic links
    expanded_path = os.path.expanduser(os.path.abspath(path))
    
    if not os.path.exists(expanded_path):
        parent_dir = os.path.dirname(expanded_path)
        if not os.path.exists(parent_dir):
            raise FileNotFoundError(
                f"After Effects installation directory not found.\n\n"
                f"Expected path: {expanded_path}\n"
                f"Parent directory also missing: {parent_dir}\n\n"
                f"Please ensure After Effects {operation} is installed and try again."
            )
        else:
            raise FileNotFoundError(
                f"After Effects version directory not found.\n\n"
                f"Path: {expanded_path}\n\n"
                f"This usually means After Effects is not installed or the version "
                f"directory structure has changed. Please verify your After Effects installation."
            )
    
    return expanded_path



def get_filtered_subdirectories(directory_path, major_version):
    """
    Returns a list of subdirectory names that match the major version prefix.
    
    Args:
        directory_path (str): Path to the directory to scan
        major_version (str): Major version prefix to filter by (e.g., "25")
        
    Returns:
        list: List of subdirectory names that start with major_version (not full paths)
    """
    try:
        # Validate and expand the path
        expanded_path = validate_path_access(directory_path, "After Effects preferences")
        
        if not os.path.isdir(expanded_path):
            raise NotADirectoryError(
                f"After Effects preferences path is not a directory.\n\n"
                f"Path: {expanded_path}\n\n"
                f"This path should point to your After Effects preferences folder. "
                f"Please check your After Effects installation."
            )
        
        # Check read permissions
        if not os.access(expanded_path, os.R_OK):
            raise PermissionError(
                f"Permission denied reading After Effects preferences.\n\n"
                f"Path: {expanded_path}\n\n"
                f"Please ensure you have read permissions to this directory or run the installer with appropriate privileges."
            )
        
        # Scan for version directories
        try:
            items = os.listdir(expanded_path)
        except OSError as e:
            raise OSError(
                f"Failed to read After Effects preferences directory.\n\n"
                f"Path: {expanded_path}\n"
                f"Error: {e}\n\n"
                f"This directory may be corrupted or inaccessible. Please check your After Effects installation."
            )
        
        subdirs = []
        for item in items:
            item_path = os.path.join(expanded_path, item)
            if os.path.isdir(item_path):
                # Filter by major version prefix (e.g., "25.1", "25.2" for major_version="25")
                if item.startswith(f"{major_version}."):
                    subdirs.append(item)
        
        if not subdirs:
            raise FileNotFoundError(
                f"No After Effects {major_version}.x versions found.\n\n"
                f"Searched in: {expanded_path}\n"
                f"Looking for directories starting with: {major_version}.\n\n"
                f"Please ensure After Effects {major_version} is installed and has been run at least once "
                f"to create the preferences directories."
            )
        
        return sorted(subdirs)  # Sort for consistent output
        
    except (ValueError, FileNotFoundError, NotADirectoryError, PermissionError, OSError):
        raise  # Re-raise our custom exceptions
    except Exception as e:
        raise Exception(
            f"Unexpected error scanning After Effects directories.\n\n"
            f"Path: {directory_path}\n"
            f"Error: {e}\n\n"
            f"Please contact support if this problem persists."
        )

def copy_files_to_subdirectories(ae_path_for_user, major_version, submitter_src_path):
    """
    Copy all files from submitter_src_path to ScriptUI Panels directory in each 
    filtered After Effects version subdirectory.
    
    Args:
        ae_path_for_user (str): Path to the After Effects directory
        major_version (str): Major version prefix to filter by
        submitter_src_path (str): Source directory containing files to copy
        
    Returns:
        list: List of destination paths where files were copied
    """
    try:
        # Validate source directory
        expanded_src_path = validate_path_access(submitter_src_path, "submitter files")
        
        if not os.path.isdir(expanded_src_path):
            raise NotADirectoryError(
                f"Submitter source path is not a directory.\n\n"
                f"Path: {expanded_src_path}\n\n"
                f"The installer package may be corrupted. Please re-download and try again."
            )
        
        # Check source directory has files
        try:
            src_items = os.listdir(expanded_src_path)
        except OSError as e:
            raise OSError(
                f"Cannot read submitter files directory.\n\n"
                f"Path: {expanded_src_path}\n"
                f"Error: {e}\n\n"
                f"The installer package may be corrupted or you may not have sufficient permissions."
            )
        
        if not src_items:
            raise FileNotFoundError(
                f"No submitter files found to install.\n\n"
                f"Source directory: {expanded_src_path}\n\n"
                f"The installer package appears to be empty or corrupted. Please re-download and try again."
            )
        
        # Get filtered subdirectories (this will validate ae_path_for_user)
        subdirs = get_filtered_subdirectories(ae_path_for_user, major_version)
        
        copied_to = []
        failed_copies = []
        
        for subdir in subdirs:
            try:
                # Construct the ScriptUI Panels path for this version
                ae_version_path = os.path.join(ae_path_for_user, subdir)
                scripts_path = os.path.join(ae_version_path, "Scripts")
                scriptui_panels_path = os.path.join(scripts_path, "ScriptUI Panels")
                
                # Create the directory structure if it doesn't exist
                try:
                    os.makedirs(scriptui_panels_path, exist_ok=True)
                except OSError as e:
                    if e.errno == 13:  # Permission denied
                        raise PermissionError(
                            f"Permission denied creating ScriptUI Panels directory.\n\n"
                            f"Path: {scriptui_panels_path}\n\n"
                            f"Please ensure you have write permissions to the After Effects preferences directory "
                            f"or run the installer with administrator privileges."
                        )
                    else:
                        raise OSError(
                            f"Failed to create ScriptUI Panels directory.\n\n"
                            f"Path: {scriptui_panels_path}\n"
                            f"Error: {e}\n\n"
                            f"Please check your file system permissions and available disk space."
                        )
                
                # Check write permissions
                if not os.access(scriptui_panels_path, os.W_OK):
                    raise PermissionError(
                        f"No write permission to ScriptUI Panels directory.\n\n"
                        f"Path: {scriptui_panels_path}\n\n"
                        f"Please ensure you have write permissions or run the installer with administrator privileges."
                    )
                
                # Copy all files from source to destination
                files_copied = 0
                for item in src_items:
                    src_item_path = os.path.join(expanded_src_path, item)
                    
                    # Rename DeadlineCloudSubmitter.jsx to DeadlineCloudSubmitter(User).jsx
                    if item == "DeadlineCloudSubmitter.jsx":
                        dst_item_name = "DeadlineCloudSubmitter(User).jsx"
                        print(f"Renaming {item} to {dst_item_name} for user installation", file=sys.stderr)
                    else:
                        dst_item_name = item
                    
                    dst_item_path = os.path.join(scriptui_panels_path, dst_item_name)
                    
                    try:
                        if os.path.isfile(src_item_path):
                            # Check if destination file is read-only and remove that attribute
                            if os.path.exists(dst_item_path):
                                try:
                                    os.chmod(dst_item_path, stat.S_IWRITE | stat.S_IREAD)
                                except OSError:
                                    pass  # Ignore chmod errors
                            
                            shutil.copy2(src_item_path, dst_item_path)
                            files_copied += 1
                            print(f"Installed {dst_item_name} to After Effects {subdir}", file=sys.stderr)
                            
                        elif os.path.isdir(src_item_path):
                            # Remove existing directory if it exists
                            if os.path.exists(dst_item_path):
                                try:
                                    shutil.rmtree(dst_item_path)
                                except OSError as e:
                                    raise OSError(
                                        f"Failed to remove existing directory before copying.\n\n"
                                        f"Path: {dst_item_path}\n"
                                        f"Error: {e}\n\n"
                                        f"Please close After Effects and try again, or manually remove this directory."
                                    )
                            
                            shutil.copytree(src_item_path, dst_item_path)
                            files_copied += 1
                            print(f"Installed directory {item} to After Effects {subdir}", file=sys.stderr)
                    
                    except shutil.Error as e:
                        raise shutil.Error(
                            f"Failed to copy {item} to After Effects {subdir}.\n\n"
                            f"Source: {src_item_path}\n"
                            f"Destination: {dst_item_path}\n"
                            f"Error: {e}\n\n"
                            f"Please ensure After Effects is not running and try again."
                        )
                    except OSError as e:
                        if e.errno == 28:  # No space left on device
                            raise OSError(
                                f"Insufficient disk space to copy files.\n\n"
                                f"Failed while copying: {item}\n"
                                f"Destination: {scriptui_panels_path}\n\n"
                                f"Please free up disk space and try again."
                            )
                        elif e.errno == 13:  # Permission denied
                            raise PermissionError(
                                f"Permission denied copying {item}.\n\n"
                                f"Destination: {dst_item_path}\n\n"
                                f"Please ensure After Effects is not running and you have write permissions."
                            )
                        else:
                            raise OSError(
                                f"Failed to copy {item}.\n\n"
                                f"Source: {src_item_path}\n"
                                f"Destination: {dst_item_path}\n"
                                f"Error: {e}\n\n"
                                f"Please check file permissions and try again."
                            )
                
                if files_copied == 0:
                    print(f"Warning: No files were copied to After Effects {subdir}", file=sys.stderr)
                else:
                    copied_to.append(scriptui_panels_path)
                    
            except Exception as e:
                failed_copies.append(f"After Effects {subdir}: {str(e)}")
                continue
        
        # Report any failures
        if failed_copies and not copied_to:
            # All copies failed
            raise Exception(
                f"Failed to install to any After Effects versions.\n\n"
                f"Errors encountered:\n" + "\n\n".join(failed_copies)
            )
        elif failed_copies:
            # Some copies failed, but some succeeded
            print(f"Warning: Installation failed for some versions:\n" + "\n".join(failed_copies), file=sys.stderr)
        
        if not copied_to:
            raise Exception(
                f"No files were successfully installed.\n\n"
                f"Please check your After Effects installation and try again."
            )
        
        return copied_to
        
    except (ValueError, FileNotFoundError, NotADirectoryError, PermissionError, OSError, shutil.Error):
        raise  # Re-raise our custom exceptions
    except Exception as e:
        raise Exception(
            f"Unexpected error during file installation.\n\n"
            f"Error: {e}\n\n"
            f"Please contact support if this problem persists."
        )

def main():
    parser = argparse.ArgumentParser(description="Install Deadline Cloud submitter to After Effects")
    parser.add_argument("--installation_scope", required=True, 
                       help="Installation scope (must be 'user' to perform operations)")
    parser.add_argument("--ae_path_for_user", required=True,
                       help="Path to the After Effects preferences directory")
    parser.add_argument("--major_version", required=True,
                       help="After Effects major version to install to (e.g., '24', '25')")
    parser.add_argument("--submitter_src_path", required=True,
                       help="Directory containing Deadline Cloud submitter files")
    
    try:
        args = parser.parse_args()
    except SystemExit:
        print(
            "Invalid command line arguments.\n\n"
            "This installer requires specific parameters to function correctly. "
            "Please run the installer normally rather than executing this script directly.",
            file=sys.stderr
        )
        sys.exit(1)
    
    try:
        # Validate arguments
        if not args.installation_scope or args.installation_scope.strip() == "":
            raise ValueError("Installation scope cannot be empty")
        
        if not args.major_version or args.major_version.strip() == "":
            raise ValueError("Major version cannot be empty")
        
        # Validate major version format
        if not args.major_version.isdigit():
            raise ValueError(
                f"Invalid major version format: '{args.major_version}'\n\n"
                f"Major version should be a number like '24' or '25'."
            )
        
        # Return empty string if installation_scope is not "user"
        if args.installation_scope.lower() != "user":
            print("")
            sys.exit(0)
        
        print(f"Installing Deadline Cloud submitter to After Effects {args.major_version}...", file=sys.stderr)
        
        # Perform the installation
        copied_to = copy_files_to_subdirectories(
            args.ae_path_for_user, 
            args.major_version, 
            args.submitter_src_path
        )
        
        # Get the list of versions that were successfully installed to
        subdirs = get_filtered_subdirectories(args.ae_path_for_user, args.major_version)
        
        # Create success message for InstallBuilder alert
        version_list = ", ".join(subdirs)
        success_message = f"Deadline Cloud submitter is successfully installed to AE {args.major_version} minor versions: {version_list}"
        
        # Log to stderr for installer logs
        print(f"Successfully installed to After Effects versions: {version_list}", file=sys.stderr)
        print(f"Installation completed to {len(copied_to)} location(s).", file=sys.stderr)
        
        # Return the success message for InstallBuilder to display as alert
        print(success_message)
        sys.exit(0)
        
    except KeyboardInterrupt:
        print(
            "Installation cancelled by user.\n\n"
            "The installation was interrupted. You may need to run the installer again.",
            file=sys.stderr
        )
        sys.exit(1)
    except ValueError as e:
        print(
            f"Configuration Error\n\n{e}\n\n"
            f"Please check the installer configuration and try again.",
            file=sys.stderr
        )
        sys.exit(1)
    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"Installation Error\n\n{e}", file=sys.stderr)
        sys.exit(1)
    except PermissionError as e:
        print(f"Permission Error\n\n{e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"System Error\n\n{e}", file=sys.stderr)
        sys.exit(1)
    except shutil.Error as e:
        print(f"File Copy Error\n\n{e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(
            f"Unexpected Installation Error\n\n{e}\n\n"
            f"Please contact support if this problem persists.\n"
            f"Include this error message and your system information.",
            file=sys.stderr
        )
        sys.exit(1)

if __name__ == "__main__":
    main()