"""
GitHub Storage Manager
Handles automatic commits of data files to GitHub repository
"""

import os
import subprocess
from pathlib import Path
import streamlit as st


class GitHubStorage:
    """Manages data persistence through GitHub commits"""
    
    def __init__(self, repo_path="."):
        self.repo_path = Path(repo_path)
        self.data_dir = self.repo_path / "data"
        
    def is_git_repo(self):
        """Check if current directory is a git repository"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def has_changes(self):
        """Check if there are uncommitted changes in data directory"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain", "data/"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            return bool(result.stdout.strip())
        except Exception:
            return False
    
    def get_git_config(self, key):
        """Get git config value"""
        try:
            result = subprocess.run(
                ["git", "config", key],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception:
            return None
    
    def set_git_config(self, key, value):
        """Set git config value"""
        try:
            subprocess.run(
                ["git", "config", key, value],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
                timeout=5
            )
            return True
        except Exception:
            return False
    
    def is_git_configured(self):
        """Check if git user is configured"""
        email = self.get_git_config("user.email")
        name = self.get_git_config("user.name")
        return bool(email and name)
    
    def commit_data(self, message="Update solve records"):
        """
        Commit data files to git repository
        
        Args:
            message (str): Commit message
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.is_git_repo():
            return False, "Not a git repository"
        
        if not self.has_changes():
            return True, "No changes to commit"
        
        try:
            # Add data files
            subprocess.run(
                ["git", "add", "data/"],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
                timeout=10
            )
            
            # Commit
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
                timeout=10
            )
            
            return True, "Changes committed successfully"
            
        except subprocess.CalledProcessError as e:
            return False, f"Git error: {e.stderr.decode() if e.stderr else str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def push_to_github(self):
        """
        Push commits to GitHub
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.is_git_repo():
            return False, "Not a git repository"
        
        try:
            result = subprocess.run(
                ["git", "push"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return True, "Pushed to GitHub successfully"
            else:
                return False, f"Push failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "Push timeout - check your internet connection"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def commit_and_push(self, message="Update solve records"):
        """
        Commit and push data in one operation
        
        Args:
            message (str): Commit message
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # First commit
        success, msg = self.commit_data(message)
        if not success and "No changes" not in msg:
            return False, msg
        
        if "No changes" in msg:
            return True, "No changes to push"
        
        # Then push
        return self.push_to_github()
    
    def auto_save_enabled(self):
        """Check if auto-save to GitHub is enabled"""
        # Check if we're running on Streamlit Cloud
        # Streamlit Cloud sets STREAMLIT_SHARING_MODE environment variable
        return os.getenv('STREAMLIT_SHARING_MODE') is not None or \
               st.session_state.get('github_auto_save', False)


def show_github_sync_ui():
    """Display GitHub sync controls in the UI"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("💾 Data Backup")
    
    github = GitHubStorage()
    
    if not github.is_git_repo():
        st.sidebar.warning("⚠️ Not a git repository")
        return
    
    # Check if Git is configured
    if not github.is_git_configured():
        st.sidebar.warning("⚠️ Git user not configured")
        
        with st.sidebar.expander("⚙️ Configure Git", expanded=True):
            st.write("Set your Git identity:")
            
            git_name = st.text_input(
                "Your Name",
                value=github.get_git_config("user.name") or "",
                key="git_name_input"
            )
            git_email = st.text_input(
                "Your Email",
                value=github.get_git_config("user.email") or "",
                key="git_email_input"
            )
            
            if st.button("Save Git Config", key="save_git_config"):
                if git_name and git_email:
                    if github.set_git_config("user.name", git_name) and \
                       github.set_git_config("user.email", git_email):
                        st.success("✅ Git configured successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to save Git config")
                else:
                    st.error("❌ Please fill in both name and email")
        return
    
    # Show configured user info
    git_user = github.get_git_config("user.name")
    git_email = github.get_git_config("user.email")
    st.sidebar.caption(f"👤 {git_user} ({git_email})")
    
    # Auto-save toggle
    auto_save = st.sidebar.checkbox(
        "Auto-sync to GitHub",
        value=st.session_state.get('github_auto_save', False),
        help="Automatically commit and push data after each save"
    )
    st.session_state['github_auto_save'] = auto_save
    
    # Manual sync button
    if st.sidebar.button("🔄 Sync Now", help="Commit and push data to GitHub"):
        with st.spinner("Syncing to GitHub..."):
            success, message = github.commit_and_push()
            if success:
                st.sidebar.success(f"✅ {message}")
            else:
                st.sidebar.error(f"❌ {message}")
    
    # Show status
    if github.has_changes():
        st.sidebar.info("📝 Unsaved changes detected")
    else:
        st.sidebar.success("✓ All changes saved")
