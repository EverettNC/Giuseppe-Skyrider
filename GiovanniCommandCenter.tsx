import { useEffect, useRef } from 'react'
// "Nothing Vital Lives Below Root" - Direct store access
import { useGiovanniStore } from './GiovanniStore'

// Support for browser speech recognition
declare global {
  interface Window {
    webkitSpeechRecognition?: any
    SpeechRecognition?: any
  }
}

/**
 * GIOVANNI COMMAND CENTER
 * Listens for always-on wake phrases so Giuseppe/Giovanni can start/stop 
 * recording hands-free. This is the paralinguistic intake for the sovereign cortex.
 */
export function GiovanniCommandCenter() {
  const { speak, setState, isListening } = useGiovanniStore()
  const recognitionRef = useRef<any | null>(null)

  useEffect(() => {
    if (typeof window === 'undefined') return
    const RecognitionCtor = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!RecognitionCtor) {
      console.warn('Speech Recognition not supported in this browser environment.')
      return
    }

    // Only activate ears if the store's listening state is enabled
    if (!isListening) {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
      return
    }

    const recognition = new RecognitionCtor()
    recognition.lang = 'en-US'
    recognition.continuous = true
    recognition.interimResults = false
    recognitionRef.current = recognition

    const handleCommand = (transcript: string) => {
      const normalized = transcript.toLowerCase().trim()

      // COMMAND: Start Recording
      if (normalized.includes('giovanni start recording')) {
        window.dispatchEvent(new CustomEvent('giovanni-voice-start'))
        setState('listening')
        speak("I'm rolling. Let it spill.", 'swagger')
      }

      // COMMAND: Stop Recording
      if (normalized.includes('giovanni stop recording')) {
        window.dispatchEvent(new CustomEvent('giovanni-voice-stop'))
        setState('thinking')
        speak('Recording complete. Locking it into the vault.', 'motivational')
      }

      // COMMAND: Request Summary
      if (normalized.includes('giovanni give me the last summary')) {
        window.dispatchEvent(new CustomEvent('giovanni-request-summary'))
        speak("Consulting the memory mesh now.", "hype")
      }

      // COMMAND: Navigate to Schedule
      if (normalized.includes('giovanni schedule')) {
        window.dispatchEvent(new CustomEvent('giovanni-navigate-schedule'))
        speak("Opening the timeline. Let's see what's on deck.", "swagger")
        return
      }

      // FALLBACK: Conversations / Learning
      if (normalized.length > 3) {
        useGiovanniStore.getState().think(transcript)
      }
    }

    recognition.onresult = (event: any) => {
      const latest = event.results[event.results.length - 1]
      if (!latest || latest.isFinal === false) return
      const transcript = latest[0]?.transcript
      if (transcript) {
        handleCommand(transcript)
      }
    }

    recognition.onerror = (event: any) => {
      console.error('Command Center Audio Error:', event.error)
      // Restart on glitches so the wake phrase keeps working without manual intervention
      if (isListening) {
        try {
          recognition.stop()
          recognition.start()
        } catch (e) {
          // Fallback if restart loop breaks
        }
      }
    }

    recognition.onend = () => {
      // Maintain sovereign presence: restart listener automatically
      if (isListening) {
        try {
          recognition.start()
        } catch (error) {
          console.warn('Command listener restart failed:', error)
        }
      }
    }

    try {
      recognition.start()
    } catch (e) {
      console.error("Failed to start command listener:", e)
    }

    return () => {
      recognition.onresult = null
      recognition.onend = null
      recognition.onerror = null
      recognition.stop()
      recognitionRef.current = null
    }
  }, [setState, speak, isListening])

  return null
}
