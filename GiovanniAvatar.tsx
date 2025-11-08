import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles, Volume2, VolumeX, MessageCircle } from 'lucide-react'
import { useGiovanniStore } from './GiovanniStore'

export function GiovanniAvatar() {
  const {
    mood,
    state,
    isVisible,
    currentMessage,
    voiceEnabled,
    toggleVoice,
    setVisible
  } = useGiovanniStore()

  if (!isVisible) {
    return (
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        onClick={() => setVisible(true)}
        className="fixed bottom-6 right-6 w-16 h-16 rounded-full bg-giovanni-primary giovanni-glow flex items-center justify-center cursor-pointer hover:scale-110 transition-transform z-50"
      >
        <Sparkles className="w-8 h-8 text-white" />
      </motion.button>
    )
  }

  // Different avatar expressions based on state
  const avatarEmoji = {
    idle: '😎',
    speaking: '🗣️',
    listening: '👂',
    thinking: '🤔',
    celebrating: '🎉'
  }[state]

  // Mood-based colors
  const moodColors = {
    swagger: 'from-purple-600 to-violet-700',
    motivational: 'from-amber-500 to-orange-600',
    sassy: 'from-pink-500 to-rose-600',
    caring: 'from-blue-500 to-cyan-600',
    hype: 'from-red-500 to-pink-600'
  }

  return (
    <motion.div
      initial={{ x: 400, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 400, opacity: 0 }}
      className="fixed top-6 right-6 z-50"
    >
      {/* Main avatar container */}
      <div className="relative">
        {/* Avatar circle */}
        <motion.div
          animate={{
            scale: state === 'speaking' ? [1, 1.05, 1] : 1,
            rotate: state === 'thinking' ? [0, -5, 5, 0] : 0
          }}
          transition={{
            scale: { duration: 0.5, repeat: state === 'speaking' ? Infinity : 0 },
            rotate: { duration: 2, repeat: state === 'thinking' ? Infinity : 0 }
          }}
          className={`
            w-24 h-24 rounded-full bg-gradient-to-br ${moodColors[mood]}
            giovanni-glow flex items-center justify-center
            text-5xl cursor-pointer
            hover:scale-105 transition-transform
          `}
          onClick={() => setVisible(false)}
        >
          {avatarEmoji}
        </motion.div>

        {/* Pulsing ring animation */}
        {state === 'speaking' && (
          <motion.div
            initial={{ scale: 1, opacity: 0.5 }}
            animate={{ scale: 1.5, opacity: 0 }}
            transition={{ duration: 1, repeat: Infinity }}
            className={`absolute inset-0 rounded-full bg-gradient-to-br ${moodColors[mood]} -z-10`}
          />
        )}

        {/* Voice toggle button */}
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={toggleVoice}
          className="absolute -bottom-2 -right-2 w-8 h-8 rounded-full bg-gray-800 border-2 border-gray-700 flex items-center justify-center hover:bg-gray-700 transition-colors"
        >
          {voiceEnabled ? (
            <Volume2 className="w-4 h-4 text-giovanni-accent" />
          ) : (
            <VolumeX className="w-4 h-4 text-gray-500" />
          )}
        </motion.button>
      </div>

      {/* Message bubble */}
      <AnimatePresence mode="wait">
        {currentMessage && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.9 }}
            transition={{ type: 'spring', damping: 20 }}
            className="absolute top-full mt-4 right-0 w-80 max-w-sm"
          >
            <div className="bg-gray-900 border border-gray-700 rounded-2xl p-4 shadow-2xl giovanni-glow">
              {/* Message header */}
              <div className="flex items-center gap-2 mb-2">
                <MessageCircle className="w-4 h-4 text-giovanni-accent" />
                <span className="text-xs text-gray-400 font-medium">
                  Giovanni {mood === 'swagger' ? '✨' : mood === 'sassy' ? '💅' : mood === 'hype' ? '🔥' : '💫'}
                </span>
              </div>

              {/* Message text */}
              <p className="text-sm text-gray-100 leading-relaxed">
                {currentMessage.text}
              </p>

              {/* Animated typing indicator */}
              {state === 'speaking' && (
                <div className="flex gap-1 mt-3">
                  {[0, 1, 2].map((i) => (
                    <motion.div
                      key={i}
                      animate={{ y: [0, -5, 0] }}
                      transition={{
                        duration: 0.6,
                        repeat: Infinity,
                        delay: i * 0.1
                      }}
                      className="w-2 h-2 rounded-full bg-giovanni-accent"
                    />
                  ))}
                </div>
              )}
            </div>

            {/* Speech bubble tail */}
            <div className="absolute -top-2 right-8 w-4 h-4 bg-gray-900 border-l border-t border-gray-700 transform rotate-45" />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
