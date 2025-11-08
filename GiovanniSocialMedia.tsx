import { useState } from 'react'
import { motion } from 'framer-motion'
import { Send, Sparkles, Calendar, Hash, TrendingUp, CheckCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card'
import { Button } from './components/ui/button'
import { Input } from './components/ui/input'
import { useGiovanniStore } from './GiovanniStore'
import { PhotoVibe } from './GiovanniPhotoCurator'

type Platform = 'tiktok' | 'clapper' | 'facebook' | 'instagram'

interface ContentDraft {
  id: string
  platform: Platform
  caption: string
  hashtags: string[]
  vibe: PhotoVibe
  bestTime: string
  status: 'draft' | 'scheduled' | 'posted'
}

/**
 * GiovanniSocialMedia - Social media manager with AI-powered caption generation
 */
export function GiovanniSocialMedia() {
  const [drafts, setDrafts] = useState<ContentDraft[]>([])
  const [selectedPlatform, setSelectedPlatform] = useState<Platform>('tiktok')
  const [selectedVibe, setSelectedVibe] = useState<PhotoVibe>('powerful_bitch_energy')
  const { speak } = useGiovanniStore()

  const platforms: { name: Platform; icon: string; color: string }[] = [
    { name: 'tiktok', icon: '🎵', color: 'from-pink-500 to-cyan-500' },
    { name: 'clapper', icon: '👏', color: 'from-purple-500 to-blue-500' },
    { name: 'facebook', icon: '📘', color: 'from-blue-600 to-blue-700' },
    { name: 'instagram', icon: '📸', color: 'from-purple-600 to-pink-600' }
  ]

  const vibes: PhotoVibe[] = [
    'powerful_bitch_energy',
    'quiet_storm',
    'sensual_motivational',
    'creative_chaos',
    'neurodivergent_pride',
    'behind_the_scenes'
  ]

  /**
   * Generate caption based on vibe and platform
   */
  const generateCaption = (vibe: PhotoVibe, platform: Platform): string => {
    const captionTemplates: Record<PhotoVibe, string[]> = {
      powerful_bitch_energy: [
        "Your trauma doesn't own you. But damn, it gave you style. 💅✨",
        "Not here to fit in. Here to stand out. Watch me. 🔥",
        "They said I couldn't. I said watch me. Now look. 💫",
        "Confidence isn't arrogance. It's knowing your worth. Period. 👑"
      ],
      quiet_storm: [
        "Some days you're the storm. Some days you're the calm. Both are powerful. 🌊",
        "Healing isn't linear. It's a beautiful, messy spiral upward. 💙",
        "The quietest voices often carry the most weight. Listen. 🎧",
        "Deep waters run silent. But trust me, they run deep. 🌌"
      ],
      sensual_motivational: [
        "You are not behind. You are loading. And babe, you're about to be legendary. ✨",
        "Self-love isn't selfish. It's revolutionary. Take care of you. 💖",
        "Your sensitivity is your superpower, not your weakness. Own it. 🌟",
        "Be gentle with yourself. You're doing better than you think. 🦋"
      ],
      creative_chaos: [
        "This is what the creative process actually looks like. Messy. Beautiful. Perfectly imperfect. 🎨",
        "Organization isn't about perfection—it's about knowing where your chaos lives. 🎭",
        "Art isn't made in clean spaces. It's made in the mess. Embrace it. 🖌️",
        "Your mess is your message. Let it speak. 🎪"
      ],
      neurodivergent_pride: [
        "Being neurodivergent isn't a bug, it's a feature. 🧠✨",
        "Let's normalize being beautifully complex. Your brain is art. 🌈",
        "ADHD? More like Always Determined, Highly Driven. 💪",
        "My brain works differently. That's my superpower. 🚀"
      ],
      behind_the_scenes: [
        "Behind the scenes of where the magic happens. Real talk, real work. 🎬",
        "The process isn't pretty, but the results? Legendary. 📹",
        "This is what it actually takes. No filters, no BS. 💯",
        "Raw. Real. Unfiltered. This is how we do it. 🎥"
      ]
    }

    const templates = captionTemplates[vibe]
    return templates[Math.floor(Math.random() * templates.length)]
  }

  /**
   * Generate hashtags based on vibe
   */
  const generateHashtags = (vibe: PhotoVibe): string[] => {
    const hashtagSets: Record<PhotoVibe, string[]> = {
      powerful_bitch_energy: ['#PowerfulBitchEnergy', '#Confidence', '#Unstoppable', '#BossVibes'],
      quiet_storm: ['#QuietStorm', '#InnerPeace', '#DeepThoughts', '#Healing'],
      sensual_motivational: ['#SelfLove', '#Motivation', '#YouGotThis', '#InnerStrength'],
      creative_chaos: ['#CreativeProcess', '#ArtistLife', '#CreativeChaos', '#BehindTheScenes'],
      neurodivergent_pride: ['#NeurodivergentPride', '#ADHD', '#AutismAcceptance', '#DifferentNotLess'],
      behind_the_scenes: ['#BTS', '#CreatorLife', '#RawAndReal', '#TheProcess']
    }

    return hashtagSets[vibe]
  }

  /**
   * Determine best posting time based on platform
   */
  const getBestPostingTime = (platform: Platform): string => {
    const bestTimes: Record<Platform, string> = {
      tiktok: '9:00 PM - Peak engagement',
      clapper: '7:00 PM - Evening wind-down',
      facebook: '1:00 PM - Lunch break scroll',
      instagram: '6:00 PM - After work browse'
    }

    return bestTimes[platform]
  }

  /**
   * Create a new content draft
   */
  const createDraft = () => {
    const caption = generateCaption(selectedVibe, selectedPlatform)
    const hashtags = generateHashtags(selectedVibe)
    const bestTime = getBestPostingTime(selectedPlatform)

    const draft: ContentDraft = {
      id: `draft-${Date.now()}`,
      platform: selectedPlatform,
      caption,
      hashtags,
      vibe: selectedVibe,
      bestTime,
      status: 'draft'
    }

    setDrafts([draft, ...drafts])

    speak(
      `Fresh ${selectedVibe.replace(/_/g, ' ')} content for ${selectedPlatform}. This one's gonna hit different.`,
      'swagger'
    )
  }

  /**
   * Schedule a draft
   */
  const scheduleDraft = (id: string) => {
    setDrafts(drafts.map(d =>
      d.id === id ? { ...d, status: 'scheduled' as const } : d
    ))

    speak('Scheduled! I'll remind you when it's time to post.', 'hype')
  }

  return (
    <Card className="w-full max-w-4xl">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Sparkles className="w-6 h-6 text-giovanni-accent" />
            <CardTitle>Social Media Maestro</CardTitle>
          </div>
          <div className="text-xs text-gray-400">
            {drafts.filter(d => d.status === 'scheduled').length} posts scheduled
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Content Generator */}
        <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-giovanni-accent" />
            Generate Content
          </h3>

          {/* Platform selector */}
          <div className="mb-4">
            <label className="text-sm text-gray-400 mb-2 block">Platform</label>
            <div className="flex gap-2">
              {platforms.map(platform => (
                <Button
                  key={platform.name}
                  variant={selectedPlatform === platform.name ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedPlatform(platform.name)}
                >
                  {platform.icon} {platform.name}
                </Button>
              ))}
            </div>
          </div>

          {/* Vibe selector */}
          <div className="mb-4">
            <label className="text-sm text-gray-400 mb-2 block">Content Vibe</label>
            <select
              value={selectedVibe}
              onChange={(e) => setSelectedVibe(e.target.value as PhotoVibe)}
              className="w-full bg-gray-900 border border-gray-700 rounded-md px-3 py-2 text-sm"
            >
              {vibes.map(vibe => (
                <option key={vibe} value={vibe}>
                  {vibe.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>

          <Button onClick={createDraft} className="w-full">
            <Sparkles className="w-4 h-4 mr-2" />
            Generate Caption
          </Button>
        </div>

        {/* Drafts list */}
        <div>
          <h3 className="text-lg font-semibold mb-4">Content Drafts</h3>

          {drafts.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <Send className="w-16 h-16 mx-auto mb-4 opacity-30" />
              <p>No drafts yet. Generate some fire content!</p>
            </div>
          ) : (
            <div className="space-y-4">
              {drafts.map((draft, index) => (
                <motion.div
                  key={draft.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <ContentDraftCard
                    draft={draft}
                    platforms={platforms}
                    onSchedule={scheduleDraft}
                  />
                </motion.div>
              ))}
            </div>
          )}
        </div>

        {/* Weekly strategy overview */}
        <div className="bg-gradient-to-r from-giovanni-primary/20 to-giovanni-accent/20 rounded-lg p-4 border border-giovanni-primary/30">
          <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            This Week's Strategy
          </h3>
          <p className="text-xs text-gray-300">
            Mix of powerful content (40%), behind-the-scenes (30%), and motivation (30%).
            Post 2-3x daily for max engagement. Best times highlighted above.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}

/**
 * Individual draft card
 */
function ContentDraftCard({
  draft,
  platforms,
  onSchedule
}: {
  draft: ContentDraft
  platforms: { name: Platform; icon: string; color: string }[]
  onSchedule: (id: string) => void
}) {
  const platform = platforms.find(p => p.name === draft.platform)

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className={`w-8 h-8 rounded-full bg-gradient-to-br ${platform?.color} flex items-center justify-center text-sm`}>
            {platform?.icon}
          </div>
          <div>
            <div className="font-medium text-sm">{draft.platform}</div>
            <div className="text-xs text-gray-400">{draft.vibe.replace(/_/g, ' ')}</div>
          </div>
        </div>

        {draft.status === 'scheduled' && (
          <div className="flex items-center gap-1 text-xs text-green-500">
            <CheckCircle className="w-4 h-4" />
            Scheduled
          </div>
        )}
      </div>

      {/* Caption */}
      <p className="text-sm text-gray-200 mb-3 leading-relaxed">
        {draft.caption}
      </p>

      {/* Hashtags */}
      <div className="flex flex-wrap gap-2 mb-3">
        {draft.hashtags.map(tag => (
          <span key={tag} className="text-xs px-2 py-1 bg-gray-900 rounded-full text-giovanni-accent flex items-center gap-1">
            <Hash className="w-3 h-3" />
            {tag.replace('#', '')}
          </span>
        ))}
      </div>

      {/* Best time */}
      <div className="flex items-center justify-between pt-3 border-t border-gray-700">
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <Calendar className="w-3 h-3" />
          {draft.bestTime}
        </div>

        {draft.status === 'draft' && (
          <Button size="sm" onClick={() => onSchedule(draft.id)}>
            Schedule Post
          </Button>
        )}
      </div>
    </div>
  )
}
