"""
Project initialization component for automatically detecting project type and configuring settings
"""

import logging
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
import fnmatch

logger = logging.getLogger("files-db-mcp.project_initializer")

# Project type detection patterns
PROJECT_TYPE_PATTERNS = {
    "python": ["pyproject.toml", "setup.py", "requirements.txt", "__init__.py"],
    "javascript": ["package.json", "package-lock.json", "yarn.lock", "node_modules"],
    "typescript": ["tsconfig.json", "tsc.config", "index.ts", "package.json"],
    "go": ["go.mod", "go.sum", "main.go", ".go"],
    "rust": ["Cargo.toml", "Cargo.lock", "src/main.rs", "src/lib.rs"],
    "java": ["pom.xml", "build.gradle", "settings.gradle", ".java"],
    "c_cpp": ["CMakeLists.txt", "Makefile", ".cpp", ".hpp", ".c", ".h"],
    "csharp": [".csproj", ".sln", "Program.cs", "NuGet.Config"],
    "php": ["composer.json", "composer.lock", "artisan", ".php"],
    "ruby": ["Gemfile", "Rakefile", ".ruby-version", ".rb"],
}

# Default embedding models by project type
DEFAULT_EMBEDDING_MODELS = {
    "python": "jinaai/jina-embeddings-v2-base-code",
    "javascript": "jinaai/jina-embeddings-v2-base-code",
    "typescript": "jinaai/jina-embeddings-v2-base-code",
    "go": "Salesforce/SFR-Embedding-2_R",
    "rust": "Salesforce/SFR-Embedding-2_R",
    "java": "Alibaba-NLP/gte-large-en-v1.5",
    "c_cpp": "Salesforce/SFR-Embedding-2_R",
    "csharp": "Alibaba-NLP/gte-large-en-v1.5",
    "php": "BAAI/bge-large-en-v1.5",
    "ruby": "BAAI/bge-large-en-v1.5",
    # Fallback for unknown project types
    "default": "sentence-transformers/all-MiniLM-L6-v2",
}

# Default model configurations by project type
DEFAULT_MODEL_CONFIGS = {
    "python": {
        "device": "auto",
        "normalize_embeddings": True,
        "quantization": "int8",
        "prompt_template": "Code: {text}"
    },
    "javascript": {
        "device": "auto",
        "normalize_embeddings": True,
        "quantization": "int8",
        "prompt_template": "Code: {text}"
    },
    "typescript": {
        "device": "auto",
        "normalize_embeddings": True,
        "quantization": "int8",
        "prompt_template": "Code: {text}"
    },
    "go": {
        "device": "auto",
        "normalize_embeddings": True,
        "prompt_template": "Code: {text}"
    },
    "rust": {
        "device": "auto",
        "normalize_embeddings": True,
        "prompt_template": "Code: {text}"
    },
    "java": {
        "device": "auto",
        "normalize_embeddings": True,
        "quantization": "int8",
    },
    "c_cpp": {
        "device": "auto",
        "normalize_embeddings": True,
        "prompt_template": "Code: {text}"
    },
    "csharp": {
        "device": "auto", 
        "normalize_embeddings": True,
        "quantization": "int8",
    },
    "php": {
        "device": "auto",
        "normalize_embeddings": True,
        "quantization": "int8",
    },
    "ruby": {
        "device": "auto",
        "normalize_embeddings": True,
        "quantization": "int8",
    },
    # Fallback for unknown project types
    "default": {
        "device": "auto",
        "normalize_embeddings": True,
        "quantization": "int8",
    },
}

# Default ignore patterns by project type (in addition to global ones)
DEFAULT_IGNORE_PATTERNS = {
    "python": ["venv/", "env/", "__pycache__/", "*.pyc", "*.pyo", "*.egg-info/", "dist/", "build/"],
    "javascript": ["node_modules/", "dist/", "build/", "coverage/", ".next/", ".cache/"],
    "typescript": ["node_modules/", "dist/", "build/", "coverage/", ".next/", ".cache/"],
    "go": ["vendor/", "bin/", "*.test"],
    "rust": ["target/", "debug/", "release/", "Cargo.lock"],
    "java": ["target/", "build/", "*.class", "*.jar"],
    "c_cpp": ["build/", "*.o", "*.a", "*.so", "*.exe", "Debug/", "Release/"],
    "csharp": ["bin/", "obj/", "packages/", "*.suo", "*.user", ".vs/"],
    "php": ["vendor/", "var/", "public/bundles/"],
    "ruby": ["vendor/", "tmp/", "log/"],
    # Fallback for unknown project types
    "default": [],
}

class ProjectInitializer:
    """
    Project initialization with auto-detection of project type and smart defaults
    """

    def __init__(self, project_path: str, data_dir: str):
        """
        Initialize project detector
        
        Args:
            project_path: Path to the project directory
            data_dir: Directory to store configuration and state
        """
        self.project_path = Path(project_path)
        self.data_dir = Path(data_dir)
        self.config_file = self.data_dir / "config.json"
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Default settings
        self.detected_project_types = []
        self.primary_project_type = "default"
        self.custom_ignore_patterns = []
        self.embedding_model = DEFAULT_EMBEDDING_MODELS["default"]
        self.model_config = DEFAULT_MODEL_CONFIGS["default"].copy()

    def detect_project_types(self) -> List[str]:
        """
        Detect project types based on file patterns
        
        Returns:
            List of detected project types
        """
        detected_types = []
        
        logger.info(f"Detecting project types in: {self.project_path}")
        
        # Check for VCS directories
        vcs_dirs = [".git", ".svn", ".hg"]
        has_vcs = any(os.path.isdir(self.project_path / vcs_dir) for vcs_dir in vcs_dirs)
        
        if has_vcs:
            logger.info(f"Detected version control system in project")
        
        # Scan root directory first for project markers
        root_files = [f.name for f in self.project_path.glob("*") if f.is_file()]
        
        # Score project types based on pattern matches
        type_scores = {project_type: 0 for project_type in PROJECT_TYPE_PATTERNS.keys()}
        
        # Check root files against patterns
        for project_type, patterns in PROJECT_TYPE_PATTERNS.items():
            for pattern in patterns:
                # Direct file match (highest score)
                if any(f == pattern for f in root_files):
                    type_scores[project_type] += 10
                    continue
                
                # Check for pattern match in root
                for file in root_files:
                    if fnmatch.fnmatch(file, pattern):
                        type_scores[project_type] += 8
        
        # Walk directory for deeper pattern matches (limited depth for performance)
        max_depth = 3
        current_depth = 0
        for root, dirs, files in os.walk(self.project_path):
            # Skip ignored directories
            if any(ignored in root for ignored in [".git", "node_modules", "__pycache__", "venv"]):
                continue
                
            # Calculate current depth
            rel_path = os.path.relpath(root, self.project_path)
            current_depth = 0 if rel_path == "." else rel_path.count(os.sep) + 1
            
            # Skip if we've gone too deep
            if current_depth > max_depth:
                continue
            
            # Check all files in this directory against patterns
            for file in files:
                file_path = os.path.join(root, file)
                rel_file_path = os.path.relpath(file_path, self.project_path)
                
                for project_type, patterns in PROJECT_TYPE_PATTERNS.items():
                    for pattern in patterns:
                        # Direct file name match
                        if file == pattern:
                            # Score decreases with depth
                            type_scores[project_type] += max(5, 10 - current_depth * 2)
                            continue
                            
                        # Extension match
                        if pattern.startswith(".") and file.endswith(pattern):
                            # Score extension matches based on frequency and depth
                            type_scores[project_type] += max(1, 3 - current_depth)
                            continue
                            
                        # Pattern match
                        if fnmatch.fnmatch(file, pattern):
                            type_scores[project_type] += max(1, 3 - current_depth)
        
        # Sort project types by score and filter those with score > 0
        sorted_types = sorted(
            [(project_type, score) for project_type, score in type_scores.items() if score > 0],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Log detection results
        logger.info(f"Project type detection scores: {dict(sorted_types)}")
        
        # Return detected types (all with score > 0)
        detected_types = [project_type for project_type, score in sorted_types]
        
        if not detected_types:
            logger.warning("No specific project type detected, using default configuration")
            detected_types = ["default"]
            
        self.detected_project_types = detected_types
        self.primary_project_type = detected_types[0] if detected_types else "default"
        
        return detected_types

    def detect_ignore_patterns(self) -> List[str]:
        """
        Detect project-specific ignore patterns from .gitignore, etc.
        
        Returns:
            List of additional ignore patterns
        """
        ignore_patterns = []
        
        # Check .gitignore
        gitignore_path = self.project_path / ".gitignore"
        if gitignore_path.exists():
            logger.info(f"Found .gitignore at {gitignore_path}")
            try:
                with open(gitignore_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        # Skip comments and empty lines
                        if line and not line.startswith("#"):
                            # Convert .gitignore patterns to glob patterns
                            # Remove negation as it's handled differently
                            if line.startswith("!"):
                                continue
                            # Handle directory markers (trailing slash)
                            if line.endswith("/"):
                                line = f"{line}**"
                            ignore_patterns.append(line)
                logger.info(f"Added {len(ignore_patterns)} patterns from .gitignore")
            except Exception as e:
                logger.warning(f"Error reading .gitignore: {e!s}")
        
        # Check .dockerignore
        dockerignore_path = self.project_path / ".dockerignore"
        if dockerignore_path.exists():
            logger.info(f"Found .dockerignore at {dockerignore_path}")
            try:
                with open(dockerignore_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        # Skip comments and empty lines
                        if line and not line.startswith("#"):
                            # Skip negation patterns
                            if line.startswith("!"):
                                continue
                            ignore_patterns.append(line)
                logger.info(f"Added patterns from .dockerignore")
            except Exception as e:
                logger.warning(f"Error reading .dockerignore: {e!s}")
        
        # Add default ignore patterns for the detected project type
        for project_type in self.detected_project_types:
            if project_type in DEFAULT_IGNORE_PATTERNS:
                type_patterns = DEFAULT_IGNORE_PATTERNS[project_type]
                ignore_patterns.extend(type_patterns)
                logger.info(f"Added {len(type_patterns)} default ignore patterns for {project_type}")
        
        # Deduplicate patterns
        self.custom_ignore_patterns = list(set(ignore_patterns))
        return self.custom_ignore_patterns

    def select_embedding_model(self) -> Tuple[str, Dict[str, Any]]:
        """
        Select appropriate embedding model based on project type
        
        Returns:
            Tuple of (model_name, model_config)
        """
        # First check environment variable for FAST_STARTUP mode
        fast_startup = os.environ.get("FAST_STARTUP", "false").lower() == "true"
        
        # Check if embedding model is explicitly set in environment
        env_model = os.environ.get("EMBEDDING_MODEL")
        if env_model:
            logger.info(f"Using embedding model from environment: {env_model}")
            self.embedding_model = env_model
            # Keep default config but allow overrides from config file
            if self.primary_project_type in DEFAULT_MODEL_CONFIGS:
                self.model_config = DEFAULT_MODEL_CONFIGS[self.primary_project_type].copy()
            else:
                self.model_config = DEFAULT_MODEL_CONFIGS["default"].copy()
                
        # Check if we have a custom config file
        elif self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    if "embedding_model" in config:
                        self.embedding_model = config["embedding_model"]
                        logger.info(f"Using custom embedding model from config: {self.embedding_model}")
                    if "model_config" in config:
                        self.model_config.update(config["model_config"])
                        logger.info(f"Using custom model configuration from config")
                    return self.embedding_model, self.model_config
            except Exception as e:
                logger.warning(f"Error reading config file: {e!s}")
        
        # If fast startup is requested, use the smallest model
        elif fast_startup:
            logger.info("FAST_STARTUP is enabled, using lightweight embedding model")
            self.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"  # Smallest model ~90MB
            self.model_config = DEFAULT_MODEL_CONFIGS["default"].copy()
            
        # Otherwise use default model for the primary project type
        elif self.primary_project_type in DEFAULT_EMBEDDING_MODELS:
            self.embedding_model = DEFAULT_EMBEDDING_MODELS[self.primary_project_type]
            self.model_config = DEFAULT_MODEL_CONFIGS[self.primary_project_type].copy()
        else:
            self.embedding_model = DEFAULT_EMBEDDING_MODELS["default"]
            self.model_config = DEFAULT_MODEL_CONFIGS["default"].copy()
        
        # Set device to auto-detect by default
        if self.model_config.get("device") == "auto":
            try:
                # Try to detect GPU
                import torch
                if torch.cuda.is_available():
                    self.model_config["device"] = "cuda"
                    logger.info("CUDA detected, using GPU for embeddings")
                elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                    self.model_config["device"] = "mps"
                    logger.info("MPS detected, using Apple Silicon GPU for embeddings")
                else:
                    self.model_config["device"] = "cpu"
                    logger.info("No GPU detected, using CPU for embeddings")
            except ImportError:
                # If torch is not available, default to CPU
                self.model_config["device"] = "cpu"
                logger.info("PyTorch not available, defaulting to CPU for embeddings")
        
        logger.info(f"Selected embedding model: {self.embedding_model}")
        logger.info(f"Model configuration: {self.model_config}")
        
        return self.embedding_model, self.model_config

    def generate_config_file(self):
        """Generate configuration file with defaults"""
        # Only generate if it doesn't already exist
        if not self.config_file.exists():
            try:
                config = {
                    "project_type": self.primary_project_type,
                    "detected_project_types": self.detected_project_types,
                    "embedding_model": self.embedding_model,
                    "model_config": self.model_config,
                    "custom_ignore_patterns": self.custom_ignore_patterns,
                    "auto_generated": True,
                    "version": "0.1.0"
                }
                
                with open(self.config_file, "w") as f:
                    json.dump(config, f, indent=2)
                
                logger.info(f"Generated configuration file: {self.config_file}")
            except Exception as e:
                logger.error(f"Error generating configuration file: {e!s}")
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    logger.info(f"Loaded configuration from {self.config_file}")
                    return config
            except Exception as e:
                logger.error(f"Error loading configuration file: {e!s}")
        return {}
    
    def get_ignore_patterns(self) -> List[str]:
        """Get combined ignore patterns"""
        global_ignore_patterns = [
            ".git", "node_modules", "__pycache__", "*.pyc", "*.pyo", 
            ".DS_Store", ".idea", ".vscode"
        ]
        
        # Combine global patterns with custom patterns
        return list(set(global_ignore_patterns + self.custom_ignore_patterns))
    
    def initialize_project(self) -> Dict[str, Any]:
        """
        Initialize project with auto-detection and configuration
        
        Returns:
            Dictionary with project configuration
        """
        logger.info(f"Initializing project at: {self.project_path}")
        
        # Step 1: Detect project types
        project_types = self.detect_project_types()
        logger.info(f"Detected project types: {project_types}")
        
        # Step 2: Detect ignore patterns
        ignore_patterns = self.detect_ignore_patterns()
        logger.info(f"Detected {len(ignore_patterns)} ignore patterns")
        
        # Step 3: Select embedding model
        embedding_model, model_config = self.select_embedding_model()
        
        # Step 4: Generate config file
        self.generate_config_file()
        
        # Return the configuration
        return {
            "project_types": project_types,
            "primary_project_type": self.primary_project_type,
            "embedding_model": embedding_model,
            "model_config": model_config,
            "ignore_patterns": self.get_ignore_patterns()
        }