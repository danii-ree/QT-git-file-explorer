import sys
import os
import subprocess
import shutil
import zipfile
from PySide6.QtWidgets import (
    QMainWindow,
    QListView,
    QVBoxLayout,
    QWidget,
    QToolBar,
    QFileSystemModel,
    QStatusBar,
    QLineEdit,
    QApplication,
    QFileIconProvider,
    QMenu,
    QAbstractItemView,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QMessageBox,
    QFileDialog,
    QSplitter,
    QStackedWidget,
    QToolButton,
    QGraphicsDropShadowEffect,
    QDialog,
    QTextEdit,
    QPushButton,
    QCheckBox,
    QComboBox,
    QInputDialog,
)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QDir, QModelIndex, QSize, Qt

# this is a comment

class GitManager:
    """Handles all Git-related operations"""
    
    @staticmethod
    def is_git_repo(path):
        """Check if a directory is a Git repository"""
        git_dir = os.path.join(path, '.git')
        return os.path.isdir(git_dir)
    
    @staticmethod
    def is_github_authenticated():
        """Check if user is authenticated with GitHub"""
        try:
            result = subprocess.run(
                ['git', 'config', '--global', 'user.name'],
                capture_output=True,
                text=True,
                timeout=2
            )
            username = result.stdout.strip()
            
            result = subprocess.run(
                ['git', 'config', '--global', 'user.email'],
                capture_output=True,
                text=True,
                timeout=2
            )
            email = result.stdout.strip()
            
            if username and email:
                return True, username, email
            return False, None, None
        except Exception:
            return False, None, None
    
    @staticmethod
    def get_repo_status(path):
        """Get the status of a Git repository"""
        try:
            result = subprocess.run(
                ['git', '-C', path, 'status', '--porcelain'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                modified = sum(1 for line in lines if line.startswith(' M') or line.startswith('M '))
                added = sum(1 for line in lines if line.startswith('A ') or line.startswith('??'))
                deleted = sum(1 for line in lines if line.startswith(' D') or line.startswith('D '))
                return {
                    'modified': modified,
                    'added': added,
                    'deleted': deleted,
                    'clean': len(lines) == 1 and lines[0] == ''
                }
        except Exception:
            pass
        return None
    
    @staticmethod
    def get_current_branch(path):
        """Get the current branch name"""
        try:
            result = subprocess.run(
                ['git', '-C', path, 'branch', '--show-current'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    @staticmethod
    def get_remote_url(path):
        """Get the remote repository URL"""
        try:
            result = subprocess.run(
                ['git', '-C', path, 'remote', 'get-url', 'origin'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    @staticmethod
    def has_upstream_branch(path):
        """Check if the current branch has an upstream tracking branch"""
        try:
            result = subprocess.run(
                ['git', '-C', path, 'rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}'],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0 and result.stdout.strip() != ''
        except Exception:
            return False
    
    @staticmethod
    def add_remote(path, name, url):
        """Add a remote repository"""
        try:
            result = subprocess.run(
                ['git', '-C', path, 'remote', 'add', name, url],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, "Remote added successfully"
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def set_upstream(path, remote_name, branch_name):
        """Set upstream tracking branch"""
        try:
            result = subprocess.run(
                ['git', '-C', path, 'branch', '--set-upstream-to', f'{remote_name}/{branch_name}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, "Upstream set successfully"
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def push_set_upstream(path, remote_name, branch_name):
        """Push and set upstream tracking branch in one command"""
        try:
            result = subprocess.run(
                ['git', '-C', path, 'push', '--set-upstream', remote_name, branch_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return True, "Push successful and upstream set"
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def commit_changes(path, message, add_all=True):
        """Commit changes to the repository"""
        try:
            if add_all:
                result = subprocess.run(
                    ['git', '-C', path, 'add', '-A'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    return False, f"Failed to stage files: {result.stderr}"
            
            result = subprocess.run(
                ['git', '-C', path, 'commit', '-m', message],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, "Commit successful"
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def push_changes(path):
        """Push changes to remote repository"""
        try:
            result = subprocess.run(
                ['git', '-C', path, 'push'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return True, "Push successful"
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def pull_changes(path):
        """Pull changes from remote repository"""
        try:
            result = subprocess.run(
                ['git', '-C', path, 'pull'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return True, "Pull successful"
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def get_all_branches(path):
        """Get list of all branches (local and remote)"""
        try:
            result = subprocess.run(
                ['git', '-C', path, 'branch', '-a'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                branches = []
                for line in result.stdout.strip().split('\n'):
                    branch = line.strip().lstrip('* ').strip()
                    if branch and not branch.startswith('remotes/origin/HEAD'):
                        if branch.startswith('remotes/origin/'):
                            branch = branch.replace('remotes/origin/', '')
                        if branch not in branches:
                            branches.append(branch)
                return branches
        except Exception:
            pass
        return []
    
    @staticmethod
    def checkout_branch(path, branch_name):
        """Checkout a different branch"""
        try:
            result = subprocess.run(
                ['git', '-C', path, 'checkout', branch_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, f"Switched to branch '{branch_name}'"
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def create_branch(path, branch_name):
        """Create a new branch"""
        try:
            result = subprocess.run(
                ['git', '-C', path, 'checkout', '-b', branch_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, f"Created and switched to branch '{branch_name}'"
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def rename_branch(path, old_name, new_name):
        """Rename a branch"""
        try:
            current_branch = GitManager.get_current_branch(path)
            if current_branch != old_name:
                result = subprocess.run(
                    ['git', '-C', path, 'checkout', old_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    return False, f"Failed to checkout branch: {result.stderr}"
            
            result = subprocess.run(
                ['git', '-C', path, 'branch', '-m', new_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, f"Branch renamed from '{old_name}' to '{new_name}'"
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)


class GitRemoteDialog(QDialog):
    """Dialog for adding a remote to a Git repository"""
    
    def __init__(self, repo_path, parent=None):
        super().__init__(parent)
        self.repo_path = repo_path
        self.setWindowTitle("Add Git Remote")
        self.setMinimumSize(500, 250)
        
        layout = QVBoxLayout(self)
        
        info_label = QLabel(f"<b>Repository:</b> {os.path.basename(repo_path)}<br>"
                           "No remote repository is configured for this branch.")
        layout.addWidget(info_label)
        
        layout.addWidget(QLabel("Remote Name:"))
        self.remote_name_edit = QLineEdit()
        self.remote_name_edit.setText("origin")
        self.remote_name_edit.setPlaceholderText("origin")
        layout.addWidget(self.remote_name_edit)
        
        layout.addWidget(QLabel("Remote URL:"))
        self.remote_url_edit = QLineEdit()
        self.remote_url_edit.setPlaceholderText("https://github.com/username/repository.git")
        layout.addWidget(self.remote_url_edit)
        
        example_label = QLabel("<i>Example: https://github.com/username/repo.git<br>"
                              "or git@github.com:username/repo.git</i>")
        example_label.setStyleSheet("color: #8be9fd; font-size: 11px;")
        layout.addWidget(example_label)
        
        self.set_upstream_checkbox = QCheckBox("Set as upstream tracking branch")
        self.set_upstream_checkbox.setChecked(True)
        layout.addWidget(self.set_upstream_checkbox)
        
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Remote")
        self.add_button.clicked.connect(self.add_remote)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setStyleSheet('''
            QDialog {
                background: #23262b;
                color: #e6e6e6;
            }
            QLabel {
                color: #e6e6e6;
            }
            QLineEdit {
                background: #2c3138;
                color: #e6e6e6;
                border: 1px solid #3a3d45;
                border-radius: 6px;
                padding: 8px;
            }
            QCheckBox {
                color: #e6e6e6;
                spacing: 8px;
            }
            QPushButton {
                background: #3a74b4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: #4a84c4;
            }
            QPushButton#cancel_button {
                background: #5a5d65;
            }
            QPushButton#cancel_button:hover {
                background: #6a6d75;
            }
        ''')
        self.cancel_button.setObjectName("cancel_button")
    
    def add_remote(self):
        remote_name = self.remote_name_edit.text().strip()
        remote_url = self.remote_url_edit.text().strip()
        
        if not remote_name:
            QMessageBox.warning(self, "Missing Name", "Please enter a remote name.")
            return
        
        if not remote_url:
            QMessageBox.warning(self, "Missing URL", "Please enter a remote URL.")
            return
        
        success, result = GitManager.add_remote(self.repo_path, remote_name, remote_url)
        
        if not success:
            QMessageBox.critical(self, "Failed", f"Failed to add remote:\n{result}")
            return
        
        if self.set_upstream_checkbox.isChecked():
            branch = GitManager.get_current_branch(self.repo_path)
            if branch:
                success, result = GitManager.set_upstream(self.repo_path, remote_name, branch)
                if not success:
                    QMessageBox.warning(self, "Upstream Failed", 
                                       f"Remote added but failed to set upstream:\n{result}")
                    self.accept()
                    return
        
        QMessageBox.information(self, "Success", f"Remote '{remote_name}' added successfully!")
        self.accept()


class GitCommitDialog(QDialog):
    """Dialog for committing changes to Git"""
    
    def __init__(self, repo_path, parent=None):
        super().__init__(parent)
        self.repo_path = repo_path
        self.setWindowTitle("Git Commit")
        self.setMinimumSize(500, 450)
        
        layout = QVBoxLayout(self)
        
        status = GitManager.get_repo_status(repo_path)
        branch = GitManager.get_current_branch(repo_path)
        remote = GitManager.get_remote_url(repo_path)
        has_upstream = GitManager.has_upstream_branch(repo_path)
        
        info_text = f"<b>Repository:</b> {os.path.basename(repo_path)}<br>"
        info_text += f"<b>Branch:</b> {branch or 'Unknown'}<br>"
        # test comment
        if remote:
            info_text += f"<b>Remote:</b> {remote}<br>"
        else:
            info_text += "<b>Remote:</b> <span style='color: #ff5555;'>Not configured</span><br>"
        
        info_text += f"<b>Modified:</b> {status['modified'] if status else 0} | "
        info_text += f"<b>Added:</b> {status['added'] if status else 0} | "
        info_text += f"<b>Deleted:</b> {status['deleted'] if status else 0}"
        
        info_label = QLabel(info_text)
        layout.addWidget(info_label)
        
        if not remote or not has_upstream:
            warning_widget = QWidget()
            warning_layout = QHBoxLayout(warning_widget)
            warning_layout.setContentsMargins(8, 8, 8, 8)
            warning_widget.setStyleSheet("background: #44475a; border-radius: 6px;")
            
            warning_label = QLabel()
            if not remote:
                warning_label.setText("⚠ No remote repository configured. You won't be able to push.")
            else:
                warning_label.setText("⚠ No upstream branch set. You may need to set upstream when pushing.")
            warning_label.setStyleSheet("color: #ffb86c;")
            warning_layout.addWidget(warning_label)
            
            if not remote:
                add_remote_btn = QPushButton("Add Remote")
                add_remote_btn.clicked.connect(self.show_add_remote_dialog)
                add_remote_btn.setStyleSheet("""
                    QPushButton {
                        background: #ffb86c;
                        color: #282a36;
                        border: none;
                        padding: 4px 12px;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background: #ffc98c;
                    }
                """)
                warning_layout.addWidget(add_remote_btn)
            
            warning_layout.addStretch()
            layout.addWidget(warning_widget)
        
        layout.addWidget(QLabel("Commit Message:"))
        self.message_edit = QTextEdit()
        self.message_edit.setPlaceholderText("Enter your commit message here...")
        layout.addWidget(self.message_edit)
        
        self.add_all_checkbox = QCheckBox("Stage all changes (git add -A)")
        self.add_all_checkbox.setChecked(True)
        layout.addWidget(self.add_all_checkbox)
        
        self.push_checkbox = QCheckBox("Push to remote after commit")
        self.push_checkbox.setEnabled(bool(remote))
        if not remote:
            self.push_checkbox.setToolTip("Add a remote repository first")
        layout.addWidget(self.push_checkbox)
        
        button_layout = QHBoxLayout()
        self.commit_button = QPushButton("Commit")
        self.commit_button.clicked.connect(self.commit)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.commit_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setStyleSheet('''
            QDialog {
                background: #23262b;
                color: #e6e6e6;
            }
            QLabel {
                color: #e6e6e6;
            }
            QTextEdit, QLineEdit {
                background: #2c3138;
                color: #e6e6e6;
                border: 1px solid #3a3d45;
                border-radius: 6px;
                padding: 8px;
            }
            QCheckBox {
                color: #e6e6e6;
                spacing: 8px;
            }
            QPushButton {
                background: #3a74b4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: #4a84c4;
            }
            QPushButton#cancel_button {
                background: #5a5d65;
            }
            QPushButton#cancel_button:hover {
                background: #6a6d75;
            }
        ''')
        self.cancel_button.setObjectName("cancel_button")
    
    def show_add_remote_dialog(self):
        """Show dialog to add a remote repository"""
        dialog = GitRemoteDialog(self.repo_path, self)
        if dialog.exec() == QDialog.Accepted:
            remote = GitManager.get_remote_url(self.repo_path)
            if remote:
                self.push_checkbox.setEnabled(True)
                self.push_checkbox.setToolTip("")
                if self.parent():
                    self.parent().update_git_status_display()
    
    def commit(self):
        message = self.message_edit.toPlainText().strip()
        if not message:
            QMessageBox.warning(self, "Empty Message", "Please enter a commit message.")
            return
        
        success, result = GitManager.commit_changes(
            self.repo_path,
            message,
            self.add_all_checkbox.isChecked()
        )
        
        if not success:
            QMessageBox.critical(self, "Commit Failed", f"Failed to commit:\n{result}")
            return
        
        if self.push_checkbox.isChecked():
            if not GitManager.has_upstream_branch(self.repo_path):
                branch = GitManager.get_current_branch(self.repo_path)
                reply = QMessageBox.question(
                    self, 
                    "Set Upstream Branch",
                    f"The branch '{branch}' has no upstream branch.\n\n"
                    f"Do you want to set 'origin/{branch}' as the upstream branch?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    success, result = GitManager.push_set_upstream(self.repo_path, "origin", branch)
                    if not success:
                        QMessageBox.critical(self, "Push Failed", f"Failed to push and set upstream:\n{result}")
                        return
                    QMessageBox.information(self, "Success", "Changes committed and pushed successfully!\nUpstream branch has been set.")
                else:
                    success, result = GitManager.push_changes(self.repo_path)
                    if not success:
                        QMessageBox.warning(self, "Push Failed", f"Commit succeeded but push failed:\n{result}")
                    else:
                        QMessageBox.information(self, "Success", "Changes committed and pushed successfully!")
            else:
                success, result = GitManager.push_changes(self.repo_path)
                if not success:
                    QMessageBox.warning(self, "Push Failed", f"Commit succeeded but push failed:\n{result}")
                else:
                    QMessageBox.information(self, "Success", "Changes committed and pushed successfully!")
        else:
            QMessageBox.information(self, "Success", "Changes committed successfully!")
        
        self.accept()


class FileExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_path = QDir.homePath()
        self.setWindowTitle("Qt6 File Explorer with Git")
        self.setGeometry(100, 100, 1000, 700)
        self.setWindowIcon(QIcon.fromTheme("system-file-manager"))
        
        self.is_authenticated, self.git_username, self.git_email = GitManager.is_github_authenticated()

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(140)
        self.sidebar.setIconSize(QSize(20, 20))
        self.sidebar.setStyleSheet('''
            QListWidget {
                background: #35373b;
                color: #f8f8f2;
                border: none;
                font-size: 12px;
                padding: 0px 0 0 0;
            }
            QListWidget::item {
                padding: 2px 0 2px 6px;
                border-radius: 3px;
                min-height: 22px;
            }
            QListWidget::item:selected {
                background: #6272a4;
                color: #f8f8f2;
            }
        ''')
        self.populate_sidebar()
        self.sidebar.currentItemChanged.connect(self.sidebar_navigate)

        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(self.toolbar)

        self.action_back = QAction(QIcon.fromTheme("go-previous"), "Back", self)
        self.action_home = QAction(QIcon.fromTheme("go-home"), "Home", self)
        self.toolbar.addAction(self.action_back)
        self.toolbar.addAction(self.action_home)
        self.action_back.triggered.connect(self.go_back)
        self.action_home.triggered.connect(self.go_home)
        
        self.toolbar.addSeparator()
        self.action_git_commit = QAction(QIcon.fromTheme("vcs-commit"), "Git Commit", self)
        self.action_git_commit.triggered.connect(self.show_git_commit_dialog)
        self.action_git_commit.setEnabled(False)
        self.toolbar.addAction(self.action_git_commit)
        
        self.action_git_pull = QAction(QIcon.fromTheme("vcs-update"), "Git Pull", self)
        self.action_git_pull.triggered.connect(self.git_pull)
        self.action_git_pull.setEnabled(False)
        self.toolbar.addAction(self.action_git_pull)
        
        self.action_git_push = QAction(QIcon.fromTheme("vcs-push"), "Git Push", self)
        self.action_git_push.triggered.connect(self.git_push)
        self.action_git_push.setEnabled(False)
        self.toolbar.addAction(self.action_git_push)

        self.path_bar = QLineEdit()
        self.path_bar.setText(self.current_path)
        self.path_bar.setPlaceholderText("/path/to/folder ...")
        self.path_bar.setReadOnly(False)
        self.path_bar.returnPressed.connect(self.on_path_bar_entered)

        self.breadcrumbs = QWidget()
        self.breadcrumbs_layout = QHBoxLayout(self.breadcrumbs)
        self.breadcrumbs_layout.setContentsMargins(0, 0, 0, 0)
        self.breadcrumbs_layout.setSpacing(0)

        self.path_stack = QStackedWidget()
        self.path_stack.addWidget(self.breadcrumbs)
        self.path_stack.addWidget(self.path_bar)
        self.path_stack.setCurrentWidget(self.breadcrumbs)

        self.edit_path_action = QAction(QIcon.fromTheme("document-edit"), "Edit Path", self)
        self.edit_path_action.triggered.connect(self.show_path_editor)
        self.toolbar.addAction(self.edit_path_action)
        self.toolbar.addWidget(self.path_stack)

        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.homePath())
        self.icon_provider = QFileIconProvider()
        self.model.setIconProvider(self.icon_provider)

        self.view = QListView()
        self.view.setModel(self.model)
        self.view.setRootIndex(self.model.index(QDir.homePath()))
        self.view.setViewMode(QListView.IconMode)
        self.view.setIconSize(QSize(64, 64))
        self.view.setGridSize(QSize(140, 130))
        self.view.setSpacing(32)
        self.view.setResizeMode(QListView.Adjust)
        self.view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.view.setDragEnabled(True)
        self.view.setAcceptDrops(True)
        self.view.setDropIndicatorShown(True)
        self.view.setMouseTracking(True)
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.open_context_menu)
        self.view.doubleClicked.connect(self.on_double_click)

        splitter = QSplitter(Qt.Horizontal)

        sidebar_container = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        sidebar_layout.addWidget(self.sidebar)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 0)
        shadow.setColor(Qt.black)
        sidebar_container.setGraphicsEffect(shadow)

        file_container = QWidget()
        file_layout = QVBoxLayout(file_container)
        file_layout.setContentsMargins(8, 8, 8, 8)
        file_layout.addWidget(self.view)

        splitter.addWidget(sidebar_container)
        splitter.addWidget(file_container)
        splitter.setHandleWidth(1)
        splitter.setSizes([160, 840])

        self.setCentralWidget(splitter)

        self.status = QStatusBar()
        self.git_status_label = QLabel()
        self.status.addPermanentWidget(self.git_status_label)
        
        self.branch_combo = QComboBox()
        self.branch_combo.setMinimumWidth(150)
        self.branch_combo.setStyleSheet('''
            QComboBox {
                background: #2c3138;
                color: #e6e6e6;
                border: 1px solid #3a3d45;
                border-radius: 4px;
                padding: 4px 8px;
                margin-right: 8px;
            }
            QComboBox:hover {
                border-color: #5aa0ff;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #e6e6e6;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background: #2c3138;
                color: #e6e6e6;
                border: 1px solid #3a3d45;
                selection-background-color: #3a74b4;
            }
        ''')
        self.branch_combo.currentTextChanged.connect(self.on_branch_changed)
        self.branch_combo.setEnabled(False)
        self.status.addPermanentWidget(QLabel("Branch:"))
        self.status.addPermanentWidget(self.branch_combo)
        
        self.new_branch_button = QPushButton("New Branch")
        self.new_branch_button.setStyleSheet('''
            QPushButton {
                background: #2c3138;
                color: #e6e6e6;
                border: 1px solid #3a3d45;
                border-radius: 4px;
                padding: 4px 12px;
                margin-right: 8px;
            }
            QPushButton:hover {
                background: #3a74b4;
                border-color: #5aa0ff;
            }
            QPushButton:disabled {
                color: #5a5d65;
                background: #23262b;
            }
        ''')
        self.new_branch_button.clicked.connect(self.create_new_branch)
        self.new_branch_button.setEnabled(False)
        self.status.addPermanentWidget(self.new_branch_button)
        
        self.rename_branch_button = QPushButton("Rename Branch")
        self.rename_branch_button.setStyleSheet('''
            QPushButton {
                background: #2c3138;
                color: #e6e6e6;
                border: 1px solid #3a3d45;
                border-radius: 4px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background: #3a74b4;
                border-color: #5aa0ff;
            }
            QPushButton:disabled {
                color: #5a5d65;
                background: #23262b;
            }
        ''')
        self.rename_branch_button.clicked.connect(self.rename_current_branch)
        self.rename_branch_button.setEnabled(False)
        self.status.addPermanentWidget(self.rename_branch_button)
        
        self.setStatusBar(self.status)

        self.history = []
        self.update_path_bar()
        self.filtered_indexes = None

        self.setStyleSheet('''
            QMainWindow {
                background: #1f2227;
            }
            QToolBar {
                background: #1b1d21;
                spacing: 8px;
                border: none;
                padding: 6px 8px;
            }
            QToolBar QToolButton {
                background: transparent;
                color: #e6e6e6;
                padding: 6px 8px;
                border-radius: 6px;
            }
            QToolBar QToolButton:hover {
                background: #2a2d33;
            }
            QToolBar QToolButton:disabled {
                color: #5a5d65;
            }
            QWidget#BreadcrumbButton {
                background: transparent;
            }
            QListView {
                background: #23262b;
                color: #e8eaed;
                border: none;
                font-size: 15px;
                icon-size: 64px 64px;
            }
            QListView::item {
                margin: 6px;
                border: 1px solid transparent;
                border-radius: 10px;
            }
            QListView::item:hover {
                background: #2c3138;
                border-color: #3a3f47;
            }
            QListView::item:selected {
                background: #3a74b4;
                color: #ffffff;
                border: 1px solid #5aa0ff;
            }
            QListWidget {
                background: #1b1d21;
                color: #e6e6e6;
                border: none;
            }
            QListWidget::item {
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background: #3a74b4;
                color: #ffffff;
            }
            QSplitter::handle {
                background: #2a2d33;
            }
            QStatusBar {
                background: #1b1d21;
                color: #c9c9c9;
                border-top: 1px solid #2a2d33;
            }
            QLineEdit {
                background: #23262b;
                color: #e6e6e6;
                border: 1px solid #3a3d45;
                padding: 6px 8px;
                min-width: 300px;
                border-radius: 6px;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                background: transparent;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background: #3a3d45;
                min-height: 30px;
                min-width: 30px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
                background: #5aa0ff;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                height: 0px;
                width: 0px;
            }
            QScrollBar::add-page, QScrollBar::sub-page {
                background: none;
            }
            QMenu {
                background: #22252a;
                color: #e6e6e6;
                border: 1px solid #3a3d45;
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                padding: 6px 10px;
                border-radius: 6px;
            }
            QMenu::item:selected {
                background: #2c3138;
            }
        ''')

        self.view.setFlow(QListView.LeftToRight)
        self.view.setWrapping(True)
        self.view.setUniformItemSizes(True)
        self.view.setTextElideMode(Qt.ElideRight)
        self.view.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.view.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.rebuild_breadcrumbs()
        self.update_git_buttons()

    def update_git_status_display(self):
        """Update the Git status display in the status bar"""
        if self.is_authenticated:
            auth_text = f"<span style='color: #50fa7b;'>● Git: {self.git_username}</span>"
        else:
            auth_text = "<span style='color: #ff5555;'>● Git: Not configured</span>"
        
        if GitManager.is_git_repo(self.current_path):
            branch = GitManager.get_current_branch(self.current_path)
            status = GitManager.get_repo_status(self.current_path)
            if status:
                changes = f"M:{status['modified']} A:{status['added']} D:{status['deleted']}"
                repo_text = f" | <span style='color: #8be9fd;'>Branch: {branch}</span> | {changes}"
            else:
                repo_text = f" | <span style='color: #8be9fd;'>Branch: {branch}</span>"
            self.git_status_label.setText(auth_text + repo_text)
            self.update_branch_selector()
        else:
            self.git_status_label.setText(auth_text)
            self.branch_combo.clear()
            self.branch_combo.setEnabled(False)
            self.new_branch_button.setEnabled(False)
            self.rename_branch_button.setEnabled(False)

    def update_branch_selector(self):
        """Update the branch combo box with available branches"""
        if not GitManager.is_git_repo(self.current_path):
            self.branch_combo.clear()
            self.branch_combo.setEnabled(False)
            self.new_branch_button.setEnabled(False)
            self.rename_branch_button.setEnabled(False)
            return
        
        current_branch = GitManager.get_current_branch(self.current_path)
        branches = GitManager.get_all_branches(self.current_path)
        
        self.branch_combo.blockSignals(True)
        self.branch_combo.clear()
        
        if branches:
            self.branch_combo.addItems(branches)
            if current_branch in branches:
                self.branch_combo.setCurrentText(current_branch)
            self.branch_combo.setEnabled(True)
            self.new_branch_button.setEnabled(True)
            self.rename_branch_button.setEnabled(True)
        else:
            self.branch_combo.setEnabled(False)
            self.new_branch_button.setEnabled(False)
            self.rename_branch_button.setEnabled(False)
        
        self.branch_combo.blockSignals(False)

    def on_branch_changed(self, branch_name):
        """Handle branch selection change"""
        if not branch_name or not GitManager.is_git_repo(self.current_path):
            return
        
        current_branch = GitManager.get_current_branch(self.current_path)
        if branch_name == current_branch:
            return
        
        reply = QMessageBox.question(
            self,
            "Switch Branch",
            f"Switch from '{current_branch}' to '{branch_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, result = GitManager.checkout_branch(self.current_path, branch_name)
            if success:
                self.status.showMessage(result)
                self.update_git_status_display()
            else:
                QMessageBox.critical(self, "Checkout Failed", f"Failed to switch branch:\n{result}")
                self.branch_combo.blockSignals(True)
                self.branch_combo.setCurrentText(current_branch)
                self.branch_combo.blockSignals(False)
        else:
            self.branch_combo.blockSignals(True)
            self.branch_combo.setCurrentText(current_branch)
            self.branch_combo.blockSignals(False)

    def create_new_branch(self):
        """Create a new Git branch"""
        if not GitManager.is_git_repo(self.current_path):
            return
        
        branch_name, ok = QInputDialog.getText(
            self,
            "Create New Branch",
            "Enter new branch name:",
            QLineEdit.Normal,
            ""
        )
        
        if ok and branch_name:
            branch_name = branch_name.strip()
            if not branch_name:
                QMessageBox.warning(self, "Invalid Name", "Branch name cannot be empty.")
                return
            
            success, result = GitManager.create_branch(self.current_path, branch_name)
            if success:
                QMessageBox.information(self, "Success", result)
                self.update_git_status_display()
            else:
                QMessageBox.critical(self, "Failed", f"Failed to create branch:\n{result}")

    def rename_current_branch(self):
        """Rename the current Git branch"""
        if not GitManager.is_git_repo(self.current_path):
            return
        
        current_branch = GitManager.get_current_branch(self.current_path)
        if not current_branch:
            QMessageBox.warning(self, "No Branch", "Could not determine current branch.")
            return
        
        new_name, ok = QInputDialog.getText(
            self,
            "Rename Branch",
            f"Rename '{current_branch}' to:",
            QLineEdit.Normal,
            current_branch
        )
        
        if ok and new_name:
            new_name = new_name.strip()
            if not new_name:
                QMessageBox.warning(self, "Invalid Name", "Branch name cannot be empty.")
                return
            
            if new_name == current_branch:
                return
            
            success, result = GitManager.rename_branch(self.current_path, current_branch, new_name)
            if success:
                QMessageBox.information(self, "Success", result)
                self.update_git_status_display()
            else:
                QMessageBox.critical(self, "Failed", f"Failed to rename branch:\n{result}")

    def update_git_buttons(self):
        """Enable/disable Git buttons based on current directory"""
        is_git_repo = GitManager.is_git_repo(self.current_path)
        self.action_git_commit.setEnabled(is_git_repo)
        self.action_git_pull.setEnabled(is_git_repo)
        self.action_git_push.setEnabled(is_git_repo)
        self.update_git_status_display()

    def show_git_commit_dialog(self):
        """Show the Git commit dialog"""
        if not GitManager.is_git_repo(self.current_path):
            QMessageBox.warning(self, "Not a Git Repository", 
                              "The current directory is not a Git repository.")
            return
        
        dialog = GitCommitDialog(self.current_path, self)
        if dialog.exec() == QDialog.Accepted:
            self.update_git_status_display()

    def git_pull(self):
        """Pull changes from remote repository"""
        if not GitManager.is_git_repo(self.current_path):
            return
        
        reply = QMessageBox.question(self, "Git Pull", 
                                     "Pull changes from remote repository?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, result = GitManager.pull_changes(self.current_path)
            if success:
                QMessageBox.information(self, "Success", "Changes pulled successfully!")
            else:
                QMessageBox.critical(self, "Pull Failed", f"Failed to pull changes:\n{result}")
            self.update_git_status_display()

    def git_push(self):
        """Push changes to remote repository"""
        if not GitManager.is_git_repo(self.current_path):
            return
        
        reply = QMessageBox.question(self, "Git Push", 
                                     "Push changes to remote repository?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, result = GitManager.push_changes(self.current_path)
            if success:
                QMessageBox.information(self, "Success", "Changes pushed successfully!")
            else:
                QMessageBox.critical(self, "Push Failed", f"Failed to push changes:\n{result}")
            self.update_git_status_display()

    def update_path_bar(self):
        self.path_bar.setText(self.current_path)
        self.rebuild_breadcrumbs()
        self.update_git_buttons()

    def show_path_editor(self):
        self.path_stack.setCurrentWidget(self.path_bar)
        self.path_bar.setFocus()
        self.path_bar.selectAll()

    def hide_path_editor(self):
        self.path_stack.setCurrentWidget(self.breadcrumbs)

    def rebuild_breadcrumbs(self):
        while self.breadcrumbs_layout.count():
            item = self.breadcrumbs_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        path = os.path.abspath(self.current_path)
        home = os.path.abspath(QDir.homePath())

        segments = []
        if path == "/":
            segments = [("/", "/", QIcon.fromTheme("drive-harddisk"))]
        elif path.startswith(home):
            rel = os.path.relpath(path, home)
            parts = [] if rel == "." else rel.split(os.sep)
            segments.append(("Home", home, QIcon.fromTheme("user-home")))
            accum = home
            for part in parts:
                accum = os.path.join(accum, part)
                icon = QIcon.fromTheme("vcs-git") if GitManager.is_git_repo(accum) else QIcon.fromTheme("folder")
                segments.append((part, accum, icon))
        else:
            accum = "/"
            root_parts = [p for p in path.split(os.sep) if p]
            segments.append(("/", "/", QIcon.fromTheme("drive-harddisk")))
            for part in root_parts:
                accum = os.path.join(accum, part)
                icon = QIcon.fromTheme("vcs-git") if GitManager.is_git_repo(accum) else QIcon.fromTheme("folder")
                segments.append((part, accum, icon))

        def add_separator():
            sep = QLabel("›")
            sep.setStyleSheet("color: #6f737a; padding: 0 6px;")
            self.breadcrumbs_layout.addWidget(sep)

        for i, (label, full_path, icon) in enumerate(segments):
            btn = QToolButton()
            btn.setObjectName("BreadcrumbButton")
            btn.setIcon(icon)
            btn.setText(label)
            btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            btn.setAutoRaise(True)
            btn.setStyleSheet("padding: 6px 8px; border-radius: 6px; color: #e6e6e6;")
            btn.clicked.connect(lambda checked=False, p=full_path: self._on_breadcrumb_clicked(p))
            self.breadcrumbs_layout.addWidget(btn)
            if i < len(segments) - 1:
                add_separator()
        self.breadcrumbs_layout.addStretch(1)

    def _on_breadcrumb_clicked(self, path):
        if os.path.isdir(path):
            self.history.append(self.current_path)
            self.current_path = path
            self.view.setRootIndex(self.model.index(path))
            self.update_path_bar()
            self.hide_path_editor()
            self.status.showMessage(f"Navigated to: {path}")

    def go_back(self):
        if self.history:
            self.current_path = self.history.pop()
            self.view.setRootIndex(self.model.index(self.current_path))
            self.update_path_bar()
            self.status.showMessage(f"Went back to: {self.current_path}")

    def go_home(self):
        if self.current_path != QDir.homePath():
            self.history.append(self.current_path)
            self.current_path = QDir.homePath()
            self.view.setRootIndex(self.model.index(self.current_path))
            self.update_path_bar()
            self.status.showMessage(f"Went home: {self.current_path}")

    def on_double_click(self, index: QModelIndex):
        path = self.model.filePath(index)
        if os.path.isdir(path):
            self.history.append(self.current_path)
            self.current_path = path
            self.view.setRootIndex(self.model.index(path))
            self.update_path_bar()
            self.status.showMessage(f"Opened folder: {path}")
        else:
            self.status.showMessage(f"Opening file: {path}")
            try:
                subprocess.Popen(["xdg-open", path])
            except Exception as e:
                self.status.showMessage(f"Failed to open: {e}")

    def open_context_menu(self, position):
        index = self.view.indexAt(position)
        if not index.isValid():
            return
        path = self.model.filePath(index)
        is_dir = os.path.isdir(path)
        is_git = GitManager.is_git_repo(path) if is_dir else False
        
        menu = QMenu()
        
        open_action = QAction(QIcon.fromTheme("document-open"), "Open", self)
        open_action.triggered.connect(lambda: self.on_double_click(index))
        menu.addAction(open_action)
        
        if is_git:
            menu.addSeparator()
            git_menu = menu.addMenu(QIcon.fromTheme("vcs-git"), "Git")
            
            commit_action = QAction(QIcon.fromTheme("vcs-commit"), "Commit...", self)
            commit_action.triggered.connect(lambda: self.show_git_commit_for_path(path))
            git_menu.addAction(commit_action)
            
            pull_action = QAction(QIcon.fromTheme("vcs-update"), "Pull", self)
            pull_action.triggered.connect(lambda: self.git_pull_for_path(path))
            git_menu.addAction(pull_action)
            
            push_action = QAction(QIcon.fromTheme("vcs-push"), "Push", self)
            push_action.triggered.connect(lambda: self.git_push_for_path(path))
            git_menu.addAction(push_action)
            
            git_menu.addSeparator()
            
            status_action = QAction(QIcon.fromTheme("vcs-status"), "Show Status", self)
            status_action.triggered.connect(lambda: self.show_git_status(path))
            git_menu.addAction(status_action)
        
        open_new_window_action = QAction(QIcon.fromTheme("window-new"), "Open in New Window", self)
        open_new_window_action.triggered.connect(lambda: subprocess.Popen([sys.executable, sys.argv[0], path]))
        menu.addAction(open_new_window_action)
        
        open_with_menu = menu.addMenu(QIcon.fromTheme("system-run"), "Open With")
        open_with_default = QAction("Default Application", self)
        open_with_default.triggered.connect(lambda: subprocess.Popen(["xdg-open", path]))
        open_with_menu.addAction(open_with_default)
        
        if not is_dir:
            send_to_menu = menu.addMenu(QIcon.fromTheme("mail-send"), "Send To")
            send_to_menu.addAction(QAction("Desktop", self))
            send_to_menu.addAction(QAction("Documents", self))
        
        menu.addSeparator()
        cut_action = QAction(QIcon.fromTheme("edit-cut"), "Cut", self)
        copy_action = QAction(QIcon.fromTheme("edit-copy"), "Copy", self)
        paste_action = QAction(QIcon.fromTheme("edit-paste"), "Paste", self)
        menu.addAction(cut_action)
        menu.addAction(copy_action)
        menu.addAction(paste_action)
        
        menu.addSeparator()
        delete_action = QAction(QIcon.fromTheme("edit-delete"), "Delete", self)
        delete_action.triggered.connect(lambda: self.delete_item(path))
        menu.addAction(delete_action)
        
        rename_action = QAction(QIcon.fromTheme("edit-rename"), "Rename", self)
        rename_action.triggered.connect(lambda: self.rename_item(index, path))
        menu.addAction(rename_action)
        
        if not is_dir:
            archive_action = QAction(QIcon.fromTheme("package-x-generic"), "Create Archive...", self)
            archive_action.triggered.connect(lambda: self.create_archive(path))
            menu.addAction(archive_action)
        
        if is_dir:
            terminal_action = QAction(QIcon.fromTheme("utilities-terminal"), "Open Terminal Here", self)
            terminal_action.triggered.connect(lambda: subprocess.Popen(["x-terminal-emulator" if shutil.which("x-terminal-emulator") else "gnome-terminal", "--working-directory", path]))
            menu.addAction(terminal_action)
        
        menu.addSeparator()
        properties_action = QAction(QIcon.fromTheme("document-properties"), "Properties...", self)
        properties_action.triggered.connect(lambda: self.show_properties(path))
        menu.addAction(properties_action)
        
        menu.exec(self.view.viewport().mapToGlobal(position))

    def show_git_commit_for_path(self, path):
        """Show Git commit dialog for a specific path"""
        dialog = GitCommitDialog(path, self)
        if dialog.exec() == QDialog.Accepted:
            self.update_git_status_display()

    def git_pull_for_path(self, path):
        """Pull changes for a specific Git repository"""
        reply = QMessageBox.question(self, "Git Pull", 
                                     f"Pull changes for {os.path.basename(path)}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, result = GitManager.pull_changes(path)
            if success:
                QMessageBox.information(self, "Success", "Changes pulled successfully!")
            else:
                QMessageBox.critical(self, "Pull Failed", f"Failed to pull changes:\n{result}")
            self.update_git_status_display()

    def git_push_for_path(self, path):
        """Push changes for a specific Git repository"""
        reply = QMessageBox.question(self, "Git Push", 
                                     f"Push changes for {os.path.basename(path)}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, result = GitManager.push_changes(path)
            if success:
                QMessageBox.information(self, "Success", "Changes pushed successfully!")
            else:
                QMessageBox.critical(self, "Push Failed", f"Failed to push changes:\n{result}")
            self.update_git_status_display()

    def show_git_status(self, path):
        """Show detailed Git status for a repository"""
        branch = GitManager.get_current_branch(path)
        status = GitManager.get_repo_status(path)
        remote = GitManager.get_remote_url(path)
        
        status_text = f"<b>Repository:</b> {os.path.basename(path)}<br>"
        status_text += f"<b>Branch:</b> {branch or 'Unknown'}<br>"
        if remote:
            status_text += f"<b>Remote:</b> {remote}<br>"
        status_text += "<br><b>Status:</b><br>"
        
        if status:
            if status['clean']:
                status_text += "Working tree clean ✓"
            else:
                status_text += f"Modified files: {status['modified']}<br>"
                status_text += f"Added files: {status['added']}<br>"
                status_text += f"Deleted files: {status['deleted']}"
        else:
            status_text += "Unable to get status"
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Git Status")
        msg.setTextFormat(Qt.RichText)
        msg.setText(status_text)
        msg.setIcon(QMessageBox.Information)
        msg.exec()

    def delete_item(self, path):
        reply = QMessageBox.question(self, "Delete", f"Are you sure you want to delete '{os.path.basename(path)}'?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self.status.showMessage(f"Deleted: {path}")
                self.view.setRootIndex(self.model.index(self.current_path))
            except Exception as e:
                self.status.showMessage(f"Failed to delete: {e}")

    def rename_item(self, index, path):
        new_name, ok = QFileDialog.getSaveFileName(self, "Rename", path)
        if ok and new_name:
            try:
                os.rename(path, new_name)
                self.status.showMessage(f"Renamed to: {new_name}")
                self.view.setRootIndex(self.model.index(self.current_path))
            except Exception as e:
                self.status.showMessage(f"Failed to rename: {e}")

    def create_archive(self, path):
        archive_path, ok = QFileDialog.getSaveFileName(self, "Create Archive", path + ".zip", "Zip Files (*.zip)")
        if ok and archive_path:
            try:
                with zipfile.ZipFile(archive_path, 'w') as zipf:
                    zipf.write(path, os.path.basename(path))
                self.status.showMessage(f"Archive created: {archive_path}")
            except Exception as e:
                self.status.showMessage(f"Failed to create archive: {e}")

    def show_properties(self, path):
        info = os.stat(path)
        prop_text = f"Path: {path}\nSize: {info.st_size} bytes\nPermissions: {oct(info.st_mode)}\nLast modified: {info.st_mtime}"
        
        if os.path.isdir(path) and GitManager.is_git_repo(path):
            branch = GitManager.get_current_branch(path)
            remote = GitManager.get_remote_url(path)
            status = GitManager.get_repo_status(path)
            
            prop_text += f"\n\n--- Git Information ---"
            prop_text += f"\nBranch: {branch or 'Unknown'}"
            if remote:
                prop_text += f"\nRemote: {remote}"
            if status:
                prop_text += f"\nModified: {status['modified']}, Added: {status['added']}, Deleted: {status['deleted']}"
        
        QMessageBox.information(self, "Properties", prop_text)

    def populate_sidebar(self):
        self.sidebar.clear()
        home = QDir.homePath()
        places = [
            ("daniel", home, QIcon.fromTheme("user-home")),
            ("Desktop", os.path.join(home, "Desktop"), QIcon.fromTheme("user-desktop")),
            ("portfolio-website", os.path.join(home, "portfolio-website"), QIcon.fromTheme("folder")),
            ("C++ Projects", os.path.join(home, "C++ Projects"), QIcon.fromTheme("folder")),
            ("Music", os.path.join(home, "Music"), QIcon.fromTheme("folder-music")),
            ("Pictures", os.path.join(home, "Pictures"), QIcon.fromTheme("folder-pictures")),
            ("Videos", os.path.join(home, "Videos"), QIcon.fromTheme("folder-videos")),
            ("Downloads", os.path.join(home, "Downloads"), QIcon.fromTheme("folder-downloads")),
            ("Documents", os.path.join(home, "Documents"), QIcon.fromTheme("folder-documents")),
        ]
        for name, path, icon in places:
            if os.path.isdir(path) and GitManager.is_git_repo(path):
                icon = QIcon.fromTheme("vcs-git")
            item = QListWidgetItem(icon, name)
            item.setData(Qt.UserRole, path)
            self.sidebar.addItem(item)
        self.sidebar.addItem("")
        device_item = QListWidgetItem(QIcon.fromTheme("drive-harddisk"), "File System")
        device_item.setData(Qt.UserRole, "/")
        font = device_item.font()
        font.setBold(True)
        device_item.setFont(font)
        self.sidebar.addItem(device_item)

    def sidebar_navigate(self, current, previous):
        if current:
            path = current.data(Qt.UserRole)
            if path:
                self.history.append(self.current_path)
                self.current_path = path
                self.view.setRootIndex(self.model.index(path))
                self.update_path_bar()
                self.status.showMessage(f"Navigated to: {path}")

    def filter_files(self, text):
        root_index = self.model.index(self.current_path)
        for row in range(self.model.rowCount(root_index)):
            index = self.model.index(row, 0, root_index)
            item_name = self.model.fileName(index)
            is_match = text.lower() in item_name.lower()
            self.view.setRowHidden(row, root_index, not is_match if text else False)

    def on_path_bar_entered(self):
        path = self.path_bar.text().strip()
        if os.path.isdir(path):
            self.history.append(self.current_path)
            self.current_path = path
            self.view.setRootIndex(self.model.index(path))
            self.update_path_bar()
            self.status.showMessage(f"Navigated to: {path}")
        else:
            self.status.showMessage(f"Invalid directory: {path}")


if __name__ == "__main__":
    QIcon.setThemeName("Papirus-Dark")
    app = QApplication(sys.argv)
    window = FileExplorer()
    window.show()
    sys.exit(app.exec())