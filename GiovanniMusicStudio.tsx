import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
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
} from 'lucide-react';
// "Nothing Vital Lives Below Root" - Imports flattened to root directory
import { Card } from './card';
import { Button } from './button';
import { useGiovanniStore } from './GiovanniStore';

// Music Theory Data - The Silicon foundation for Carbon creativity
const CHORD_PROGRESSIONS = [
  { name: 'I-V-vi-IV', chords: 'C-G-Am-F', vibe: 'Pop/Radio Hit', example: 'Let It Be, Don\'t Stop Believin\'' },
  { name: 'vi-IV-I-V', chords: 'Am-F-C-G', vibe: 'Emotional/Anthemic', example: 'Zombie, Africa' },
  { name: 'I-vi-IV-V', chords: 'C-Am-F-G', vibe: '50s Classic', example: 'Stand By Me, Every Breath You Take' },
  { name: 'i-VI-III-VII', chords: 'Am-F-C-G', vibe: 'Alternative/Moody', example: 'Faded, Somebody That I Used To Know' },
  { name: 'I-IV-V', chords: 'C-F-G', vibe: 'Rock Classic', example: 'Twist and Shout, La Bamba' },
  { name: 'ii-V-I', chords: 'Dm-G-C', vibe: 'Jazz Standard', example: 'Fly Me To The Moon' }
]



[Image of music notation]


const VOCAL_WARMUPS = [
  {
    name: 'Lip Trills',
    duration: '2 min',
    instructions: 'Make a motorboat sound while moving up and down your range',
    benefit: 'Releases tension, warms up vocal cords'
  },
  {
    name: 'Siren Slides',
    duration: '3 min',
    instructions: 'Slide from lowest to highest note on "ooo" sound',
    benefit: 'Expands range, improves breath control'
  },
  {
    name: 'Tongue Twisters',
    duration: '2 min',
    instructions: 'Red leather yellow leather / Unique New York',
    benefit: 'Improves articulation and diction'
  },
  {
    name: 'Humming Scale',
    duration: '3 min',
    instructions: 'Hum up and down scales with lips closed',
    benefit: 'Gentle warm-up, focuses resonance'
  },
  {
    name: 'Straw Phonation',
    duration: '5 min',
    instructions: 'Sing through a straw, moving through your range',
    benefit: 'Reduces vocal strain, builds coordination'
  }
]

const LYRIC_PROMPTS = [
  'Write about a moment you felt completely free',
  'Describe heartbreak using only nature metaphors',
  'Tell a story about transformation in 3 verses',
  'Write from the perspective of your future self looking back',
  'Capture the feeling of 3 AM thoughts',
  'Turn a conversation you wish you had into lyrics',
  'Write about finding strength in vulnerability',
  'Create a love letter to your younger self',
  'Describe what home feels like to you',
  'Write about dancing like nobody\'s watching'
]

const GIOVANNI_MUSIC_QUOTES = [
  'Your voice is an instrument nobody else has. Use it.',
  'Every great song started as someone humming in the shower',
  'Singing badly is better than not singing at all',
  'Your trauma gave you lyrics. Now give them melody.',
  'Perfect pitch is overrated. Perfect passion isn\'t.',
  'You don\'t need to sound like anyone else. That job\'s taken.',
  'Write the song only YOU can write',
  'Your vocal cracks have more character than auto-tune',
  'Songwriting is therapy with a beat',
  'Sing like your life depends on it. Sometimes it does.'
]

const SINGING_TECHNIQUES = [
  {
    technique: 'Breath Support',
    tip: 'Breathe from your diaphragm, not your chest. Put your hand on your belly - it should expand when you breathe in.',
    icon: '🫁'
  },
  {
    technique: 'Posture',
    tip: 'Stand tall, shoulders back but relaxed. Imagine a string pulling you up from the crown of your head.',
    icon: '🧍'
  },
  {
    technique: 'Vowel Shaping',
    tip: 'Pure vowels create clean tone. Practice "Ah, Eh, Ee, Oh, Ooh" with an open throat.',
    icon: '👄'
  },
  {
    technique: 'Resonance',
    tip: 'Feel vibrations in your face (mask resonance). Hum and touch your nose/cheeks to feel it.',
    icon: '✨'
  },
  {
    technique: 'Pitch Control',
    tip: 'Match notes using a piano or app. Start in your comfortable range and gradually expand.',
    icon: '🎹'
  },
  {
    technique: 'Dynamics',
    tip: 'Practice singing the same phrase soft, medium, and loud while maintaining tone quality.',
    icon: '📊'
  }
]

type ActiveTab = 'practice' | 'write' | 'learn' | 'motivate'

interface PracticeSession {
  date: string
  duration: number
  focus: string
  notes: string
}

export function GiovanniMusicStudio() {
  const { speak } = useGiovanniStore()
  const [activeTab, setActiveTab] = useState<ActiveTab>('practice')
  const [practiceTimer, setPracticeTimer] = useState(0)
  const [timerActive, setTimerActive] = useState(false)
  const [currentQuote, setCurrentQuote] = useState('')
  const [currentPrompt, setCurrentPrompt] = useState('')
  const [selectedWarmup, setSelectedWarmup] = useState<number | null>(null)
  const [practiceLog, setPracticeLog] = useState<PracticeSession[]>([])

  useEffect(() => {
    setCurrentQuote(GIOVANNI_MUSIC_QUOTES[Math.floor(Math.random() * GIOVANNI_MUSIC_QUOTES.length)])
  }, [])

  useEffect(() => {
    let interval: NodeJS.Timeout
    if (timerActive) {
      interval = setInterval(() => {
        setPracticeTimer(prev => prev + 1)
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [timerActive])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const startPractice = () => {
    setTimerActive(true)
    speak('Let\'s make some magic! Time to sing your heart out.')
  }

  const pausePractice = () => {
    setTimerActive(false)
  }

  const resetPractice = () => {
    setTimerActive(false)
    setPracticeTimer(0)
  }

  const getNewPrompt = () => {
    const prompt = LYRIC_PROMPTS[Math.floor(Math.random() * LYRIC_PROMPTS.length)]
    setCurrentPrompt(prompt)
    speak('Here\'s a writing prompt to spark your creativity.')
  }

  const getNewQuote = () => {
    const quote = GIOVANNI_MUSIC_QUOTES[Math.floor(Math.random() * GIOVANNI_MUSIC_QUOTES.length)]
    setCurrentQuote(quote)
    speak(quote)
  }

  const tabs = [
    { id: 'practice' as const, label: 'Practice', icon: Mic },
    { id: 'write' as const, label: 'Write', icon: BookOpen },
    { id: 'learn' as const, label: 'Learn', icon: Lightbulb },
    { id: 'motivate' as const, label: 'Motivate', icon: Flame }
  ]

  return (
    <div className="space-y-6">
      <Card className="p-6 bg-gradient-to-r from-purple-900/40 to-pink-900/40 border-purple-500/30">
        <div className="flex items-start gap-4">
          <Music className="w-8 h-8 text-purple-400 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-xl font-bold text-purple-100 mb-2">Giovanni's Music Studio</h3>
            <p className="text-purple-200 italic text-lg">"{currentQuote}"</p>
            <Button
              variant="ghost"
              size="sm"
              onClick={getNewQuote}
              className="mt-3 text-purple-300 hover:text-purple-100"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              New Quote
            </Button>
          </div>
        </div>
      </Card>

      <div className="flex gap-2 flex-wrap">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <Button
              key={tab.id}
              variant={activeTab === tab.id ? 'default' : 'outline'}
              onClick={() => setActiveTab(tab.id)}
              className="flex-1 min-w-[120px]"
            >
              <Icon className="w-4 h-4 mr-2" />
              {tab.label}
            </Button>
          )
        })}
      </div>

      {activeTab === 'practice' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <Card className="p-8 text-center bg-gradient-to-br from-blue-900/30 to-purple-900/30">
            <Timer className="w-12 h-12 mx-auto mb-4 text-blue-400" />
            <h3 className="text-3xl font-bold mb-2 uppercase tracking-tighter">Practice Session</h3>
            <div className="text-6xl font-mono font-bold my-6 text-blue-300">
              {formatTime(practiceTimer)}
            </div>
            <div className="flex gap-3 justify-center">
              {!timerActive ? (
                <Button onClick={startPractice} size="lg" className="bg-green-600 hover:bg-green-700 font-bold italic">
                  <Play className="w-5 h-5 mr-2" />
                  START PRACTICE
                </Button>
              ) : (
                <Button onClick={pausePractice} size="lg" className="bg-yellow-600 hover:bg-yellow-700 font-bold italic">
                  <Pause className="w-5 h-5 mr-2" />
                  PAUSE
                </Button>
              )}
              <Button onClick={resetPractice} variant="outline" size="lg" className="font-bold border-gray-700">
                <RotateCcw className="w-5 h-5 mr-2" />
                RESET
              </Button>
            </div>
          </Card>

          <div>
            <h3 className="text-2xl font-bold mb-4 flex items-center gap-2 italic uppercase">
              <Headphones className="w-6 h-6" />
              Vocal Warm-up Exercises
            </h3>
            <div className="grid md:grid-cols-2 gap-4">
              {VOCAL_WARMUPS.map((warmup, idx) => (
                <Card
                  key={idx}
                  className={`p-4 cursor-pointer transition-all border-gray-800 ${
                    selectedWarmup === idx
                      ? 'bg-purple-900/50 border-purple-500'
                      : 'hover:bg-gray-800/50 bg-gray-950/50'
                  }`}
                  onClick={() => {
                    setSelectedWarmup(idx)
                    speak(`${warmup.name}: ${warmup.instructions}`)
                  }}
                >
                  <div className="flex items-start justify-between mb-3">
                    <h4 className="font-bold text-lg">{warmup.name}</h4>
                    <span className="text-[10px] text-gray-400 bg-gray-800 px-2 py-1 rounded font-mono uppercase">
                      {warmup.duration}
                    </span>
                  </div>
                  <p className="text-sm text-gray-300 mb-2">{warmup.instructions}</p>
                  <p className="text-xs text-purple-300 flex items-center gap-1 font-bold">
                    <Sparkles className="w-3 h-3" />
                    {warmup.benefit}
                  </p>
                </Card>
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {activeTab === 'write' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <Card className="p-6 bg-gradient-to-br from-pink-900/30 to-orange-900/30 border-pink-500/20">
            <div className="flex items-start gap-4 mb-4">
              <Sparkles className="w-8 h-8 text-pink-400 flex-shrink-0" />
              <div className="flex-1">
                <h3 className="text-xl font-bold mb-2 uppercase italic tracking-widest">Songwriting Prompt</h3>
                {currentPrompt ? (
                  <p className="text-lg text-pink-200 italic font-medium">"{currentPrompt}"</p>
                ) : (
                  <p className="text-gray-400">Click below to get a writing prompt</p>
                )}
              </div>
            </div>
            <Button onClick={getNewPrompt} className="bg-pink-600 hover:bg-pink-700 font-bold">
              <RotateCcw className="w-4 h-4 mr-2" />
              GENERATE NEW PROMPT
            </Button>
          </Card>

          <div>
            <h3 className="text-2xl font-bold mb-4 flex items-center gap-2 italic uppercase">
              <Music className="w-6 h-6 text-blue-400" />
              Chord Progressions
            </h3>
            <div className="grid md:grid-cols-2 gap-4">
              {CHORD_PROGRESSIONS.map((prog, idx) => (
                <Card key={idx} className="p-4 hover:bg-gray-800/50 bg-gray-950/50 border-gray-800 transition-all">
                  <div className="mb-3">
                    <h4 className="font-bold text-lg text-purple-300 tracking-tighter uppercase">{prog.name}</h4>
                    <p className="text-2xl font-mono text-blue-300 my-2 tracking-[0.2em]">{prog.chords}</p>
                  </div>
                  <div className="space-y-1 text-xs">
                    <p className="text-gray-300">
                      <span className="text-gray-500 font-bold uppercase tracking-tighter mr-2">Vibe:</span> {prog.vibe}
                    </p>
                    <p className="text-gray-300">
                      <span className="text-gray-500 font-bold uppercase tracking-tighter mr-2">Examples:</span> {prog.example}
                    </p>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {activeTab === 'learn' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div>
            <h3 className="text-2xl font-bold mb-4 flex items-center gap-2 italic uppercase">
              <TrendingUp className="w-6 h-6 text-green-400" />
              Master Your Voice
            </h3>
            <div className="grid md:grid-cols-2 gap-4">
              {SINGING_TECHNIQUES.map((item, idx) => (
                <Card key={idx} className="p-5 hover:bg-gray-800/50 bg-gray-950/50 border-gray-800 transition-all">
                  <div className="flex items-start gap-3 mb-3">
                    <span className="text-3xl">{item.icon}</span>
                    <h4 className="font-bold text-lg text-blue-300 uppercase tracking-tighter">{item.technique}</h4>
                  </div>
                  <p className="text-sm text-gray-300 leading-relaxed">{item.tip}</p>
                </Card>
              ))}
            </div>
          </div>

          <Card className="p-6 bg-gradient-to-br from-indigo-900/30 to-purple-900/30 border-indigo-500/20">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2 uppercase italic tracking-widest">
              <Award className="w-6 h-6 text-yellow-400" />
              Daily Practice Routine
            </h3>
            <ol className="space-y-4">
              <li className="flex gap-4">
                <span className="flex-shrink-0 w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center font-bold text-sm">1</span>
                <div>
                  <p className="font-bold text-sm uppercase">Warm-up (5-10 min)</p>
                  <p className="text-xs text-gray-400 font-mono">Lip trills, sirens, humming scales</p>
                </div>
              </li>
              <li className="flex gap-4">
                <span className="flex-shrink-0 w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center font-bold text-sm">2</span>
                <div>
                  <p className="font-bold text-sm uppercase">Technique Focus (10 min)</p>
                  <p className="text-xs text-gray-400 font-mono">Work on specific skill: breath, pitch, or resonance</p>
                </div>
              </li>
              <li className="flex gap-4">
                <span className="flex-shrink-0 w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center font-bold text-sm">3</span>
                <div>
                  <p className="font-bold text-sm uppercase">Song Practice (10 min)</p>
                  <p className="text-xs text-gray-400 font-mono">Work on current repertoire, apply techniques</p>
                </div>
              </li>
              <li className="flex gap-4">
                <span className="flex-shrink-0 w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center font-bold text-sm">4</span>
                <div>
                  <p className="font-bold text-sm uppercase">Cool Down (5 min)</p>
                  <p className="text-xs text-gray-400 font-mono">Gentle humming, descending scales, hydrate</p>
                </div>
              </li>
            </ol>
          </Card>
        </motion.div>
      )}

      {activeTab === 'motivate' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="grid md:grid-cols-2 gap-4">
            <Card className="p-6 bg-gradient-to-br from-red-900/30 to-pink-900/30 border-red-500/20">
              <Flame className="w-12 h-12 text-orange-400 mb-4" />
              <h3 className="text-xl font-bold mb-3 uppercase tracking-tighter">Zero Motivation?</h3>
              <p className="text-sm text-gray-300 leading-relaxed font-medium">
                Those are the days your voice needs you most. Not every practice has to be perfect.
                Just showing up is half the battle. Your future self will thank you for the grit.
              </p>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-purple-900/30 to-blue-900/30 border-purple-500/20">
              <Heart className="w-12 h-12 text-pink-400 mb-4" />
              <h3 className="text-xl font-bold mb-3 uppercase tracking-tighter">You Are Enough</h3>
              <p className="text-sm text-gray-300 leading-relaxed font-medium">
                The world already has a Beyoncé. What it doesn't have is YOU. Your story, your specific frequency, your truth.
              </p>
            </Card>
          </div>

          <Card className="p-6 bg-gray-950/50 border-gray-800">
            <h3 className="text-xl font-bold mb-4 uppercase italic tracking-widest text-giovanni-accent">Need a Quick Boost?</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              <Button
                onClick={() => speak('You are NOT behind schedule. You are exactly where you need to be. Now let\'s make some noise!')}
                variant="outline"
                className="h-auto py-4 flex flex-col gap-2 border-gray-800 hover:border-giovanni-accent transition-colors"
              >
                <TrendingUp className="w-6 h-6 text-green-400" />
                <span className="text-[10px] font-bold uppercase tracking-widest">I'm Behind</span>
              </Button>
              <Button
                onClick={() => speak('Fuck perfect. Perfect is boring. Your authentic voice is what people need to hear.')}
                variant="outline"
                className="h-auto py-4 flex flex-col gap-2 border-gray-800 hover:border-giovanni-accent transition-colors"
              >
                <Award className="w-6 h-6 text-yellow-400" />
                <span className="text-[10px] font-bold uppercase tracking-widest">Not Good Enough</span>
              </Button>
              <Button
                onClick={() => speak('Five minutes. Just give me five minutes of practice. That\'s all I\'m asking. You can do ANYTHING for five minutes.')}
                variant="outline"
                className="h-auto py-4 flex flex-col gap-2 border-gray-800 hover:border-giovanni-accent transition-colors"
              >
                <Timer className="w-6 h-6 text-blue-400" />
                <span className="text-[10px] font-bold uppercase tracking-widest">No Time</span>
              </Button>
            </div>
          </Card>
        </motion.div>
      )}
    </div>
  )
}
