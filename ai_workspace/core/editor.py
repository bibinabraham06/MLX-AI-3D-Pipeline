"""Integrated Code Editor Engine - Like Claude Code/VS Code"""

from typing import Optional, List, Dict, Any, Union, AsyncGenerator
from pathlib import Path
import asyncio
import time
import os
import subprocess
from dataclasses import dataclass, asdict
from enum import Enum
import mimetypes
import json

from ..config import get_config


class FileType(Enum):
    """Supported file types"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    HTML = "html"
    CSS = "css"
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"
    TEXT = "text"
    IMAGE = "image"
    BINARY = "binary"


@dataclass
class FileInfo:
    """File information"""
    path: Path
    name: str
    size: int
    modified: float
    file_type: FileType
    is_directory: bool
    permissions: str
    encoding: Optional[str] = None


@dataclass
class EditorSession:
    """Editor session state"""
    session_id: str
    project_path: Path
    open_files: List[str]
    active_file: Optional[str]
    cursor_position: Dict[str, Any]
    settings: Dict[str, Any]
    created_at: float
    last_activity: float


@dataclass
class SearchResult:
    """Search result"""
    file_path: Path
    line_number: int
    column_start: int
    column_end: int
    content: str
    context_before: List[str]
    context_after: List[str]


@dataclass
class CodeCompletionRequest:
    """Code completion request"""
    file_path: Path
    content: str
    cursor_position: int
    language: str
    context_lines: int = 10


@dataclass
class CodeCompletionResult:
    """Code completion result"""
    suggestions: List[Dict[str, Any]]
    documentation: Optional[str]
    type_info: Optional[str]


class CodeEditorEngine:
    """Modern code editor engine with AI assistance"""

    def __init__(self):
        self.config = get_config()
        self.active_sessions: Dict[str, EditorSession] = {}
        self.file_watchers: Dict[str, Any] = {}

    async def initialize(self):
        """Initialize the editor engine"""
        pass

    # File Operations
    async def read_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Read file content with metadata"""
        path = Path(file_path).absolute()

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        try:
            # Get file info
            stat = path.stat()
            file_info = FileInfo(
                path=path,
                name=path.name,
                size=stat.st_size,
                modified=stat.st_mtime,
                file_type=self._detect_file_type(path),
                is_directory=path.is_dir(),
                permissions=oct(stat.st_mode)[-3:],
            )

            if file_info.is_directory:
                return {"type": "directory", "info": asdict(file_info)}

            # Read content based on file type
            if file_info.file_type in [FileType.IMAGE, FileType.BINARY]:
                return {
                    "type": "binary",
                    "info": asdict(file_info),
                    "content": None,
                    "message": "Binary file - cannot display content"
                }

            # Read text content
            encodings = ['utf-8', 'utf-16', 'latin-1']
            content = None
            encoding_used = None

            for encoding in encodings:
                try:
                    content = path.read_text(encoding=encoding)
                    encoding_used = encoding
                    break
                except UnicodeDecodeError:
                    continue

            if content is None:
                return {
                    "type": "binary",
                    "info": asdict(file_info),
                    "content": None,
                    "message": "Could not decode file content"
                }

            file_info.encoding = encoding_used

            return {
                "type": "text",
                "info": asdict(file_info),
                "content": content,
                "lines": content.count('\n') + 1
            }

        except Exception as e:
            raise RuntimeError(f"Error reading file {path}: {e}")

    async def write_file(self, file_path: Union[str, Path], content: str,
                        encoding: str = 'utf-8') -> Dict[str, Any]:
        """Write content to file"""
        path = Path(file_path).absolute()

        try:
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)

            # Write content
            path.write_text(content, encoding=encoding)

            # Return updated file info
            return await self.read_file(path)

        except Exception as e:
            raise RuntimeError(f"Error writing file {path}: {e}")

    async def list_directory(self, dir_path: Union[str, Path],
                           include_hidden: bool = False) -> List[Dict[str, Any]]:
        """List directory contents"""
        path = Path(dir_path).absolute()

        if not path.exists() or not path.is_dir():
            raise ValueError(f"Directory not found: {path}")

        items = []
        try:
            for item in sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                if not include_hidden and item.name.startswith('.'):
                    continue

                stat = item.stat()
                file_info = FileInfo(
                    path=item,
                    name=item.name,
                    size=stat.st_size,
                    modified=stat.st_mtime,
                    file_type=self._detect_file_type(item),
                    is_directory=item.is_dir(),
                    permissions=oct(stat.st_mode)[-3:],
                )

                items.append(asdict(file_info))

            return items

        except Exception as e:
            raise RuntimeError(f"Error listing directory {path}: {e}")

    # Search Operations
    async def search_in_file(self, file_path: Union[str, Path], query: str,
                           case_sensitive: bool = False, regex: bool = False) -> List[SearchResult]:
        """Search for text in a specific file"""
        import re

        path = Path(file_path)
        results = []

        try:
            content = await self.read_file(path)
            if content["type"] != "text":
                return results

            lines = content["content"].split('\n')
            flags = 0 if case_sensitive else re.IGNORECASE

            if regex:
                pattern = re.compile(query, flags)
            else:
                pattern = re.compile(re.escape(query), flags)

            for i, line in enumerate(lines):
                for match in pattern.finditer(line):
                    result = SearchResult(
                        file_path=path,
                        line_number=i + 1,
                        column_start=match.start(),
                        column_end=match.end(),
                        content=line,
                        context_before=lines[max(0, i-2):i],
                        context_after=lines[i+1:min(len(lines), i+3)]
                    )
                    results.append(result)

            return results

        except Exception as e:
            print(f"Error searching file {path}: {e}")
            return []

    async def search_in_project(self, project_path: Union[str, Path], query: str,
                              file_pattern: str = "*", case_sensitive: bool = False,
                              regex: bool = False) -> List[SearchResult]:
        """Search across all files in a project"""
        path = Path(project_path)
        all_results = []

        # Get all matching files
        if file_pattern == "*":
            files = list(path.rglob("*"))
        else:
            files = list(path.rglob(file_pattern))

        # Filter to text files only
        text_files = [f for f in files if f.is_file() and
                     self._detect_file_type(f) not in [FileType.IMAGE, FileType.BINARY]]

        # Search in each file
        for file_path in text_files[:100]:  # Limit to first 100 files for performance
            file_results = await self.search_in_file(file_path, query, case_sensitive, regex)
            all_results.extend(file_results)

        return all_results

    # AI-Powered Features
    async def get_code_completion(self, request: CodeCompletionRequest) -> CodeCompletionResult:
        """Get AI-powered code completion"""
        # This would integrate with the chat engine for code completion
        # For now, return basic completions

        suggestions = []

        # Basic Python completions
        if request.language == "python":
            keywords = ["def", "class", "if", "else", "elif", "for", "while", "try", "except", "import", "from"]
            current_line = request.content[:request.cursor_position].split('\n')[-1]

            for keyword in keywords:
                if keyword.startswith(current_line.split()[-1] if current_line.split() else ""):
                    suggestions.append({
                        "label": keyword,
                        "kind": "keyword",
                        "insertText": keyword,
                        "detail": f"Python keyword: {keyword}"
                    })

        return CodeCompletionResult(
            suggestions=suggestions[:10],  # Limit to 10 suggestions
            documentation=None,
            type_info=None
        )

    async def format_code(self, content: str, language: str) -> str:
        """Format code using appropriate formatter"""
        if language == "python":
            try:
                # Use black for Python formatting
                process = await asyncio.create_subprocess_exec(
                    "black", "--code", content,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()

                if process.returncode == 0:
                    return stdout.decode()
            except FileNotFoundError:
                pass  # black not installed

        elif language == "javascript" or language == "typescript":
            try:
                # Use prettier for JS/TS formatting
                process = await asyncio.create_subprocess_exec(
                    "prettier", "--parser", "typescript",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    stdin=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate(content.encode())

                if process.returncode == 0:
                    return stdout.decode()
            except FileNotFoundError:
                pass  # prettier not installed

        # Return original content if no formatter available
        return content

    async def lint_code(self, content: str, language: str, file_path: Path) -> List[Dict[str, Any]]:
        """Lint code and return issues"""
        issues = []

        if language == "python":
            try:
                # Use flake8 for Python linting
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(content)
                    f.flush()

                    process = await asyncio.create_subprocess_exec(
                        "flake8", "--format=json", f.name,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await process.communicate()

                    if stdout:
                        # Parse flake8 output (this is simplified)
                        for line in stdout.decode().split('\n'):
                            if line.strip():
                                issues.append({
                                    "severity": "warning",
                                    "message": line,
                                    "line": 1,
                                    "column": 1
                                })

                os.unlink(f.name)
            except Exception:
                pass

        return issues

    # Session Management
    async def create_session(self, project_path: Union[str, Path]) -> EditorSession:
        """Create a new editor session"""
        import uuid

        session_id = str(uuid.uuid4())
        session = EditorSession(
            session_id=session_id,
            project_path=Path(project_path),
            open_files=[],
            active_file=None,
            cursor_position={},
            settings={},
            created_at=time.time(),
            last_activity=time.time()
        )

        self.active_sessions[session_id] = session
        return session

    async def get_session(self, session_id: str) -> Optional[EditorSession]:
        """Get editor session by ID"""
        return self.active_sessions.get(session_id)

    async def update_session(self, session_id: str, **updates) -> EditorSession:
        """Update editor session"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session not found: {session_id}")

        session = self.active_sessions[session_id]
        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)

        session.last_activity = time.time()
        return session

    # Utility Methods
    def _detect_file_type(self, file_path: Path) -> FileType:
        """Detect file type based on extension and content"""
        suffix = file_path.suffix.lower()

        type_map = {
            '.py': FileType.PYTHON,
            '.js': FileType.JAVASCRIPT,
            '.ts': FileType.TYPESCRIPT,
            '.html': FileType.HTML,
            '.css': FileType.CSS,
            '.json': FileType.JSON,
            '.yaml': FileType.YAML,
            '.yml': FileType.YAML,
            '.md': FileType.MARKDOWN,
            '.txt': FileType.TEXT,
            '.png': FileType.IMAGE,
            '.jpg': FileType.IMAGE,
            '.jpeg': FileType.IMAGE,
            '.gif': FileType.IMAGE,
            '.svg': FileType.IMAGE,
        }

        if suffix in type_map:
            return type_map[suffix]

        # Use mimetypes for unknown extensions
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            if mime_type.startswith('text/'):
                return FileType.TEXT
            elif mime_type.startswith('image/'):
                return FileType.IMAGE

        return FileType.BINARY

    async def cleanup(self):
        """Clean up resources"""
        # Close file watchers
        for watcher in self.file_watchers.values():
            if hasattr(watcher, 'close'):
                watcher.close()

        self.file_watchers.clear()
        self.active_sessions.clear()