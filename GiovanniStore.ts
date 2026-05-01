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
  audioInitialized: boolean
  initializeAudio: () => Promise<void>
  think: (text: string) => Promise<void>
  error: string | null
  clearError: () => void
  initEvents: () => () => void
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
  audioInitialized: false,
  error: null,

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

    // Trigger voice synthesis if enabled and audio is initialized
    if (get().voiceEnabled && get().audioInitialized) {
      try {
        const baseUrl = (import.meta as any).env.VITE_API_URL || 'http://localhost:8001';
        const apiUrl = `${baseUrl}/api/speak`;

        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text, tonescore: 80.0 })
        });

        if (!response.ok) throw new Error(`Server responded with ${response.status}`);

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
        set({ 
          state: 'idle',
          error: "[SILICON FAILURE]: Local synthesis engine offline. Check backend logs."
        });
        
        // Auto-clear error after 5 seconds
        setTimeout(() => get().clearError(), 5000);
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

  toggleListening: async () => {
    const currentState = get().isListening;
    const nextState = !currentState;
    
    set({ isListening: nextState });
    
    try {
      const baseUrl = (import.meta as any).env.VITE_API_URL || 'http://localhost:8001';
      const endpoint = nextState ? `${baseUrl}/api/listen` : `${baseUrl}/api/stop-listening`;
      
      await fetch(endpoint, { method: 'POST' });
    } catch (err) {
      console.error("Failed to toggle backend listening:", err);
    }
  },

  setFacsState: (facs) => set({ facsState: facs }),

  initializeAudio: async () => {
    try {
      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
      if (AudioContextClass) {
        const audioCtx = new AudioContextClass();
        await audioCtx.resume();
      }
      
      // Prime audio with a user gesture
      const audio = new Audio();
      audio.play().catch(() => {}); 
      
      set({ audioInitialized: true });
    } catch (err) {
      console.error("Failed to initialize audio context:", err);
      set({ audioInitialized: true });
    }
  },

  think: async (text) => {
    set({ state: 'thinking' })
    try {
      const apiUrl = (import.meta as any).env.VITE_TTS_API_URL?.replace('/speak', '/think') || 'http://localhost:8001/api/think';
      
      const formData = new FormData();
      formData.append('text', text);
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) throw new Error(`Think server responded with ${response.status}`);

      const result = await response.json();
      const reply = result.text || "I'm processing that.";
      
      // Speak the response
      await get().speak(reply, result.persona_state?.mood || 'swagger');
    } catch (err) {
      console.error('Think failed:', err);
      set({ state: 'idle' });
      await get().speak("My cognitive mesh is offline. Check the brain.", 'sassy');
    }
  },
  clearError: () => set({ error: null }),
  initEvents: () => {
    const baseUrl = (import.meta as any).env.VITE_API_URL || 'http://localhost:8001';
    const eventSource = new EventSource(`${baseUrl}/api/events`);
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'thought') {
          // Add the reply to the store and speak it
          get().speak(data.reply, data.mood);
        }
      } catch (err) {
        console.error("Failed to parse event data:", err);
      }
    };
    
    return () => eventSource.close();
  },
}))
