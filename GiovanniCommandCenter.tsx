import { useEffect, useRef } from 'react'
import { useGiovanniStore } from './GiovanniStore'

// Support for browser speech recognition
declare global {
  interface Window {
    webkitSpeechRecognition?: typeof SpeechRecognition
    SpeechRecognition?: typeof SpeechRecognition
  }
}

/**
 * Listens for always-on wake phrases so Giovanni can start/stop recording hands-free.
 */
export function GiovanniCommandCenter() {
  const { speak, setState, isListening } = useGiovanniStore()
  const recognitionRef = useRef<SpeechRecognition | null>(null)

  useEffect(() => {
    if (typeof window === 'undefined') return
    const RecognitionCtor = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!RecognitionCtor) return

    if (!isListening) {
      return
    }

    const recognition = new RecognitionCtor()
    recognition.lang = 'en-US'
    recognition.continuous = true
    recognition.interimResults = false
    recognitionRef.current = recognition

    const handleCommand = (transcript: string) => {
      const normalized = transcript.toLowerCase().trim()

      if (normalized.includes('giovanni start recording')) {
        window.dispatchEvent(new CustomEvent('giovanni-voice-start'))
        setState('listening')
        speak("I'm rolling. Let it spill.", 'swagger')
      }

      if (normalized.includes('giovanni stop recording')) {
        window.dispatchEvent(new CustomEvent('giovanni-voice-stop'))
        setState('thinking')
        speak('Recording complete. Want me to summarize it?', 'motivational')
      }

      if (normalized.includes('giovanni give me the last summary')) {
        window.dispatchEvent(new CustomEvent('giovanni-request-summary'))
      }
    }

    recognition.onresult = (event) => {
      const latest = event.results[event.results.length - 1]
      if (!latest || latest.isFinal === false) return
      const transcript = latest[0]?.transcript
      if (transcript) {
        handleCommand(transcript)
      }
    }

    recognition.onerror = () => {
      // Restart on glitches so the wake phrase keeps working
      recognition.stop()
      recognition.start()
    }

    recognition.onend = () => {
      try {
        recognition.start()
      } catch (error) {
        console.warn('Command listener restart failed:', error)
      }
    }

    recognition.start()

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
