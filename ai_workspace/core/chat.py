"""Conversational AI Engine - Integration with MLX LLMs"""

from typing import Optional, List, Dict, Any, Union, AsyncGenerator
from pathlib import Path
import asyncio
import time
import json
from dataclasses import dataclass
from enum import Enum

from ..config import get_config


class MessageRole(Enum):
    """Chat message roles"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class ChatMessage:
    """Chat message"""
    role: MessageRole
    content: str
    timestamp: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ChatSession:
    """Chat session state"""
    session_id: str
    messages: List[ChatMessage]
    model: str
    settings: Dict[str, Any]
    created_at: float
    last_activity: float


@dataclass
class CodeContext:
    """Code context for AI assistance"""
    file_path: Optional[Path]
    content: str
    language: str
    cursor_position: Optional[int]
    selection: Optional[str]


class ChatEngine:
    """Conversational AI engine with code understanding"""

    def __init__(self):
        self.config = get_config()
        self.active_sessions: Dict[str, ChatSession] = {}
        self.current_model = None
        self.mlx_model = None

    async def initialize(self):
        """Initialize the chat engine"""
        if self.config.enable_chat:
            await self._load_default_model()

    async def _load_default_model(self):
        """Load the default chat model"""
        model_name = self.config.chat_model or self.config.default_llm_model

        try:
            if self.config.enable_mlx and self._is_mlx_available():
                await self._load_mlx_model(model_name)
            else:
                await self._load_transformers_model(model_name)

            self.current_model = model_name
            print(f"✓ Loaded chat model: {model_name}")

        except Exception as e:
            print(f"✗ Failed to load chat model: {e}")

    def _is_mlx_available(self) -> bool:
        """Check if MLX is available"""
        try:
            import mlx.core as mx
            return True
        except ImportError:
            return False

    async def _load_mlx_model(self, model_name: str):
        """Load MLX-based language model"""
        try:
            import mlx_lm

            # Load model in executor to avoid blocking
            def load_model():
                model, tokenizer = mlx_lm.load(model_name)
                return model, tokenizer

            loop = asyncio.get_event_loop()
            self.mlx_model = await loop.run_in_executor(None, load_model)

        except ImportError:
            raise RuntimeError("MLX-LM not installed. Install with: pip install mlx-lm")

    async def _load_transformers_model(self, model_name: str):
        """Load Transformers-based model (fallback)"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch

            device = self.config.get_optimal_device()
            if device == "mlx":
                device = "mps" if torch.backends.mps.is_available() else "cpu"

            def load_model():
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16 if device in ["mps", "cuda"] else torch.float32,
                    device_map="auto" if device == "cuda" else None
                )
                if device != "cuda":
                    model = model.to(device)
                return model, tokenizer

            loop = asyncio.get_event_loop()
            self.mlx_model = await loop.run_in_executor(None, load_model)

        except ImportError:
            raise RuntimeError("Transformers not installed. Install with: pip install transformers")

    async def create_session(self, model: Optional[str] = None) -> ChatSession:
        """Create a new chat session"""
        import uuid

        session_id = str(uuid.uuid4())
        session = ChatSession(
            session_id=session_id,
            messages=[],
            model=model or self.current_model,
            settings={
                "temperature": self.config.chat_temperature,
                "max_tokens": 2048,
                "top_p": 0.9,
            },
            created_at=time.time(),
            last_activity=time.time()
        )

        # Add system message for AI workspace context
        system_message = ChatMessage(
            role=MessageRole.SYSTEM,
            content=self._get_system_prompt(),
            timestamp=time.time()
        )
        session.messages.append(system_message)

        self.active_sessions[session_id] = session
        return session

    def _get_system_prompt(self) -> str:
        """Get system prompt for AI workspace context"""
        return """You are Claude Code, an AI assistant integrated into an AI Workspace that combines:

1. **Code Editor**: You can read, write, and analyze code in multiple languages
2. **AI Image Generation**: You can create images using Stable Diffusion
3. **3D Generation**: You can create depth maps, normal maps, and 3D assets
4. **Project Management**: You can help organize and manage development projects

**Your Capabilities:**
- Write and debug code in Python, JavaScript, TypeScript, and more
- Generate textures, concepts, and visual assets
- Create 3D-ready assets (depth maps, normal maps)
- Search and analyze codebases
- Provide technical explanations and tutorials
- Help with AI/ML workflows and automation

**Guidelines:**
- Be concise and practical in your responses
- Offer code examples when helpful
- Suggest visual or 3D assets when relevant to the project
- Ask clarifying questions when context is needed
- Integrate multiple workspace features when appropriate

You are currently assisting with development in an AI-powered workspace. How can I help you today?"""

    async def chat(
        self,
        session_id: str,
        message: str,
        code_context: Optional[CodeContext] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Chat with AI assistant"""

        if session_id not in self.active_sessions:
            raise ValueError(f"Session not found: {session_id}")

        session = self.active_sessions[session_id]

        # Add user message
        user_message = ChatMessage(
            role=MessageRole.USER,
            content=message,
            timestamp=time.time(),
            metadata={"code_context": code_context.__dict__ if code_context else None}
        )
        session.messages.append(user_message)

        yield {"status": "thinking", "progress": 0.1}

        try:
            # Generate response
            if self.mlx_model and self._is_mlx_available():
                async for chunk in self._generate_mlx_response(session, message, code_context):
                    yield chunk
            else:
                async for chunk in self._generate_transformers_response(session, message, code_context):
                    yield chunk

            session.last_activity = time.time()

        except Exception as e:
            yield {"status": "error", "error": str(e)}

    async def _generate_mlx_response(
        self,
        session: ChatSession,
        message: str,
        code_context: Optional[CodeContext]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate response using MLX"""
        try:
            import mlx_lm

            model, tokenizer = self.mlx_model

            # Prepare conversation history
            conversation = self._format_conversation(session, message, code_context)

            yield {"status": "generating", "progress": 0.3}

            # Generate response
            def generate():
                response = mlx_lm.generate(
                    model,
                    tokenizer,
                    prompt=conversation,
                    max_tokens=session.settings["max_tokens"],
                    temp=session.settings["temperature"],
                )
                return response

            loop = asyncio.get_event_loop()
            response_text = await loop.run_in_executor(None, generate)

            # Add assistant message
            assistant_message = ChatMessage(
                role=MessageRole.ASSISTANT,
                content=response_text,
                timestamp=time.time()
            )
            session.messages.append(assistant_message)

            yield {
                "status": "complete",
                "progress": 1.0,
                "response": response_text,
                "message": assistant_message
            }

        except Exception as e:
            yield {"status": "error", "error": f"MLX generation failed: {e}"}

    async def _generate_transformers_response(
        self,
        session: ChatSession,
        message: str,
        code_context: Optional[CodeContext]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate response using Transformers (fallback)"""
        try:
            import torch

            model, tokenizer = self.mlx_model

            # Prepare conversation
            conversation = self._format_conversation(session, message, code_context)

            yield {"status": "generating", "progress": 0.3}

            def generate():
                inputs = tokenizer.encode(conversation, return_tensors="pt")
                device = next(model.parameters()).device
                inputs = inputs.to(device)

                with torch.no_grad():
                    outputs = model.generate(
                        inputs,
                        max_new_tokens=session.settings["max_tokens"],
                        temperature=session.settings["temperature"],
                        top_p=session.settings.get("top_p", 0.9),
                        do_sample=True,
                        pad_token_id=tokenizer.eos_token_id
                    )

                response = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
                return response.strip()

            loop = asyncio.get_event_loop()
            response_text = await loop.run_in_executor(None, generate)

            # Add assistant message
            assistant_message = ChatMessage(
                role=MessageRole.ASSISTANT,
                content=response_text,
                timestamp=time.time()
            )
            session.messages.append(assistant_message)

            yield {
                "status": "complete",
                "progress": 1.0,
                "response": response_text,
                "message": assistant_message
            }

        except Exception as e:
            yield {"status": "error", "error": f"Transformers generation failed: {e}"}

    def _format_conversation(
        self,
        session: ChatSession,
        current_message: str,
        code_context: Optional[CodeContext]
    ) -> str:
        """Format conversation for model input"""
        conversation = []

        # Add recent messages (keep within context window)
        recent_messages = session.messages[-10:]  # Last 10 messages

        for msg in recent_messages:
            if msg.role == MessageRole.SYSTEM:
                conversation.append(f"System: {msg.content}")
            elif msg.role == MessageRole.USER:
                conversation.append(f"User: {msg.content}")
            elif msg.role == MessageRole.ASSISTANT:
                conversation.append(f"Assistant: {msg.content}")

        # Add code context if provided
        if code_context:
            context_info = []
            if code_context.file_path:
                context_info.append(f"File: {code_context.file_path}")
            if code_context.language:
                context_info.append(f"Language: {code_context.language}")
            if code_context.selection:
                context_info.append(f"Selected: {code_context.selection}")

            context_str = " | ".join(context_info)
            conversation.append(f"Context: {context_str}")

            if code_context.content:
                conversation.append(f"Code:\n```{code_context.language}\n{code_context.content}\n```")

        # Add current message
        conversation.append(f"User: {current_message}")
        conversation.append("Assistant:")

        return "\n".join(conversation)

    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get chat session by ID"""
        return self.active_sessions.get(session_id)

    async def clear_session(self, session_id: str):
        """Clear chat session history"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            # Keep only system message
            system_messages = [msg for msg in session.messages if msg.role == MessageRole.SYSTEM]
            session.messages = system_messages

    async def delete_session(self, session_id: str):
        """Delete chat session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]

    def get_available_models(self) -> List[str]:
        """Get list of available chat models"""
        return [
            "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit",
            "mlx-community/Mistral-7B-Instruct-v0.3-4bit",
            "mlx-community/CodeLlama-7B-Instruct-hf-4bit",
            "microsoft/DialoGPT-medium",  # Fallback for non-MLX
        ]

    async def cleanup(self):
        """Clean up resources"""
        if self.mlx_model:
            del self.mlx_model
            self.mlx_model = None

        self.active_sessions.clear()

        # Clear GPU memory
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            elif torch.backends.mps.is_available():
                torch.mps.empty_cache()
        except ImportError:
            pass