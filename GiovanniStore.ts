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

  // Actions
  setMood: (mood: GiovanniMood) => void
  setState: (state: GiovanniState) => void
  setVisible: (visible: boolean) => void
  setPosition: (position: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left') => void
  addMessage: (text: string, mood: GiovanniMood) => void
  speak: (text: string, mood: GiovanniMood) => void
  clearMessages: () => void
  toggleVoice: () => void
  setVolume: (volume: number) => void
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

  speak: (text, mood) => {
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
    if (get().voiceEnabled && 'speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.volume = get().volume
      utterance.rate = 0.95
      utterance.pitch = 0.9

      utterance.onend = () => {
        set({ state: 'idle' })
        // Mark as spoken
        set((state) => ({
          messages: state.messages.map(m =>
            m.id === message.id ? { ...m, spoken: true } : m
          )
        }))
      }

      window.speechSynthesis.speak(utterance)
    } else {
      // If voice is disabled, just show the message briefly
      setTimeout(() => {
        set({ state: 'idle' })
      }, 3000)
    }
  },

  clearMessages: () => set({ messages: [], currentMessage: null }),

  toggleVoice: () => set((state) => ({ voiceEnabled: !state.voiceEnabled })),

  setVolume: (volume) => set({ volume: Math.max(0, Math.min(1, volume)) })
}))
