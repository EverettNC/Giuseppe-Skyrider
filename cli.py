"""
Simple command-line interface for ICanHearYou voice synthesis.

Usage:
    # Train a voice
    python cli.py train --name "my_voice" --audio data/raw/*.wav --tier premium
    
    # Synthesize speech
    python cli.py synthesize --voicepack my_voice.voicepack --text "Hello world" --emotion happy
    
    # Analyze audio tone
    python cli.py analyze --audio data/raw/sample.wav
"""

import argparse
from pathlib import Path
import sys
import json

from src import VoiceSynthesisOrchestrator, Tier, get_logger
from src.core.voicepack import VoicepackMetadata

logger = get_logger(__name__)


def train_command(args):
    """Train a new voice from audio files."""
    print(f"\n🎤 Training voice: {args.name}")
    print(f"Tier: {args.tier}")
    
    # Parse audio files
    audio_files = []
    for pattern in args.audio:
        audio_files.extend(Path().glob(pattern))
    
    if not audio_files:
        print("❌ No audio files found")
        return 1
    
    print(f"Found {len(audio_files)} audio files")
    
    # Initialize orchestrator
    tier = Tier(args.tier)
    orchestrator = VoiceSynthesisOrchestrator(tier=tier)
    
    # Create metadata
    metadata = VoicepackMetadata(
        name=args.name,
        tier=args.tier,
        gender=args.gender,
        age_range=args.age_range
    )
    
    # Train
    try:
        voicepack_path = orchestrator.train_voice(
            audio_files=audio_files,
            voice_name=args.name,
            metadata=metadata
        )
        
        print(f"\n✅ Voice training complete!")
        print(f"Voicepack: {voicepack_path}")
        return 0
        
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        logger.error(f"Training error", exc_info=True)
        return 1


def synthesize_command(args):
    """Synthesize speech from text."""
    print(f"\n🔊 Synthesizing speech")
    print(f"Voicepack: {args.voicepack}")
    print(f"Text: {args.text}")
    
    voicepack_path = Path(args.voicepack)
    if not voicepack_path.exists():
        print(f"❌ Voicepack not found: {voicepack_path}")
        return 1
    
    # Initialize orchestrator
    tier = Tier(args.tier)
    orchestrator = VoiceSynthesisOrchestrator(tier=tier)
    
    try:
        # Load voicepack
        orchestrator.load_voicepack(voicepack_path)
        
        # Synthesize
        result = orchestrator.synthesize(
            text=args.text,
            emotion=args.emotion,
            emotion_intensity=args.intensity,
            generate_lipsync=args.lipsync
        )
        
        # Save audio
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        import soundfile as sf
        sf.write(
            str(output_path),
            result["audio"],
            result["sample_rate"]
        )
        
        print(f"\n✅ Synthesis complete!")
        print(f"Output: {output_path}")
        print(f"Duration: {result['duration']:.2f}s")
        print(f"Emotion: {result['emotion']} ({result['emotion_intensity']:.0%})")
        
        # Save lip-sync if generated
        if result.get("lipsync_data"):
            lipsync_path = output_path.with_suffix('.lipsync.json')
            with open(lipsync_path, 'w') as f:
                json.dump(result["lipsync_data"], f, indent=2)
            print(f"Lip-sync: {lipsync_path}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Synthesis failed: {e}")
        logger.error("Synthesis error", exc_info=True)
        return 1


def analyze_command(args):
    """Analyze audio tone."""
    print(f"\n📊 Analyzing audio: {args.audio}")
    
    audio_path = Path(args.audio)
    if not audio_path.exists():
        print(f"❌ Audio file not found: {audio_path}")
        return 1
    
    try:
        orchestrator = VoiceSynthesisOrchestrator()
        result = orchestrator.analyze_audio_tone(audio_path)
        
        print(f"\n✅ Analysis complete!")
        print(f"\nToneScore™: {result['tone_score']}/100")
        print(f"Arousal: {result['arousal']}/100")
        print(f"Valence: {result['valence']}/100")
        print(f"Interpretation: {result['interpretation']}")
        
        print(f"\nEmotions:")
        for emotion, score in sorted(result['emotions'].items(), key=lambda x: -x[1]):
            print(f"  {emotion:12s}: {score:.2%}")
        
        print(f"\nPhysiological:")
        print(f"  Pitch: {result.get('pitch_mean', 0):.1f} Hz")
        print(f"  HNR: {result.get('hnr', 0):.1f} dB")
        print(f"  Jitter: {result.get('jitter', 0):.4f}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        logger.error("Analysis error", exc_info=True)
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ICanHearYou - Voice Synthesis for CHRISTMAN_MIND",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Train command
    train_parser = subparsers.add_parser('train', help='Train a new voice')
    train_parser.add_argument('--name', required=True, help='Voice name')
    train_parser.add_argument('--audio', nargs='+', required=True, help='Audio file patterns')
    train_parser.add_argument('--tier', default='basic', choices=['free', 'basic', 'premium', 'elite', 'ultra'])
    train_parser.add_argument('--gender', help='Gender (male/female/other)')
    train_parser.add_argument('--age-range', help='Age range (e.g. 30-40)')
    
    # Synthesize command
    synth_parser = subparsers.add_parser('synthesize', help='Synthesize speech')
    synth_parser.add_argument('--voicepack', required=True, help='Voicepack file')
    synth_parser.add_argument('--text', required=True, help='Text to synthesize')
    synth_parser.add_argument('--emotion', default='neutral', help='Emotion name')
    synth_parser.add_argument('--intensity', type=float, default=1.0, help='Emotion intensity (0-1)')
    synth_parser.add_argument('--tier', default='basic', choices=['free', 'basic', 'premium', 'elite', 'ultra'])
    synth_parser.add_argument('--output', default='output/synthesis.wav', help='Output audio file')
    synth_parser.add_argument('--lipsync', action='store_true', help='Generate lip-sync data')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze audio tone')
    analyze_parser.add_argument('--audio', required=True, help='Audio file to analyze')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Run command
    if args.command == 'train':
        return train_command(args)
    elif args.command == 'synthesize':
        return synthesize_command(args)
    elif args.command == 'analyze':
        return analyze_command(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
