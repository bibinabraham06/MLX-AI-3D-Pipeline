"""Configuration management for AI Workspace"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import validator
import yaml
import os


class AIWorkspaceConfig(BaseSettings):
    """Main configuration class"""

    # Paths
    workspace_root: Path = Path.home() / "ai-workspace"
    models_dir: Path = workspace_root / "models"
    projects_dir: Path = workspace_root / "projects"
    cache_dir: Path = workspace_root / "cache"
    logs_dir: Path = workspace_root / "logs"

    # API Settings
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_workers: int = 1

    # Hardware Settings
    device: str = "auto"  # auto, mps, cuda, cpu
    max_memory_gb: Optional[int] = None
    enable_mlx: bool = True
    enable_mps: bool = True

    # Model Settings
    default_sd_model: str = "runwayml/stable-diffusion-v1-5"
    default_llm_model: str = "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"
    model_cache_size: int = 3  # Number of models to keep loaded

    # Generation Settings
    default_image_size: int = 512
    default_steps: int = 20
    default_guidance_scale: float = 7.5
    max_batch_size: int = 4

    # Chat Settings
    enable_chat: bool = True
    chat_model: Optional[str] = None
    max_chat_history: int = 100
    chat_temperature: float = 0.7

    # Security
    api_key: Optional[str] = None
    allowed_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Features
    enable_3d: bool = True
    enable_web_ui: bool = True
    enable_auto_save: bool = True

    class Config:
        env_file = ".env"
        env_prefix = "AI_WORKSPACE_"

    @validator("workspace_root", pre=True)
    def expand_path(cls, v):
        return Path(v).expanduser().absolute()

    def create_directories(self):
        """Create necessary directories"""
        dirs = [
            self.workspace_root,
            self.models_dir,
            self.projects_dir,
            self.cache_dir,
            self.logs_dir,
        ]

        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

    def detect_hardware(self) -> Dict[str, Any]:
        """Auto-detect hardware capabilities"""
        import platform

        hardware_info = {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
        }

        # Check for Apple Silicon
        if platform.machine() == "arm64" and platform.system() == "Darwin":
            hardware_info["apple_silicon"] = True
            hardware_info["recommended_device"] = "mps"
        else:
            hardware_info["apple_silicon"] = False

        # Check for CUDA
        try:
            import torch
            hardware_info["cuda_available"] = torch.cuda.is_available()
            hardware_info["mps_available"] = torch.backends.mps.is_available()
        except ImportError:
            hardware_info["cuda_available"] = False
            hardware_info["mps_available"] = False

        # Check for MLX
        try:
            import mlx.core as mx
            hardware_info["mlx_available"] = True
        except ImportError:
            hardware_info["mlx_available"] = False

        return hardware_info

    def get_optimal_device(self) -> str:
        """Get the optimal device for this hardware"""
        if self.device != "auto":
            return self.device

        hardware = self.detect_hardware()

        if hardware.get("mlx_available") and self.enable_mlx:
            return "mlx"
        elif hardware.get("mps_available") and self.enable_mps:
            return "mps"
        elif hardware.get("cuda_available"):
            return "cuda"
        else:
            return "cpu"

    @classmethod
    def load_from_file(cls, config_path: Path) -> "AIWorkspaceConfig":
        """Load configuration from YAML file"""
        if config_path.exists():
            with open(config_path) as f:
                config_data = yaml.safe_load(f)
            return cls(**config_data)
        return cls()

    def save_to_file(self, config_path: Path):
        """Save configuration to YAML file"""
        config_data = self.dict()
        # Convert Path objects to strings for YAML serialization
        for key, value in config_data.items():
            if isinstance(value, Path):
                config_data[key] = str(value)

        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)


# Global config instance
config = AIWorkspaceConfig()


def get_config() -> AIWorkspaceConfig:
    """Get the global configuration instance"""
    return config


def init_config(config_path: Optional[Path] = None) -> AIWorkspaceConfig:
    """Initialize configuration"""
    global config

    if config_path is None:
        config_path = Path.cwd() / "config.yaml"

    config = AIWorkspaceConfig.load_from_file(config_path)
    config.create_directories()

    return config