import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Image, Sparkles, Calendar, Tag, TrendingUp } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card'
import { Button } from './components/ui/button'
import { useGiovanniStore } from './GiovanniStore'

export type PhotoVibe =
  | 'powerful_bitch_energy'
  | 'quiet_storm'
  | 'sensual_motivational'
  | 'creative_chaos'
  | 'neurodivergent_pride'
  | 'behind_the_scenes'

export interface Photo {
  id: string
  filename: string
  path: string
  date: Date
  vibe?: PhotoVibe
  tags: string[]
  suggested: boolean
  engagement_score?: number
}

/**
 * GiovanniPhotoCurator - AI-powered photo organization with vibe categorization
 */
export function GiovanniPhotoCurator() {
  const [photos, setPhotos] = useState<Photo[]>([])
  const [selectedVibe, setSelectedVibe] = useState<PhotoVibe | 'all'>('all')
  const [loading, setLoading] = useState(false)
  const { speak } = useGiovanniStore()

  const vibes: { name: PhotoVibe; emoji: string; description: string }[] = [
    { name: 'powerful_bitch_energy', emoji: '💅', description: 'Bold, confident, unstoppable' },
    { name: 'quiet_storm', emoji: '🌊', description: 'Deep, contemplative, powerful' },
    { name: 'sensual_motivational', emoji: '✨', description: 'Inspiring, warm, uplifting' },
    { name: 'creative_chaos', emoji: '🎨', description: 'Raw, authentic, artistic' },
    { name: 'neurodivergent_pride', emoji: '🧠', description: 'Celebrating uniqueness' },
    { name: 'behind_the_scenes', emoji: '🎬', description: 'Process, realness, transparency' }
  ]

  /**
   * Load photos from public directory (in a real app, this would scan file system)
   */
  const loadPhotos = async () => {
    setLoading(true)

    try {
      // Simulated photo library - in production, this would use File System Access API
      // or read from a designated photo directory
      const mockPhotos: Photo[] = [
        {
          id: '1',
          filename: 'studio_setup_001.jpg',
          path: '/photos/studio_setup_001.jpg',
          date: new Date('2025-11-01'),
          vibe: 'behind_the_scenes',
          tags: ['studio', 'workspace', 'creative'],
          suggested: true,
          engagement_score: 85
        },
        {
          id: '2',
          filename: 'confident_portrait.jpg',
          path: '/photos/confident_portrait.jpg',
          date: new Date('2025-11-05'),
          vibe: 'powerful_bitch_energy',
          tags: ['portrait', 'confidence', 'powerful'],
          suggested: true,
          engagement_score: 92
        },
        {
          id: '3',
          filename: 'creative_process.jpg',
          path: '/photos/creative_process.jpg',
          date: new Date('2025-11-07'),
          vibe: 'creative_chaos',
          tags: ['process', 'art', 'messy'],
          suggested: false,
          engagement_score: 78
        }
      ]

      setPhotos(mockPhotos)

      // Giovanni's reaction
      speak(
        `Found ${mockPhotos.length} photos in your library. ${mockPhotos.filter(p => p.suggested).length} of them are absolute fire and ready to post.`,
        'swagger'
      )
    } catch (error) {
      console.error('Error loading photos:', error)
    } finally {
      setLoading(false)
    }
  }

  /**
   * Categorize a photo by vibe
   */
  const categorizePhoto = (photoId: string, vibe: PhotoVibe) => {
    setPhotos(photos.map(photo =>
      photo.id === photoId ? { ...photo, vibe } : photo
    ))

    const vibeInfo = vibes.find(v => v.name === vibe)
    speak(
      `That's definitely ${vibeInfo?.emoji} ${vibe.replace(/_/g, ' ')} energy. Good eye!`,
      'swagger'
    )
  }

  /**
   * Get Giovanni's suggestion for posting
   */
  const getSuggestion = () => {
    const topPhotos = photos
      .filter(p => p.suggested)
      .sort((a, b) => (b.engagement_score || 0) - (a.engagement_score || 0))

    if (topPhotos.length === 0) {
      speak('Upload some photos first, then I'll tell you what's gonna hit.', 'sassy')
      return
    }

    const topPhoto = topPhotos[0]
    const vibeInfo = vibes.find(v => v.name === topPhoto.vibe)

    speak(
      `${topPhoto.filename} is giving ${vibeInfo?.emoji} ${vibeInfo?.name.replace(/_/g, ' ')}. Post this one. Trust me.`,
      'hype'
    )
  }

  useEffect(() => {
    loadPhotos()
  }, [])

  const filteredPhotos = selectedVibe === 'all'
    ? photos
    : photos.filter(p => p.vibe === selectedVibe)

  return (
    <Card className="w-full max-w-4xl">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Image className="w-6 h-6 text-giovanni-accent" />
            <CardTitle>Photo Curator</CardTitle>
          </div>
          <Button onClick={getSuggestion} size="sm">
            <Sparkles className="w-4 h-4 mr-2" />
            What Should I Post?
          </Button>
        </div>
      </CardHeader>

      <CardContent>
        {/* Vibe filters */}
        <div className="flex flex-wrap gap-2 mb-6">
          <Button
            variant={selectedVibe === 'all' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedVibe('all')}
          >
            All Photos
          </Button>
          {vibes.map(vibe => (
            <Button
              key={vibe.name}
              variant={selectedVibe === vibe.name ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedVibe(vibe.name)}
              title={vibe.description}
            >
              {vibe.emoji} {vibe.name.replace(/_/g, ' ')}
            </Button>
          ))}
        </div>

        {/* Photo grid */}
        {loading ? (
          <div className="text-center py-12 text-gray-400">
            Loading your visual library...
          </div>
        ) : filteredPhotos.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <Image className="w-16 h-16 mx-auto mb-4 opacity-30" />
            <p>No photos found for this vibe</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredPhotos.map((photo, index) => (
              <motion.div
                key={photo.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <PhotoCard
                  photo={photo}
                  vibes={vibes}
                  onCategorize={categorizePhoto}
                />
              </motion.div>
            ))}
          </div>
        )}

        {/* Stats bar */}
        <div className="mt-6 pt-6 border-t border-gray-800 grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-giovanni-accent">{photos.length}</div>
            <div className="text-xs text-gray-400">Total Photos</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-giovanni-accent">
              {photos.filter(p => p.suggested).length}
            </div>
            <div className="text-xs text-gray-400">Ready to Post</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-giovanni-accent">
              {new Set(photos.map(p => p.vibe)).size}
            </div>
            <div className="text-xs text-gray-400">Vibe Categories</div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

/**
 * Individual photo card component
 */
function PhotoCard({
  photo,
  vibes,
  onCategorize
}: {
  photo: Photo
  vibes: { name: PhotoVibe; emoji: string }[]
  onCategorize: (id: string, vibe: PhotoVibe) => void
}) {
  const vibeInfo = vibes.find(v => v.name === photo.vibe)

  return (
    <div className="relative group bg-gray-800 rounded-lg overflow-hidden border border-gray-700 hover:border-giovanni-accent transition-colors">
      {/* Placeholder for photo - in production would show actual image */}
      <div className="aspect-square bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center">
        <Image className="w-12 h-12 text-gray-600" />
      </div>

      {/* Overlay with info */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
        <div className="absolute bottom-0 left-0 right-0 p-3">
          <div className="text-xs text-gray-300 mb-2 flex items-center gap-2">
            <Calendar className="w-3 h-3" />
            {photo.date.toLocaleDateString()}
          </div>

          {photo.engagement_score && (
            <div className="text-xs text-giovanni-accent mb-2 flex items-center gap-2">
              <TrendingUp className="w-3 h-3" />
              {photo.engagement_score}% engagement score
            </div>
          )}

          {vibeInfo && (
            <div className="text-sm font-medium mb-2">
              {vibeInfo.emoji} {photo.vibe?.replace(/_/g, ' ')}
            </div>
          )}

          <div className="flex flex-wrap gap-1">
            {photo.tags.map(tag => (
              <span
                key={tag}
                className="text-xs px-2 py-1 bg-gray-900/80 rounded-full flex items-center gap-1"
              >
                <Tag className="w-3 h-3" />
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Suggested badge */}
      {photo.suggested && (
        <div className="absolute top-2 right-2 bg-giovanni-accent text-white text-xs px-2 py-1 rounded-full flex items-center gap-1">
          <Sparkles className="w-3 h-3" />
          Fire
        </div>
      )}
    </div>
  )
}
