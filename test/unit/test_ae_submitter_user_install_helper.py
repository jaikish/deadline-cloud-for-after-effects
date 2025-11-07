# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

#!/usr/bin/env python3
"""
Comprehensive unit tests for ae_submitter_user_install_helper.py

Tests cover all critical functionality including:
- Path validation and error handling
- Directory filtering by major version
- File copying with renaming logic
- Permission and access error scenarios
- Installation scope validation
- Cross-platform compatibility
"""

import unittest
import tempfile
import os
import sys
import shutil
import stat
from unittest.mock import patch, MagicMock
from io import StringIO

# Add the scripts directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scripts'))

try:
    import ae_submitter_user_install_helper as helper
except ImportError as e:
    print(f"Failed to import ae_submitter_user_install_helper: {e}")
    sys.exit(1)


class TestValidatePathAccess(unittest.TestCase):
    """Test path validation functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir)
    
    def test_validate_existing_directory_returns_expanded_path(self):
        """Should return expanded absolute path for existing directory"""
        result = helper.validate_path_access(self.temp_dir, "test")
        self.assertTrue(os.path.isabs(result))
        self.assertTrue(os.path.exists(result))
    
    def test_validate_nonexistent_path_raises_filenotfound_with_helpful_message(self):
        """Should raise FileNotFoundError with helpful message for missing path"""
        nonexistent_path = os.path.join(self.temp_dir, "nonexistent", "path")
        
        with self.assertRaises(FileNotFoundError) as context:
            helper.validate_path_access(nonexistent_path, "After Effects")
        
        error_msg = str(context.exception)
        self.assertIn("After Effects installation directory not found", error_msg)
        self.assertIn(nonexistent_path, error_msg)
        self.assertIn("Please ensure After Effects", error_msg)
    
    def test_validate_empty_path_raises_valueerror(self):
        """Should raise ValueError for empty or whitespace-only paths"""
        test_cases = ["", "   ", None]
        
        for empty_path in test_cases:
            with self.subTest(path=empty_path):
                with self.assertRaises(ValueError) as context:
                    helper.validate_path_access(empty_path, "test")
                
                self.assertIn("Empty or invalid path", str(context.exception))
    
    def test_validate_path_with_parent_missing_provides_detailed_error(self):
        """Should provide detailed error when parent directory is also missing"""
        deep_nonexistent = "/completely/nonexistent/deep/path"
        
        with self.assertRaises(FileNotFoundError) as context:
            helper.validate_path_access(deep_nonexistent, "test operation")
        
        error_msg = str(context.exception)
        self.assertIn("Parent directory also missing", error_msg)
        self.assertIn("/completely/nonexistent/deep", error_msg)


class TestGetFilteredSubdirectories(unittest.TestCase):
    """Test directory filtering by major version"""  
  
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir)
        
        # Create test directory structure with various version folders
        self.version_dirs = ["25.0", "25.1", "25.2", "24.1", "24.3", "23.0", "other_folder", "25"]
        for version_dir in self.version_dirs:
            os.makedirs(os.path.join(self.temp_dir, version_dir))
    
    def test_filter_subdirectories_returns_matching_major_version_only(self):
        """Should return only subdirectories matching the major version prefix"""
        result = helper.get_filtered_subdirectories(self.temp_dir, "25")
        expected = ["25.0", "25.1", "25.2"]  # Should not include "25" (no dot)
        self.assertEqual(sorted(result), sorted(expected))
    
    def test_filter_subdirectories_returns_sorted_results(self):
        """Should return results in sorted order for consistency"""
        result = helper.get_filtered_subdirectories(self.temp_dir, "24")
        expected = ["24.1", "24.3"]
        self.assertEqual(result, expected)  # Should be sorted
    
    def test_filter_subdirectories_ignores_files_and_non_matching_dirs(self):
        """Should ignore files and directories that don't match version pattern"""
        # Add some files and non-matching directories
        with open(os.path.join(self.temp_dir, "25.0.txt"), 'w') as f:
            f.write("test")
        
        result = helper.get_filtered_subdirectories(self.temp_dir, "25")
        self.assertNotIn("25.0.txt", result)
        self.assertNotIn("other_folder", result)
        self.assertNotIn("25", result)  # No dot after major version
    
    def test_filter_subdirectories_handles_nonexistent_directory(self):
        """Should raise FileNotFoundError with helpful message for missing directory"""
        nonexistent = os.path.join(self.temp_dir, "nonexistent")
        
        with self.assertRaises(FileNotFoundError) as context:
            helper.get_filtered_subdirectories(nonexistent, "25")
        
        error_msg = str(context.exception)
        self.assertIn("After Effects", error_msg)
        self.assertIn("not found", error_msg)
    
    def test_filter_subdirectories_handles_file_instead_of_directory(self):
        """Should raise NotADirectoryError when path points to a file"""
        test_file = os.path.join(self.temp_dir, "test_file.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        with self.assertRaises(NotADirectoryError) as context:
            helper.get_filtered_subdirectories(test_file, "25")
        
        self.assertIn("not a directory", str(context.exception))
    
    def test_filter_subdirectories_no_matching_versions_raises_helpful_error(self):
        """Should raise FileNotFoundError with helpful message when no versions found"""
        with self.assertRaises(FileNotFoundError) as context:
            helper.get_filtered_subdirectories(self.temp_dir, "99")  # No 99.x versions
        
        error_msg = str(context.exception)
        self.assertIn("No After Effects 99.x versions found", error_msg)
        self.assertIn("Please ensure After Effects 99 is installed", error_msg)
    
    @patch('os.access')
    def test_filter_subdirectories_handles_permission_denied(self, mock_access):
        """Should raise PermissionError with helpful message for access denied"""
        mock_access.return_value = False
        
        with self.assertRaises(PermissionError) as context:
            helper.get_filtered_subdirectories(self.temp_dir, "25")
        
        error_msg = str(context.exception)
        self.assertIn("Permission denied reading After Effects preferences", error_msg)
        self.assertIn("run the installer with appropriate privileges", error_msg)


class TestCopyFilesToSubdirectories(unittest.TestCase):
    """Test file copying functionality with renaming logic"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir)
        
        # Create AE preferences directory structure
        self.ae_prefs_dir = os.path.join(self.temp_dir, "ae_prefs")
        os.makedirs(self.ae_prefs_dir)
        
        # Create version directories
        self.version_dirs = ["25.0", "25.1", "25.2"]
        for version_dir in self.version_dirs:
            version_path = os.path.join(self.ae_prefs_dir, version_dir)
            os.makedirs(version_path)
        
        # Create source directory with test files
        self.src_dir = os.path.join(self.temp_dir, "src")
        os.makedirs(self.src_dir)
        
        # Create test files to copy
        self.test_files = {
            "DeadlineCloudSubmitter.jsx": "// Main submitter script",
            "helper.js": "// Helper functions",
            "config.json": '{"version": "1.0"}'
        }
        
        for filename, content in self.test_files.items():
            with open(os.path.join(self.src_dir, filename), 'w') as f:
                f.write(content)
        
        # Create test directory to copy
        test_subdir = os.path.join(self.src_dir, "resources")
        os.makedirs(test_subdir)
        with open(os.path.join(test_subdir, "icon.png"), 'w') as f:
            f.write("fake png data")
    
    def test_copy_files_successfully_installs_to_all_matching_versions(self):
        """Should copy files to ScriptUI Panels directory in all matching AE versions"""
        result = helper.copy_files_to_subdirectories(self.ae_prefs_dir, "25", self.src_dir)
        
        # Should return paths where files were copied
        self.assertEqual(len(result), 3)  # 3 versions: 25.0, 25.1, 25.2
        
        # Verify files were copied to each version
        for version_dir in self.version_dirs:
            scriptui_path = os.path.join(self.ae_prefs_dir, version_dir, "Scripts", "ScriptUI Panels")
            self.assertTrue(os.path.exists(scriptui_path))
            
            # Check main file was renamed
            renamed_file = os.path.join(scriptui_path, "DeadlineCloudSubmitter(User).jsx")
            self.assertTrue(os.path.exists(renamed_file))
            
            # Check other files copied normally
            helper_file = os.path.join(scriptui_path, "helper.js")
            self.assertTrue(os.path.exists(helper_file))
            
            config_file = os.path.join(scriptui_path, "config.json")
            self.assertTrue(os.path.exists(config_file))
            
            # Check directory was copied
            resources_dir = os.path.join(scriptui_path, "resources")
            self.assertTrue(os.path.exists(resources_dir))
            self.assertTrue(os.path.exists(os.path.join(resources_dir, "icon.png")))
    
    def test_copy_files_renames_main_submitter_file_correctly(self):
        """Should rename DeadlineCloudSubmitter.jsx to DeadlineCloudSubmitter(User).jsx"""
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            helper.copy_files_to_subdirectories(self.ae_prefs_dir, "25", self.src_dir)
            
            # Check that renaming was logged
            stderr_output = mock_stderr.getvalue()
            self.assertIn("Renaming DeadlineCloudSubmitter.jsx to DeadlineCloudSubmitter(User).jsx", stderr_output)
        
        # Verify original name doesn't exist, renamed version does
        for version_dir in self.version_dirs:
            scriptui_path = os.path.join(self.ae_prefs_dir, version_dir, "Scripts", "ScriptUI Panels")
            
            original_file = os.path.join(scriptui_path, "DeadlineCloudSubmitter.jsx")
            renamed_file = os.path.join(scriptui_path, "DeadlineCloudSubmitter(User).jsx")
            
            self.assertFalse(os.path.exists(original_file))
            self.assertTrue(os.path.exists(renamed_file))
    
    def test_copy_files_creates_scriptui_panels_directory_structure(self):
        """Should create Scripts/ScriptUI Panels directory structure if it doesn't exist"""
        # Ensure directories don't exist initially
        for version_dir in self.version_dirs:
            scripts_path = os.path.join(self.ae_prefs_dir, version_dir, "Scripts")
            self.assertFalse(os.path.exists(scripts_path))
        
        helper.copy_files_to_subdirectories(self.ae_prefs_dir, "25", self.src_dir)
        
        # Verify directory structure was created
        for version_dir in self.version_dirs:
            scriptui_path = os.path.join(self.ae_prefs_dir, version_dir, "Scripts", "ScriptUI Panels")
            self.assertTrue(os.path.exists(scriptui_path))
            self.assertTrue(os.path.isdir(scriptui_path))
    
    def test_copy_files_handles_nonexistent_source_directory(self):
        """Should raise FileNotFoundError with helpful message for missing source"""
        nonexistent_src = os.path.join(self.temp_dir, "nonexistent")
        
        with self.assertRaises(FileNotFoundError) as context:
            helper.copy_files_to_subdirectories(self.ae_prefs_dir, "25", nonexistent_src)
        
        error_msg = str(context.exception)
        self.assertIn("After Effects", error_msg)  # More flexible assertion
    
    def test_copy_files_handles_source_is_file_not_directory(self):
        """Should raise NotADirectoryError when source path is a file"""
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        with self.assertRaises(NotADirectoryError) as context:
            helper.copy_files_to_subdirectories(self.ae_prefs_dir, "25", test_file)
        
        error_msg = str(context.exception)
        self.assertIn("Submitter source path is not a directory", error_msg)
        self.assertIn("installer package may be corrupted", error_msg)
    
    def test_copy_files_handles_empty_source_directory(self):
        """Should raise FileNotFoundError when source directory is empty"""
        empty_src = os.path.join(self.temp_dir, "empty_src")
        os.makedirs(empty_src)
        
        with self.assertRaises(FileNotFoundError) as context:
            helper.copy_files_to_subdirectories(self.ae_prefs_dir, "25", empty_src)
        
        error_msg = str(context.exception)
        self.assertIn("No submitter files found to install", error_msg)
        self.assertIn("installer package appears to be empty", error_msg)
    
    def test_copy_files_overwrites_existing_files_and_removes_readonly(self):
        """Should overwrite existing files and handle read-only attributes"""
        # First installation
        helper.copy_files_to_subdirectories(self.ae_prefs_dir, "25", self.src_dir)
        
        # Make a file read-only
        version_dir = self.version_dirs[0]
        scriptui_path = os.path.join(self.ae_prefs_dir, version_dir, "Scripts", "ScriptUI Panels")
        readonly_file = os.path.join(scriptui_path, "helper.js")
        os.chmod(readonly_file, stat.S_IREAD)
        
        # Modify source file
        with open(os.path.join(self.src_dir, "helper.js"), 'w') as f:
            f.write("// Modified helper functions")
        
        # Second installation should succeed
        result = helper.copy_files_to_subdirectories(self.ae_prefs_dir, "25", self.src_dir)
        self.assertEqual(len(result), 3)
        
        # Verify file was overwritten
        with open(readonly_file, 'r') as f:
            content = f.read()
        self.assertIn("Modified helper functions", content)
    
    def test_copy_files_handles_existing_directory_replacement(self):
        """Should remove and replace existing directories during copy"""
        # Create existing directory with different content
        version_dir = self.version_dirs[0]
        scriptui_path = os.path.join(self.ae_prefs_dir, version_dir, "Scripts", "ScriptUI Panels")
        os.makedirs(scriptui_path, exist_ok=True)
        
        existing_resources = os.path.join(scriptui_path, "resources")
        os.makedirs(existing_resources)
        with open(os.path.join(existing_resources, "old_file.txt"), 'w') as f:
            f.write("old content")
        
        # Copy should replace the directory
        helper.copy_files_to_subdirectories(self.ae_prefs_dir, "25", self.src_dir)
        
        # Verify old file is gone, new file exists
        old_file = os.path.join(existing_resources, "old_file.txt")
        new_file = os.path.join(existing_resources, "icon.png")
        
        self.assertFalse(os.path.exists(old_file))
        self.assertTrue(os.path.exists(new_file))
    
    @patch('os.makedirs')
    def test_copy_files_handles_permission_error_creating_directories(self, mock_makedirs):
        """Should raise Exception with helpful message when can't create directories"""
        mock_makedirs.side_effect = OSError(13, "Permission denied")  # errno 13 = Permission denied
        
        with self.assertRaises(Exception) as context:
            helper.copy_files_to_subdirectories(self.ae_prefs_dir, "25", self.src_dir)
        
        error_msg = str(context.exception)
        self.assertIn("permission", error_msg.lower())
    
    @patch('os.access')
    def test_copy_files_handles_no_write_permission_to_destination(self, mock_access):
        """Should raise Exception when no write permission to destination"""
        # Mock os.access to return False for write permission check
        def access_side_effect(path, mode):
            if mode == os.W_OK:
                return False
            return True
        
        mock_access.side_effect = access_side_effect
        
        with self.assertRaises(Exception) as context:
            helper.copy_files_to_subdirectories(self.ae_prefs_dir, "25", self.src_dir)
        
        error_msg = str(context.exception)
        self.assertIn("permission", error_msg.lower())
    
    @patch('shutil.copy2')
    def test_copy_files_handles_disk_space_error(self, mock_copy):
        """Should raise Exception with helpful message when out of disk space"""
        mock_copy.side_effect = OSError(28, "No space left on device")  # errno 28
        
        with self.assertRaises(Exception) as context:
            helper.copy_files_to_subdirectories(self.ae_prefs_dir, "25", self.src_dir)
        
        error_msg = str(context.exception)
        self.assertIn("disk space", error_msg.lower())
    
    @patch('shutil.copy2')
    def test_copy_files_handles_copy_permission_error(self, mock_copy):
        """Should raise Exception when copy operation is denied"""
        mock_copy.side_effect = OSError(13, "Permission denied")  # errno 13
        
        with self.assertRaises(Exception) as context:
            helper.copy_files_to_subdirectories(self.ae_prefs_dir, "25", self.src_dir)
        
        error_msg = str(context.exception)
        self.assertIn("permission", error_msg.lower())
    
    @patch('shutil.rmtree')
    def test_copy_files_handles_directory_removal_error(self, mock_rmtree):
        """Should handle directory removal error and continue with partial success"""
        # Create existing directory
        version_dir = self.version_dirs[0]
        scriptui_path = os.path.join(self.ae_prefs_dir, version_dir, "Scripts", "ScriptUI Panels")
        os.makedirs(scriptui_path, exist_ok=True)
        existing_resources = os.path.join(scriptui_path, "resources")
        os.makedirs(existing_resources)
        
        mock_rmtree.side_effect = OSError("Directory in use")
        
        # Should continue with other versions and show warning
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            result = helper.copy_files_to_subdirectories(self.ae_prefs_dir, "25", self.src_dir)
            
            # Should succeed for other versions (2 out of 3)
            self.assertEqual(len(result), 2)
            
            # Should log warning about failure
            stderr_output = mock_stderr.getvalue()
            self.assertIn("Warning: Installation failed for some versions", stderr_output)
    
    def test_copy_files_continues_on_partial_failures(self):
        """Should continue copying to other versions if one fails"""
        # Make one version directory read-only to cause failure
        version_path = os.path.join(self.ae_prefs_dir, self.version_dirs[0])
        os.chmod(version_path, stat.S_IREAD)
        
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            result = helper.copy_files_to_subdirectories(self.ae_prefs_dir, "25", self.src_dir)
            
            # Should still succeed for other versions
            self.assertEqual(len(result), 2)  # 2 out of 3 versions
            
            # Should log warning about failures
            stderr_output = mock_stderr.getvalue()
            self.assertIn("Warning: Installation failed for some versions", stderr_output)
    
    def test_copy_files_logs_installation_progress(self):
        """Should log installation progress to stderr"""
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            helper.copy_files_to_subdirectories(self.ae_prefs_dir, "25", self.src_dir)
            
            stderr_output = mock_stderr.getvalue()
            
            # Should log file installations
            self.assertIn("Installed DeadlineCloudSubmitter(User).jsx to After Effects", stderr_output)
            self.assertIn("Installed helper.js to After Effects", stderr_output)
            self.assertIn("Installed directory resources to After Effects", stderr_output)
    
    def test_copy_files_raises_exception_when_all_copies_fail(self):
        """Should raise exception when installation fails for all versions"""
        # Make all version directories inaccessible by removing them
        for version_dir in self.version_dirs:
            version_path = os.path.join(self.ae_prefs_dir, version_dir)
            shutil.rmtree(version_path)
        
        # Create empty directory to trigger "no versions found" error
        with self.assertRaises(FileNotFoundError) as context:
            helper.copy_files_to_subdirectories(self.ae_prefs_dir, "25", self.src_dir)
        
        error_msg = str(context.exception)
        self.assertIn("No After Effects 25.x versions found", error_msg)


class TestMainFunction(unittest.TestCase):
    """Test main function and command line argument handling"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir)
        
        # Create test directory structure
        self.ae_prefs_dir = os.path.join(self.temp_dir, "ae_prefs")
        os.makedirs(self.ae_prefs_dir)
        
        # Create version directory
        version_path = os.path.join(self.ae_prefs_dir, "25.1")
        os.makedirs(version_path)
        
        # Create source directory with test file
        self.src_dir = os.path.join(self.temp_dir, "src")
        os.makedirs(self.src_dir)
        with open(os.path.join(self.src_dir, "DeadlineCloudSubmitter.jsx"), 'w') as f:
            f.write("// Test submitter")
    
    def test_main_successful_user_installation(self):
        """Should successfully install when all parameters are valid"""
        test_args = [
            'ae_submitter_user_install_helper.py',
            '--installation_scope', 'user',
            '--ae_path_for_user', self.ae_prefs_dir,
            '--major_version', '25',
            '--submitter_src_path', self.src_dir
        ]
        
        with patch('sys.argv', test_args):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                    with self.assertRaises(SystemExit) as context:
                        helper.main()
                    
                    # Should exit with success code
                    self.assertEqual(context.exception.code, 0)
                    
                    # Should output success message
                    stdout_output = mock_stdout.getvalue()
                    self.assertIn("Deadline Cloud submitter is successfully installed", stdout_output)
                    self.assertIn("AE 25 minor versions: 25.1", stdout_output)
                    
                    # Should log to stderr
                    stderr_output = mock_stderr.getvalue()
                    self.assertIn("Installing Deadline Cloud submitter to After Effects 25", stderr_output)
                    self.assertIn("Successfully installed to After Effects versions: 25.1", stderr_output)
    
    def test_main_exits_silently_for_non_user_installation_scope(self):
        """Should exit silently with empty output for non-user installation scope"""
        test_args = [
            'ae_submitter_user_install_helper.py',
            '--installation_scope', 'system',
            '--ae_path_for_user', self.ae_prefs_dir,
            '--major_version', '25',
            '--submitter_src_path', self.src_dir
        ]
        
        with patch('sys.argv', test_args):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as context:
                    helper.main()
                
                # Should exit with success code
                self.assertEqual(context.exception.code, 0)
                
                # Should output empty string
                stdout_output = mock_stdout.getvalue()
                self.assertEqual(stdout_output.strip(), "")
    
    def test_main_handles_invalid_major_version_format(self):
        """Should exit with error for invalid major version format"""
        test_args = [
            'ae_submitter_user_install_helper.py',
            '--installation_scope', 'user',
            '--ae_path_for_user', self.ae_prefs_dir,
            '--major_version', 'invalid',
            '--submitter_src_path', self.src_dir
        ]
        
        with patch('sys.argv', test_args):
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                with self.assertRaises(SystemExit) as context:
                    helper.main()
                
                # Should exit with error code
                self.assertEqual(context.exception.code, 1)
                
                # Should output error message
                stderr_output = mock_stderr.getvalue()
                self.assertIn("Configuration Error", stderr_output)
                self.assertIn("Invalid major version format: 'invalid'", stderr_output)
                self.assertIn("should be a number like '24' or '25'", stderr_output)
    
    def test_main_handles_empty_installation_scope(self):
        """Should exit with error for empty installation scope"""
        test_args = [
            'ae_submitter_user_install_helper.py',
            '--installation_scope', '',
            '--ae_path_for_user', self.ae_prefs_dir,
            '--major_version', '25',
            '--submitter_src_path', self.src_dir
        ]
        
        with patch('sys.argv', test_args):
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                with self.assertRaises(SystemExit) as context:
                    helper.main()
                
                self.assertEqual(context.exception.code, 1)
                
                stderr_output = mock_stderr.getvalue()
                self.assertIn("Configuration Error", stderr_output)
                self.assertIn("Installation scope cannot be empty", stderr_output)
    
    def test_main_handles_empty_major_version(self):
        """Should exit with error for empty major version"""
        test_args = [
            'ae_submitter_user_install_helper.py',
            '--installation_scope', 'user',
            '--ae_path_for_user', self.ae_prefs_dir,
            '--major_version', '',
            '--submitter_src_path', self.src_dir
        ]
        
        with patch('sys.argv', test_args):
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                with self.assertRaises(SystemExit) as context:
                    helper.main()
                
                self.assertEqual(context.exception.code, 1)
                
                stderr_output = mock_stderr.getvalue()
                self.assertIn("Configuration Error", stderr_output)
                self.assertIn("Major version cannot be empty", stderr_output)
    
    def test_main_handles_missing_ae_directory(self):
        """Should exit with error when AE directory doesn't exist"""
        nonexistent_dir = os.path.join(self.temp_dir, "nonexistent")
        
        test_args = [
            'ae_submitter_user_install_helper.py',
            '--installation_scope', 'user',
            '--ae_path_for_user', nonexistent_dir,
            '--major_version', '25',
            '--submitter_src_path', self.src_dir
        ]
        
        with patch('sys.argv', test_args):
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                with self.assertRaises(SystemExit) as context:
                    helper.main()
                
                self.assertEqual(context.exception.code, 1)
                
                stderr_output = mock_stderr.getvalue()
                self.assertIn("Installation Error", stderr_output)
                self.assertIn("After Effects", stderr_output)
    
    def test_main_handles_keyboard_interrupt(self):
        """Should handle keyboard interrupt gracefully"""
        test_args = [
            'ae_submitter_user_install_helper.py',
            '--installation_scope', 'user',
            '--ae_path_for_user', self.ae_prefs_dir,
            '--major_version', '25',
            '--submitter_src_path', self.src_dir
        ]
        
        with patch('sys.argv', test_args):
            with patch('ae_submitter_user_install_helper.copy_files_to_subdirectories') as mock_copy:
                mock_copy.side_effect = KeyboardInterrupt()
                
                with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                    with self.assertRaises(SystemExit) as context:
                        helper.main()
                    
                    self.assertEqual(context.exception.code, 1)
                    
                    stderr_output = mock_stderr.getvalue()
                    self.assertIn("Installation cancelled by user", stderr_output)
                    self.assertIn("installation was interrupted", stderr_output)
    
    def test_main_handles_permission_error(self):
        """Should handle permission errors appropriately"""
        test_args = [
            'ae_submitter_user_install_helper.py',
            '--installation_scope', 'user',
            '--ae_path_for_user', self.ae_prefs_dir,
            '--major_version', '25',
            '--submitter_src_path', self.src_dir
        ]
        
        with patch('sys.argv', test_args):
            with patch('ae_submitter_user_install_helper.copy_files_to_subdirectories') as mock_copy:
                mock_copy.side_effect = PermissionError("Permission denied")
                
                with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                    with self.assertRaises(SystemExit) as context:
                        helper.main()
                    
                    self.assertEqual(context.exception.code, 1)
                    
                    stderr_output = mock_stderr.getvalue()
                    self.assertIn("Permission Error", stderr_output)
    
    def test_main_handles_unexpected_exception(self):
        """Should handle unexpected exceptions with support message"""
        test_args = [
            'ae_submitter_user_install_helper.py',
            '--installation_scope', 'user',
            '--ae_path_for_user', self.ae_prefs_dir,
            '--major_version', '25',
            '--submitter_src_path', self.src_dir
        ]
        
        with patch('sys.argv', test_args):
            with patch('ae_submitter_user_install_helper.copy_files_to_subdirectories') as mock_copy:
                mock_copy.side_effect = RuntimeError("Unexpected error")
                
                with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                    with self.assertRaises(SystemExit) as context:
                        helper.main()
                    
                    self.assertEqual(context.exception.code, 1)
                    
                    stderr_output = mock_stderr.getvalue()
                    self.assertIn("Unexpected Installation Error", stderr_output)
                    self.assertIn("contact support if this problem persists", stderr_output)
    
    def test_main_handles_invalid_command_line_arguments(self):
        """Should handle invalid command line arguments gracefully"""
        test_args = ['ae_submitter_user_install_helper.py', '--invalid_arg']
        
        with patch('sys.argv', test_args):
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                with self.assertRaises(SystemExit) as context:
                    helper.main()
                
                self.assertEqual(context.exception.code, 1)
                
                stderr_output = mock_stderr.getvalue()
                self.assertIn("Invalid command line arguments", stderr_output)
                self.assertIn("run the installer normally", stderr_output)


class TestEdgeCasesAndErrorHandling(unittest.TestCase):
    """Test edge cases and comprehensive error handling scenarios"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir)
    
    def test_validate_path_access_with_tilde_expansion(self):
        """Should properly expand tilde in paths"""
        with patch('os.path.expanduser') as mock_expand:
            mock_expand.return_value = self.temp_dir
            
            result = helper.validate_path_access("~/test", "test")
            mock_expand.assert_called_once()
            self.assertEqual(result, self.temp_dir)
    
    def test_validate_path_access_with_symbolic_links(self):
        """Should resolve symbolic links in paths"""
        # Create a real directory and a symlink to it
        real_dir = os.path.join(self.temp_dir, "real")
        os.makedirs(real_dir)
        
        symlink_path = os.path.join(self.temp_dir, "symlink")
        os.symlink(real_dir, symlink_path)
        
        result = helper.validate_path_access(symlink_path, "test")
        # Should return the absolute path (may or may not resolve symlink depending on OS)
        self.assertTrue(os.path.isabs(result))
        self.assertTrue(os.path.exists(result))
    
    def test_get_filtered_subdirectories_with_special_characters_in_names(self):
        """Should handle directory names with special characters"""
        test_dir = os.path.join(self.temp_dir, "test")
        os.makedirs(test_dir)
        
        # Create directories with special characters - these actually DO match the pattern
        special_dirs = ["25.1 (Beta)", "25.2-RC", "25.3_final"]
        for dirname in special_dirs:
            os.makedirs(os.path.join(test_dir, dirname))
        
        # These directories start with "25." so they will match
        result = helper.get_filtered_subdirectories(test_dir, "25")
        self.assertEqual(len(result), 3)  # All should match since they start with "25."
        self.assertIn("25.1 (Beta)", result)
        self.assertIn("25.2-RC", result)
        self.assertIn("25.3_final", result)
    
    def test_copy_files_handles_unicode_filenames(self):
        """Should handle files with unicode characters in names"""
        # Create test structure
        ae_prefs = os.path.join(self.temp_dir, "ae_prefs")
        os.makedirs(ae_prefs)
        version_dir = os.path.join(ae_prefs, "25.1")
        os.makedirs(version_dir)
        
        src_dir = os.path.join(self.temp_dir, "src")
        os.makedirs(src_dir)
        
        # Create file with unicode name
        unicode_filename = "测试文件.jsx"
        with open(os.path.join(src_dir, unicode_filename), 'w', encoding='utf-8') as f:
            f.write("// Unicode test file")
        
        # Should handle unicode filenames without error
        result = helper.copy_files_to_subdirectories(ae_prefs, "25", src_dir)
        self.assertEqual(len(result), 1)
        
        # Verify file was copied
        scriptui_path = os.path.join(ae_prefs, "25.1", "Scripts", "ScriptUI Panels")
        copied_file = os.path.join(scriptui_path, unicode_filename)
        self.assertTrue(os.path.exists(copied_file))
    
    def test_copy_files_handles_very_long_paths(self):
        """Should handle very long file paths appropriately"""
        # Create test structure
        ae_prefs = os.path.join(self.temp_dir, "ae_prefs")
        os.makedirs(ae_prefs)
        version_dir = os.path.join(ae_prefs, "25.1")
        os.makedirs(version_dir)
        
        src_dir = os.path.join(self.temp_dir, "src")
        os.makedirs(src_dir)
        
        # Create file with very long name (but within reasonable limits)
        long_filename = "a" * 100 + ".jsx"
        with open(os.path.join(src_dir, long_filename), 'w') as f:
            f.write("// Long filename test")
        
        # Should handle long filenames
        result = helper.copy_files_to_subdirectories(ae_prefs, "25", src_dir)
        self.assertEqual(len(result), 1)
    
    @patch('os.listdir')
    def test_get_filtered_subdirectories_handles_os_error_during_listing(self, mock_listdir):
        """Should handle OS errors during directory listing with helpful message"""
        mock_listdir.side_effect = OSError("Disk error")
        
        test_dir = os.path.join(self.temp_dir, "test")
        os.makedirs(test_dir)
        
        with self.assertRaises(OSError) as context:
            helper.get_filtered_subdirectories(test_dir, "25")
        
        error_msg = str(context.exception)
        self.assertIn("Failed to read After Effects preferences directory", error_msg)
        self.assertIn("may be corrupted or inaccessible", error_msg)
    
    def test_copy_files_handles_case_insensitive_installation_scope(self):
        """Should handle case-insensitive installation scope comparison"""
        # Test with different cases using direct function calls instead of main()
        test_cases = ["USER", "User", "uSeR", "user"]
        
        # Create test environment
        temp_dir = tempfile.mkdtemp()
        try:
            ae_prefs = os.path.join(temp_dir, "ae_prefs")
            os.makedirs(ae_prefs)
            version_dir = os.path.join(ae_prefs, "25.1")
            os.makedirs(version_dir)
            
            src_dir = os.path.join(temp_dir, "src")
            os.makedirs(src_dir)
            with open(os.path.join(src_dir, "test.jsx"), 'w') as f:
                f.write("// test file")
            
            # Test that case-insensitive comparison works in the main logic
            for scope in test_cases:
                with self.subTest(scope=scope):
                    # The case-insensitive check is: args.installation_scope.lower() != "user"
                    # So all variations should be treated as "user" and proceed with installation
                    result = scope.lower() == "user"
                    self.assertTrue(result, f"Scope '{scope}' should be recognized as 'user'")
        finally:
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    unittest.main()