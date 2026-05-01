import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Calendar,
  Image as ImageIcon,
  Send,
  Box,
  Menu,
  X,
  Brain,
  BookOpen,
  Music,
  Smartphone,
  LayoutDashboard,
  Mic,
  MicOff
} from 'lucide-react'
import { useGiovanniStore } from './GiovanniStore'
import GiovanniAvatar from './GiovanniAvatar' 
import { GiovanniMobileCompanion } from './GiovanniMobileCompanion'
import { GiovanniAnalyticsDashboard } from './GiovanniAnalyticsDashboard'
import { GiovanniCommandCenter } from './GiovanniCommandCenter'
import { GiovanniReminders, useMorningMotivation, useHydrationReminder } from './GiovanniReminders'
import { GiovanniPhotoCurator } from './GiovanniPhotoCurator'
import { GiovanniSocialMedia } from './GiovanniSocialMedia'
import { GiovanniStudioOrganizer } from './GiovanniStudioOrganizer'
import { GiovanniMusicStudio } from './GiovanniMusicStudio'
import { GiuseppePanel } from './GiuseppePanel'
import GiuseppeNotesTaker from './GiuseppeNotesTaker'
import GiuseppeBook from './GiuseppeBook'
import { Button } from './Button' // UPDATED: Path now at root

type View = 'dashboard' | 'schedule' | 'photos' | 'social' | 'studio' | 'notes' | 'book' | 'music' | 'mobile'

export default function App() {
  const [currentView, setCurrentView] = useState<View>('schedule')
  const [menuOpen, setMenuOpen] = useState(false)
  const { isListening, toggleListening } = useGiovanniStore()

  useMorningMotivation()
  useHydrationReminder()

  const navigation = [
    { id: 'dashboard' as const, label: 'Overview', icon: LayoutDashboard },
    { id: 'schedule' as const, label: 'Schedule', icon: Calendar },
    { id: 'notes' as const, label: 'Notes', icon: Brain },
    { id: 'book' as const, label: 'The Book', icon: BookOpen },
    { id: 'photos' as const, label: 'Photos', icon: ImageIcon },
    { id: 'social' as const, label: 'Social Media', icon: Send },
    { id: 'studio' as const, label: 'Studio', icon: Box },
    { id: 'music' as const, label: 'Music Studio', icon: Music },
    { id: 'mobile' as const, label: 'Pocket', icon: Smartphone }
  ]

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <div className="fixed inset-0 bg-gradient-to-br from-purple-900/20 via-gray-950 to-amber-900/20 pointer-events-none" />

      <div className="relative z-10">
        <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-40">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-giovanni-primary to-giovanni-accent bg-clip-text text-transparent giovanni-text-glow">
                  Giovanni Skyrider
                </h1>
                <p className="text-xs text-gray-400 mt-1">
                  Your Digital Hype Man & Executive AI Companion
                </p>
              </div>

              <nav className="hidden md:flex gap-2 items-center">
                <Button
                  variant={isListening ? 'default' : 'outline'}
                  onClick={toggleListening}
                  size="sm"
                  className={isListening ? "bg-red-500/10 text-red-500 border-red-500/20 hover:bg-red-500/20 mr-2" : "text-gray-400 border-gray-700 hover:text-white mr-2"}
                >
                  {isListening ? <Mic className="w-4 h-4 mr-2" /> : <MicOff className="w-4 h-4 mr-2" />}
                  {isListening ? 'Listening' : 'Mic Off'}
                </Button>
                {navigation.map((item) => {
                  const Icon = item.icon
                  return (
                    <Button
                      key={item.id}
                      variant={currentView === item.id ? 'default' : 'ghost'}
                      onClick={() => setCurrentView(item.id)}
                      size="sm"
                    >
                      <Icon className="w-4 h-4 mr-2" />
                      {item.label}
                    </Button>
                  )
                })}
              </nav>

              <button
                onClick={() => setMenuOpen(!menuOpen)}
                className="md:hidden p-2 hover:bg-gray-800 rounded-lg transition-colors"
              >
                {menuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 py-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentView}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {currentView === 'dashboard' && <GiovanniAnalyticsDashboard />}
              {currentView === 'schedule' && <GiuseppePanel />}
              {currentView === 'notes' && <GiuseppeNotesTaker />}
              {currentView === 'book' && <GiuseppeBook />}
              {currentView === 'photos' && <GiovanniPhotoCurator />}
              {currentView === 'social' && <GiovanniSocialMedia />}
              {currentView === 'studio' && <GiovanniStudioOrganizer />}
              {currentView === 'music' && <GiovanniMusicStudio />}
              {currentView === 'mobile' && <GiovanniMobileCompanion />}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>

      <GiovanniAvatar />
      <GiovanniReminders />
      <GiovanniCommandCenter />
    </div>
  )
}
