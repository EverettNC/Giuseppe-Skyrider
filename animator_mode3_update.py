"""
Update for animator.py to integrate Mode 3 (Voice Avatar)

This adds the complete implementation to the existing animate_with_voice method.
"""

# Code to add to animator.py:

def animate_with_voice_UPDATED(
    self,
    photo: Union[str, Path, np.ndarray],
    text: Optional[str] = None,
    voice_sample: Optional[Union[str, Path]] = None,
    audio_file: Optional[Union[str, Path]] = None,
    quality: str = "high",
    fps: int = 30,
    output_path: Optional[Union[str, Path]] = None,
    language: str = "en"
) -> Path:
    """
    Mode 3: Create speaking avatar with voice cloning and lip sync.
    
    This is the complete memorial experience - your aunt's photo speaks
    with her own voice, with realistic lip movements.
    
    Args:
        photo: Photo to animate
        text: What to say (requires voice_sample for cloning)
        voice_sample: Audio sample to clone voice from
        audio_file: Pre-recorded audio (bypasses voice cloning)
        quality: Animation quality
        fps: Frames per second
        output_path: Where to save video
        language: Language for TTS
    
    Returns:
        Path to final speaking avatar video
    """
    from .lipsync import AvatarBuilder
    from .voice import VoiceCloner
    
    if output_path is None:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(f"speaking_avatar_{timestamp}.mp4")
    else:
        output_path = Path(output_path)
    
    # Validate inputs
    if audio_file is None and (text is None or voice_sample is None):
        raise ValueError(
            "Must provide either:\n"
            "  - audio_file (pre-recorded), OR\n"
            "  - text + voice_sample (for voice cloning)"
        )
    
    print("=" * 70)
    print("MODE 3: SPEAKING AVATAR WITH VOICE CLONING")
    print("=" * 70)
    print()
    
    # Build the avatar
    avatar_builder = AvatarBuilder()
    
    if audio_file:
        # Use pre-recorded audio
        print("Using pre-recorded audio...")
        from .lipsync import LipSyncer
        lip_syncer = LipSyncer()
        
        result = lip_syncer.sync_lips_to_audio(
            face_image=photo,
            audio_file=audio_file,
            output_path=output_path,
            fps=fps,
            quality=quality
        )
    else:
        # Clone voice and generate speech
        print("Cloning voice and generating speech...")
        result = avatar_builder.create_speaking_avatar(
            photo_path=photo,
            voice_sample_path=voice_sample,
            text_to_speak=text,
            output_path=output_path,
            language=language
        )
    
    print()
    print("=" * 70)
    print(f"✓ Speaking avatar created: {result}")
    print("=" * 70)
    
    return result
