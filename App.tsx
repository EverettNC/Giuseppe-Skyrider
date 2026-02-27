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
import { GiovanniAvatar } from './GiovanniAvatar'
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
import { Button } from './components/ui/button'

type View = 'dashboard' | 'schedule' | 'photos' | 'social' | 'studio' | 'notes' | 'book' | 'music' | 'mobile'

/**
 * Main Giovanni Skyrider Application
 */
export default function App() {
  const [currentView, setCurrentView] = useState<View>('schedule')
  const [menuOpen, setMenuOpen] = useState(false)
  const { isListening, toggleListening } = useGiovanniStore()

  // Initialize Giovanni's proactive features
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
      {/* Background gradient */}
      <div className="fixed inset-0 bg-gradient-to-br from-purple-900/20 via-gray-950 to-amber-900/20 pointer-events-none" />

      {/* Main container */}
      <div className="relative z-10">
        {/* Header */}
        <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-40">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              {/* Logo */}
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-giovanni-primary to-giovanni-accent bg-clip-text text-transparent giovanni-text-glow">
                  Giovanni Skyrider
                </h1>
                <p className="text-xs text-gray-400 mt-1">
                  Your Digital Hype Man & Executive AI Companion
                </p>
              </div>

              {/* Desktop navigation */}
              <nav className="hidden md:flex gap-2 items-center">
                <Button
                  variant={isListening ? 'default' : 'outline'}
                  onClick={toggleListening}
                  size="sm"
                  className={isListening ? "bg-red-500/10 text-red-500 border-red-500/20 hover:bg-red-500/20 mr-2" : "text-gray-400 border-gray-700 hover:text-white mr-2"}
                  title={isListening ? "Giovanni is listening (Wake Word Active)" : "Giovanni is asleep (Mic Off)"}
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

              {/* Mobile menu toggle */}
              <button
                onClick={() => setMenuOpen(!menuOpen)}
                className="md:hidden p-2 hover:bg-gray-800 rounded-lg transition-colors"
              >
                {menuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>

            {/* Mobile navigation */}
            <AnimatePresence>
              {menuOpen && (
                <motion.nav
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="md:hidden overflow-hidden"
                >
                  <div className="flex flex-col gap-2 pt-4">
                    <Button
                      variant={isListening ? 'default' : 'outline'}
                      onClick={toggleListening}
                      size="sm"
                      className={`w-full justify-start mb-2 ${isListening ? "bg-red-500/10 text-red-500 border-red-500/20 hover:bg-red-500/20" : "text-gray-400 border-gray-700 hover:text-white"}`}
                    >
                      {isListening ? <Mic className="w-4 h-4 mr-2" /> : <MicOff className="w-4 h-4 mr-2" />}
                      {isListening ? 'Wake Word: Listening' : 'Wake Word: Off'}
                    </Button>
                    {navigation.map((item) => {
                      const Icon = item.icon
                      return (
                        <Button
                          key={item.id}
                          variant={currentView === item.id ? 'default' : 'ghost'}
                          onClick={() => {
                            setCurrentView(item.id)
                            setMenuOpen(false)
                          }}
                          size="sm"
                          className="w-full justify-start"
                        >
                          <Icon className="w-4 h-4 mr-2" />
                          {item.label}
                        </Button>
                      )
                    })}
                  </div>
                </motion.nav>
              )}
            </AnimatePresence>
          </div>
        </header>

        {/* Main content */}
        <main className="max-w-7xl mx-auto px-4 py-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentView}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {currentView === 'dashboard' && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h2 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
                      <LayoutDashboard className="w-8 h-8 text-giovanni-accent" />
                      Command Dashboard
                    </h2>
                  </div>
                  <GiovanniAnalyticsDashboard />
                </div>
              )}

              {currentView === 'schedule' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-3xl font-bold mb-2">Schedule & Tasks</h2>
                    <p className="text-gray-400">
                      Your content calendar, medication reminders, and daily flow
                    </p>
                  </div>
                  <GiuseppePanel />
                </div>
              )}

              {currentView === 'notes' && <GiuseppeNotesTaker />}

              {currentView === 'book' && <GiuseppeBook />}

              {currentView === 'photos' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-3xl font-bold mb-2">Photo Library</h2>
                    <p className="text-gray-400">
                      Organized by vibe, tagged by mood, curated with purpose
                    </p>
                  </div>
                  <GiovanniPhotoCurator />
                </div>
              )}

              {currentView === 'social' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-3xl font-bold mb-2">Social Media Command Center</h2>
                    <p className="text-gray-400">
                      Generate captions, schedule posts, dominate your feed
                    </p>
                  </div>
                  <GiovanniSocialMedia />
                </div>
              )}

              {currentView === 'studio' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-3xl font-bold mb-2">Studio & Desk Organizer</h2>
                    <p className="text-gray-400">
                      Track your gear, organize your chaos, own your space
                    </p>
                  </div>
                  <GiovanniStudioOrganizer />
                </div>
              )}

              {currentView === 'music' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-3xl font-bold mb-2">Music Composition Studio</h2>
                    <p className="text-gray-400">
                      Compose songs, train your voice, and unleash your musical genius
                    </p>
                  </div>
                  <GiovanniMusicStudio />
                </div>
              )}

              {currentView === 'mobile' && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h2 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
                      <Smartphone className="w-8 h-8 text-giovanni-accent" />
                      Giovanni Pocket Sync
                    </h2>
                  </div>
                  <GiovanniMobileCompanion />
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        </main>

        {/* Footer */}
        <footer className="border-t border-gray-800 mt-16">
          <div className="max-w-7xl mx-auto px-4 py-6 text-center text-sm text-gray-500">
            <p>
              Built with swagger by Everett N. Christman & Derek C. Jr.
            </p>
            <p className="mt-1 text-xs">
              Christman AI Project • Nothing Vital Lives Below Root
            </p>
          </div>
        </footer>
      </div>

      {/* Giovanni Avatar - always visible */}
      <GiovanniAvatar />

      {/* Giovanni Reminders - runs in background */}
      <GiovanniReminders />

      {/* Giovanni Command Center - runs in background for voice activation */}
      <GiovanniCommandCenter />
    </div>
  )
}
