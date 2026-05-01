import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Music,
  Mic,
  Volume2,
  Heart,
  Flame,
  Sparkles,
  Play,
  Pause,
  RotateCcw,
  Lightbulb,
  BookOpen,
  TrendingUp,
  Award,
  Timer,
  Headphones
} from 'lucide-react'
import { Card } from './card' // FIXED: Path is now at root
import { Button } from './button' // FIXED: Path is now at root
import { useGiovanniStore } from './GiovanniStore'

const CHORD_PROGRESSIONS = [
  { name: 'I-V-vi-IV', chords: 'C-G-Am-F', vibe: 'Pop/Radio Hit', example: "Let It Be" },
  { name: 'vi-IV-I-V', chords: 'Am-F-C-G', vibe: 'Emotional/Anthemic', example: 'Zombie' }
]

const VOCAL_WARMUPS = [
  { name: 'Lip Trills', duration: '2 min', instructions: 'Motorboat sound up/down range', benefit: 'Releases tension' },
  { name: 'Siren Slides', duration: '3 min', instructions: 'Slide high to low on "ooo"', benefit: 'Expands range' }
]

const GIOVANNI_MUSIC_QUOTES = [
  'Your voice is an instrument nobody else has. Use it.',
  'Your vocal cracks have more character than auto-tune',
  'Sing like your life depends on it. Sometimes it does.'
]

export function GiovanniMusicStudio() {
  const { speak } = useGiovanniStore()
  const [activeTab, setActiveTab] = useState<'practice' | 'write' | 'learn' | 'motivate'>('practice')
  const [practiceTimer, setPracticeTimer] = useState(0)
  const [timerActive, setTimerActive] = useState(false)
  const [currentQuote, setCurrentQuote] = useState('')

  useEffect(() => {
    setCurrentQuote(GIOVANNI_MUSIC_QUOTES[Math.floor(Math.random() * GIOVANNI_MUSIC_QUOTES.length)])
  }, [])

  useEffect(() => {
    let interval: any
    if (timerActive) {
      interval = setInterval(() => setPracticeTimer(prev => prev + 1), 1000)
    }
    return () => clearInterval(interval)
  }, [timerActive])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="space-y-6">
      <Card className="p-6 bg-gradient-to-r from-purple-900/40 to-pink-900/40 border-purple-500/30">
        <div className="flex items-start gap-4">
          <Music className="w-8 h-8 text-purple-400 mt-1" />
          <div>
            <h3 className="text-xl font-bold text-purple-100 mb-2">Giovanni's Music Studio</h3>
            <p className="text-purple-200 italic text-lg">"{currentQuote}"</p>
          </div>
        </div>
      </Card>

      <div className="flex gap-2 flex-wrap">
        {['practice', 'write', 'learn', 'motivate'].map((tab) => (
          <Button
            key={tab}
            variant={activeTab === tab ? 'default' : 'outline'}
            onClick={() => setActiveTab(tab as any)}
            className="flex-1"
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </Button>
        ))}
      </div>

      {activeTab === 'practice' && (
        <Card className="p-8 text-center bg-gradient-to-br from-blue-900/30 to-purple-900/30">
          <Timer className="w-12 h-12 mx-auto mb-4 text-blue-400" />
          <div className="text-6xl font-mono font-bold my-6 text-blue-300">
            {formatTime(practiceTimer)}
          </div>
          <div className="flex gap-3 justify-center">
            <Button onClick={() => setTimerActive(!timerActive)} size="lg">
              {timerActive ? <Pause className="w-5 h-5 mr-2" /> : <Play className="w-5 h-5 mr-2" />}
              {timerActive ? 'Pause' : 'Start'}
            </Button>
            <Button onClick={() => setPracticeTimer(0)} variant="outline" size="lg">
              Reset
            </Button>
          </div>
        </Card>
      )}
    </div>
  )
}
