"""
Git Lock Manager — Safe concurrent Git operations.

Prevents race conditions when multiple agents commit simultaneously.

Usage:
    lock_manager = GitLockManager()
    lock_manager.safe_commit(worktree, ["prd.md"], "feat: PRD generated")
"""

import os
import subprocess
from pathlib import Path
from typing import List
import logging
import time

logger = logging.getLogger("GitLock")


class GitLockManager:
    """
    Thread-safe Git operations with file locking.
    """
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.lock_file = self.project_root / ".git" / "uz_factory.lock"
        self.timeout = 30  # seconds
    
    def _acquire_lock(self) -> bool:
        """Acquire file lock."""
        start = time.time()
        
        while time.time() - start < self.timeout:
            try:
                # Create lock file exclusively
                fd = os.open(str(self.lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                logger.debug(f"Lock acquired: {self.lock_file}")
                return True
            except FileExistsError:
                # Lock exists, check if stale
                try:
                    mtime = self.lock_file.stat().st_mtime
                    if time.time() - mtime > 60:  # 60s stale threshold
                        logger.warning("Removing stale lock")
                        self.lock_file.unlink()
                        continue
                except:
                    pass
                
                time.sleep(0.5)
        
        logger.error(f"Lock timeout after {self.timeout}s")
        return False
    
    def _release_lock(self):
        """Release file lock."""
        try:
            self.lock_file.unlink()
            logger.debug("Lock released")
        except:
            pass
    
    def safe_commit(
        self,
        worktree: Path,
        files: List[str],
        message: str,
        push: bool = False
    ) -> bool:
        """
        Safely commit files with lock protection.
        
        Args:
            worktree: Path to worktree
            files: List of files to commit
            message: Commit message
            push: Whether to push after commit
            
        Returns:
            True if successful
        """
        if not self._acquire_lock():
            raise TimeoutError("Could not acquire Git lock")
        
        try:
            # Add files
            add_cmd = ["git", "-C", str(worktree), "add"] + files
            result = subprocess.run(add_cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                logger.error(f"git add failed: {result.stderr}")
                return False
            
            # Commit
            commit_cmd = ["git", "-C", str(worktree), "commit", "-m", message]
            result = subprocess.run(commit_cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                if "nothing to commit" in result.stdout or "nothing to commit" in result.stderr:
                    logger.info("Nothing to commit")
                    return True
                logger.error(f"git commit failed: {result.stderr}")
                return False
            
            logger.info(f"Committed: {message[:50]}...")
            
            # Push if requested
            if push:
                push_cmd = ["git", "-C", str(worktree), "push"]
                result = subprocess.run(push_cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode != 0:
                    logger.error(f"git push failed: {result.stderr}")
                    return False
                
                logger.info("Pushed to remote")
            
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("Git operation timed out")
            return False
        except Exception as e:
            logger.error(f"Git error: {e}")
            return False
        finally:
            self._release_lock()
    
    def safe_merge(
        self,
        branch: str,
        into: str = "main",
        delete_after: bool = True
    ) -> bool:
        """
        Safely merge a branch with lock protection.
        
        Args:
            branch: Branch to merge
            into: Target branch (default: main)
            delete_after: Delete source branch after merge
            
        Returns:
            True if successful
        """
        if not self._acquire_lock():
            raise TimeoutError("Could not acquire Git lock")
        
        try:
            # Checkout target
            subprocess.run(
                ["git", "checkout", into],
                capture_output=True, check=True, timeout=10
            )
            
            # Merge
            result = subprocess.run(
                ["git", "merge", branch, "--no-ff", "-m", f"Merge {branch} into {into}"],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"Merge failed: {result.stderr}")
                return False
            
            logger.info(f"Merged {branch} into {into}")
            
            # Delete branch if requested
            if delete_after:
                subprocess.run(
                    ["git", "branch", "-d", branch],
                    capture_output=True, timeout=10
                )
                logger.info(f"Deleted branch {branch}")
            
            return True
            
        except Exception as e:
            logger.error(f"Merge error: {e}")
            return False
        finally:
            self._release_lock()


# Singleton
_manager = None

def get_git_lock_manager() -> GitLockManager:
    """Get singleton Git lock manager."""
    global _manager
    if _manager is None:
        _manager = GitLockManager()
    return _manager


if __name__ == "__main__":
    # Test
    manager = get_git_lock_manager()
    print(f"Lock file: {manager.lock_file}")
    print(f"Project root: {manager.project_root}")
