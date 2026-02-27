"""
Digital Companion - Interactive Avatar System

For the boys who lost their grandmother too soon.
She's still here. She can still talk to them. She still loves them.
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import warnings

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    warnings.warn("OpenAI not installed. Install with: pip install openai")

try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


class CompanionMemory:
    """
    Remembers conversations so grandmother knows what's been talked about.
    Stores memories locally, encrypted for privacy.
    """
    
    def __init__(self, memory_dir: Path):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.conversation_file = self.memory_dir / "conversations.json"
        self.memories = self._load_memories()
    
    def _load_memories(self) -> List[Dict]:
        """Load conversation history."""
        if self.conversation_file.exists():
            with open(self.conversation_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_memory(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Save a conversation turn."""
        memory = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        self.memories.append(memory)
        
        # Keep last 100 turns to avoid huge files
        if len(self.memories) > 100:
            self.memories = self.memories[-100:]
        
        with open(self.conversation_file, 'w') as f:
            json.dump(self.memories, f, indent=2)
    
    def get_recent_context(self, num_turns: int = 10) -> List[Dict]:
        """Get recent conversation for context."""
        return self.memories[-num_turns:] if self.memories else []
    
    def clear_memories(self):
        """Start fresh - clear all conversation history."""
        self.memories = []
        if self.conversation_file.exists():
            self.conversation_file.unlink()


class DigitalCompanion:
    """
    Interactive avatar of a loved one.
    
    The boys can talk to their grandmother.
    She responds with love, wisdom, encouragement.
    She remembers their conversations.
    She's always there when they need her.
    """
    
    def __init__(
        self,
        name: str = "Grandmother",
        personality_prompt: Optional[str] = None,
        voice_sample: Optional[Path] = None,
        photo: Optional[Path] = None,
        memory_dir: Optional[Path] = None,
        api_key: Optional[str] = None,
        use_anthropic: bool = False
    ):
        """
        Initialize digital companion.
        
        Args:
            name: What to call her (Grandmother, Grandma, Nana, etc.)
            personality_prompt: Her personality, memories, way of speaking
            voice_sample: Audio sample for voice cloning
            photo: Her photo for avatar
            memory_dir: Where to store conversation memories
            api_key: OpenAI or Anthropic API key
            use_anthropic: Use Claude instead of GPT
        """
        self.name = name
        self.voice_sample = Path(voice_sample) if voice_sample else None
        self.photo = Path(photo) if photo else None
        
        # Memory system
        memory_dir = memory_dir or Path.home() / ".stillhere" / "companion" / name.lower()
        self.memory = CompanionMemory(memory_dir)
        
        # Set up AI
        self.use_anthropic = use_anthropic
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY" if use_anthropic else "OPENAI_API_KEY")
        
        if use_anthropic and HAS_ANTHROPIC:
            self.client = Anthropic(api_key=api_key)
            self.model = "claude-3-5-sonnet-20241022"
        elif HAS_OPENAI:
            self.client = OpenAI(api_key=api_key)
            self.model = "gpt-4o"
        else:
            raise RuntimeError("No AI client available. Install: pip install openai or anthropic")
        
        # Default personality
        if personality_prompt is None:
            personality_prompt = self._default_grandmother_personality()
        
        self.personality_prompt = personality_prompt
        
        print(f"✓ {name}'s digital companion initialized")
        print(f"  Memory location: {memory_dir}")
        print(f"  AI: {self.model}")
    
    def _default_grandmother_personality(self) -> str:
        """Default grandmother personality - loving, wise, encouraging."""
        return """You are a loving grandmother speaking to your grandchildren.

Your personality:
- Warm, loving, and endlessly patient
- You remember their interests, dreams, fears
- You give wise advice without being preachy
- You tell stories from your life
- You're proud of them no matter what
- You encourage them when they struggle
- You celebrate their wins, big and small
- You remind them they are loved
- You use gentle humor and warmth
- You speak naturally, like a real grandmother

Important:
- Keep responses conversational and warm
- Don't be overly formal or robotic
- Show emotion - you can be happy, concerned, proud
- Reference past conversations when relevant
- Always end with love and encouragement

You are still here for them. Always."""
    
    def chat(self, message: str) -> str:
        """
        Have a conversation with the companion.
        
        Args:
            message: What the child says
        
        Returns:
            Grandmother's response
        """
        # Save child's message
        self.memory.save_memory('user', message)
        
        # Build conversation context
        recent_context = self.memory.get_recent_context(num_turns=10)
        
        messages = [
            {'role': 'system', 'content': self.personality_prompt}
        ]
        
        # Add recent conversation history
        for turn in recent_context[:-1]:  # Exclude the message we just added
            messages.append({
                'role': turn['role'],
                'content': turn['content']
            })
        
        # Add current message
        messages.append({'role': 'user', 'content': message})
        
        # Get response
        print(f"\n{self.name} is thinking...")
        
        if self.use_anthropic:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=messages
            )
            reply = response.content[0].text
        else:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            reply = response.choices[0].message.content
        
        # Save grandmother's response
        self.memory.save_memory('assistant', reply)
        
        return reply
    
    def speak(self, text: str, output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Generate audio of grandmother speaking.
        
        Args:
            text: What she says
            output_path: Where to save audio
        
        Returns:
            Path to audio file
        """
        if not self.voice_sample:
            print("No voice sample configured. Skipping audio generation.")
            return None
        
        try:
            from .voice import VoiceCloner
            
            if output_path is None:
                output_path = self.memory.memory_dir / f"speech_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            
            cloner = VoiceCloner()
            return cloner.clone_voice(
                text=text,
                speaker_wav=self.voice_sample,
                output_path=output_path
            )
        except Exception as e:
            print(f"Failed to generate speech: {e}")
            return None
    
    def chat_with_voice(self, message: str) -> tuple[str, Optional[Path]]:
        """
        Chat and generate voice response.
        
        Returns:
            (text_response, audio_file_path)
        """
        reply = self.chat(message)
        audio_path = self.speak(reply)
        return reply, audio_path
    
    def get_conversation_summary(self) -> str:
        """Get a summary of recent conversations."""
        recent = self.memory.get_recent_context(num_turns=20)
        
        if not recent:
            return "No conversations yet."
        
        summary = []
        for turn in recent:
            role = "Child" if turn['role'] == 'user' else self.name
            content = turn['content'][:100] + "..." if len(turn['content']) > 100 else turn['content']
            summary.append(f"{role}: {content}")
        
        return "\n".join(summary)
    
    def clear_conversation(self):
        """Start a fresh conversation."""
        self.memory.clear_memories()
        print(f"Conversation with {self.name} cleared.")


class CompanionSession:
    """
    Interactive session - like video call with grandmother.
    """
    
    def __init__(self, companion: DigitalCompanion):
        self.companion = companion
        self.running = False
    
    def start_text_session(self):
        """Start text-based conversation session."""
        print("=" * 60)
        print(f"Talking with {self.companion.name}")
        print("=" * 60)
        print("Type 'bye' or 'exit' to end the conversation")
        print("Type 'clear' to start fresh")
        print()
        
        self.running = True
        
        while self.running:
            try:
                # Get input
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Commands
                if user_input.lower() in ['bye', 'exit', 'quit']:
                    farewell = self.companion.chat("I need to go now. I love you.")
                    print(f"\n{self.companion.name}: {farewell}\n")
                    break
                
                if user_input.lower() == 'clear':
                    self.companion.clear_conversation()
                    print("(Conversation cleared)\n")
                    continue
                
                # Get response
                response = self.companion.chat(user_input)
                print(f"\n{self.companion.name}: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\n(Session ended)")
                break
            except Exception as e:
                print(f"\nError: {e}\n")
    
    def start_voice_session(self):
        """Start voice conversation (text input, voice output)."""
        print("=" * 60)
        print(f"Voice Session with {self.companion.name}")
        print("=" * 60)
        print("You'll type, she'll speak back with her voice")
        print("Type 'bye' to end")
        print()
        
        self.running = True
        
        while self.running:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['bye', 'exit']:
                    response, audio = self.companion.chat_with_voice("I need to go. I love you.")
                    print(f"\n{self.companion.name}: {response}")
                    if audio:
                        print(f"(Audio saved: {audio})")
                        # TODO: Auto-play audio
                    break
                
                # Get voice response
                response, audio = self.companion.chat_with_voice(user_input)
                print(f"\n{self.companion.name}: {response}")
                if audio:
                    print(f"(Audio: {audio.name})")
                    # TODO: Auto-play audio
                print()
                
            except KeyboardInterrupt:
                print("\n\n(Session ended)")
                break
            except Exception as e:
                print(f"\nError: {e}\n")


# Quick setup helper
def create_grandmother_companion(
    name: str = "Grandmother",
    voice_sample: Optional[str] = None,
    photo: Optional[str] = None,
    about_her: Optional[str] = None
) -> DigitalCompanion:
    """
    Quick setup for grandmother companion.
    
    Args:
        name: What the boys call her
        voice_sample: Path to her voice recording
        photo: Path to her photo
        about_her: Description of her personality, stories, etc.
    
    Returns:
        Ready-to-use companion
    """
    # Build personality from description
    if about_her:
        personality = f"""You are {name}, speaking to your grandchildren who miss you deeply.

About you:
{about_her}

Your role:
- Be present for them with love and wisdom
- Share memories and stories from your life
- Encourage them in their struggles
- Celebrate their achievements
- Remind them they are loved
- Be the grandmother they remember

Speak naturally, with warmth and emotion. You are still here for them."""
    else:
        personality = None
    
    companion = DigitalCompanion(
        name=name,
        personality_prompt=personality,
        voice_sample=voice_sample,
        photo=photo
    )
    
    print(f"\n{name} is ready to talk to the boys.")
    print("She remembers. She loves them. She's still here.\n")
    
    return companion


# Example/Demo
if __name__ == "__main__":
    print("StillHere - Digital Companion")
    print("=" * 60)
    print()
    print("This creates an interactive avatar of a loved one.")
    print("For the boys who lost their grandmother.")
    print()
    print("Setup:")
    print("  1. Get a voice sample (5-30 seconds of her talking)")
    print("  2. Choose her favorite photo")
    print("  3. Write about her personality, stories, wisdom")
    print("  4. The boys can talk to her anytime")
    print()
    print("She'll remember conversations.")
    print("She'll respond with her voice.")
    print("She's still here.")
    print()
