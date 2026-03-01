import { create } from 'zustand'

export type GiovanniMood = 'swagger' | 'motivational' | 'sassy' | 'caring' | 'hype'

export type GiovanniState = 'idle' | 'speaking' | 'listening' | 'thinking' | 'celebrating'

export interface GiovanniMessage {
  id: string
  text: string
  mood: GiovanniMood
  timestamp: Date
  spoken: boolean
}

export interface FacsBlendshapes {
  browInnerUp: number;
  browDownLeft: number;
  browDownRight: number;
  eyeBlinkLeft: number;
  eyeBlinkRight: number;
  eyeWideLeft: number;
  eyeWideRight: number;
  jawOpen: number;
  mouthSmileLeft: number;
  mouthSmileRight: number;
  mouthFrownLeft: number;
  mouthFrownRight: number;
  cheekPuff: number;
}

interface GiovanniStore {
  // Avatar state
  mood: GiovanniMood
  state: GiovanniState
  isVisible: boolean
  position: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left'

  // Messages & interactions
  messages: GiovanniMessage[]
  currentMessage: GiovanniMessage | null

  // Voice settings
  voiceEnabled: boolean
  volume: number
  isListening: boolean

  // FACS Blendshape state (from Vortex payload)
  facsState: FacsBlendshapes | null

  // Actions
  setMood: (mood: GiovanniMood) => void
  setState: (state: GiovanniState) => void
  setVisible: (visible: boolean) => void
  setPosition: (position: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left') => void
  addMessage: (text: string, mood: GiovanniMood) => void
  speak: (text: string, mood: GiovanniMood) => Promise<void>
  clearMessages: () => void
  toggleVoice: () => void
  setVolume: (volume: number) => void
  toggleListening: () => void
  setFacsState: (facs: FacsBlendshapes) => void
}

export const useGiovanniStore = create<GiovanniStore>((set, get) => ({
  // Initial state
  mood: 'swagger',
  state: 'idle',
  isVisible: true,
  position: 'top-right',
  messages: [],
  currentMessage: null,
  voiceEnabled: true,
  volume: 0.8,
  isListening: false,
  facsState: null,

  // Actions
  setMood: (mood) => set({ mood }),

  setState: (state) => set({ state }),

  setVisible: (visible) => set({ isVisible: visible }),

  setPosition: (position) => set({ position }),

  addMessage: (text, mood) => {
    const message: GiovanniMessage = {
      id: `${Date.now()}-${Math.random()}`,
      text,
      mood,
      timestamp: new Date(),
      spoken: false
    }
    set((state) => ({
      messages: [...state.messages, message],
      currentMessage: message
    }))
  },

  speak: async (text, mood) => {
    const message: GiovanniMessage = {
      id: `${Date.now()}-${Math.random()}`,
      text,
      mood,
      timestamp: new Date(),
      spoken: false
    }

    set((state) => ({
      messages: [...state.messages, message],
      currentMessage: message,
      mood,
      state: 'speaking'
    }))

    // Trigger voice synthesis if enabled
    if (get().voiceEnabled) {
      try {
        const response = await fetch('http://localhost:8001/api/speak', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            text,
            tonescore: 80.0 // Default ToneScore parameter
          })
        });

        if (!response.ok) {
          throw new Error(`Speech synthesis failed: ${response.statusText}`);
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        audio.volume = get().volume;

        audio.onended = () => {
          set({ state: 'idle' })
          // Mark as spoken
          set((state) => ({
            messages: state.messages.map(m =>
              m.id === message.id ? { ...m, spoken: true } : m
            )
          }))
          URL.revokeObjectURL(url);
        };

        await audio.play();
      } catch (err) {
        console.error('Audio playback failed:', err);
        set({ state: 'idle' });
        // Fallback visible string
        const fallbackMsg: GiovanniMessage = {
          id: `error-${Date.now()}`,
          text: "[SILICON FAILURE]: Synthesis offline or keys missing. Please check .env",
          mood: 'sassy',
          timestamp: new Date(),
          spoken: true
        };
        set((state) => ({
          messages: [...state.messages, fallbackMsg],
          currentMessage: fallbackMsg
        }));
      }
    } else {
      // If voice is disabled, just show the message briefly
      setTimeout(() => {
        set({ state: 'idle' })
      }, 3000)
    }
  },

  clearMessages: () => set({ messages: [], currentMessage: null }),

  toggleVoice: () => set((state) => ({ voiceEnabled: !state.voiceEnabled })),

  setVolume: (volume) => set({ volume: Math.max(0, Math.min(1, volume)) }),

  toggleListening: () => set((state) => ({ isListening: !state.isListening })),

  setFacsState: (facs) => set({ facsState: facs }),
}))
