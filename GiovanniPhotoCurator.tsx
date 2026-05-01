import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Image, Sparkles, Calendar, Tag, TrendingUp } from 'lucide-react'
// "Nothing Vital Lives Below Root" - Imports flattened to root directory
import { Card, CardContent, CardHeader, CardTitle } from './card'
import { Button } from './button'
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
 * Hardware Native: Sovereign asset management for the Carbon-Silicon exchange.
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

  const loadPhotos = async () => {
    setLoading(true)

    try {
      // Simulated photo library - routes to the project root assets
      const mockPhotos: Photo[] = [
        {
          id: '1',
          filename: 'studio_setup_001.jpg',
          path: 'https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?q=80&w=600&auto=format&fit=crop',
          date: new Date('2025-11-01'),
          vibe: 'behind_the_scenes',
          tags: ['studio', 'workspace', 'creative'],
          suggested: true,
          engagement_score: 85
        },
        {
          id: '2',
          filename: 'confident_portrait.jpg',
          path: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=600&auto=format&fit=crop',
          date: new Date('2025-11-05'),
          vibe: 'powerful_bitch_energy',
          tags: ['portrait', 'confidence', 'powerful'],
          suggested: true,
          engagement_score: 92
        },
        {
          id: '3',
          filename: 'creative_process.jpg',
          path: 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?q=80&w=600&auto=format&fit=crop',
          date: new Date('2025-11-07'),
          vibe: 'creative_chaos',
          tags: ['process', 'art', 'messy'],
          suggested: false,
          engagement_score: 78
        }
      ]

      setPhotos(mockPhotos)

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

  const getSuggestion = () => {
    const topPhotos = photos
      .filter(p => p.suggested)
      .sort((a, b) => (b.engagement_score || 0) - (a.engagement_score || 0))

    if (topPhotos.length === 0) {
      speak('Upload some photos first, then I\'ll tell you what\'s gonna hit.', 'sassy')
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
    <Card className="w-full max-w-4xl bg-gray-950 border-gray-800 text-gray-100">
      <CardHeader className="border-b border-gray-900 pb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Image className="w-6 h-6 text-giovanni-accent" />
            <CardTitle className="text-2xl font-bold tracking-tight uppercase italic">Photo Curator</CardTitle>
          </div>
          <Button 
            onClick={getSuggestion} 
            size="sm"
            className="bg-giovanni-accent hover:bg-giovanni-accent/80 text-white font-black italic tracking-widest"
          >
            <Sparkles className="w-4 h-4 mr-2" />
            WHAT SHOULD I POST?
          </Button>
        </div>
      </CardHeader>

      <CardContent className="pt-6">
        {/* Vibe filters */}
        <div className="flex flex-wrap gap-2 mb-6">
          <Button
            variant={selectedVibe === 'all' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedVibe('all')}
            className={selectedVibe === 'all' ? 'bg-gray-800 text-white' : 'border-gray-800 text-gray-400'}
          >
            All Photos
          </Button>
          {vibes.map(vibe => (
            <Button
              key={vibe.name}
              variant={selectedVibe === vibe.name ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedVibe(vibe.name)}
              className={selectedVibe === vibe.name ? 'bg-giovanni-primary text-white border-transparent' : 'border-gray-800 text-gray-500'}
              title={vibe.description}
            >
              {vibe.emoji} {vibe.name.replace(/_/g, ' ')}
            </Button>
          ))}
        </div>

        {/* Photo grid */}
        {loading ? (
          <div className="text-center py-20 text-gray-600 font-mono uppercase tracking-[0.3em] animate-pulse">
            Scanning hardware library...
          </div>
        ) : filteredPhotos.length === 0 ? (
          <div className="text-center py-20 text-gray-700">
            <Image className="w-16 h-16 mx-auto mb-4 opacity-10" />
            <p className="uppercase tracking-widest font-bold">No assets found</p>
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
        <div className="mt-8 pt-6 border-t border-gray-900 grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-black text-giovanni-accent tracking-tighter">{photos.length}</div>
            <div className="text-[10px] text-gray-600 font-bold uppercase tracking-widest">Total Assets</div>
          </div>
          <div>
            <div className="text-2xl font-black text-giovanni-accent tracking-tighter">
              {photos.filter(p => p.suggested).length}
            </div>
            <div className="text-[10px] text-gray-600 font-bold uppercase tracking-widest">Post Ready</div>
          </div>
          <div>
            <div className="text-2xl font-black text-giovanni-accent tracking-tighter">
              {new Set(photos.map(p => p.vibe)).size}
            </div>
            <div className="text-[10px] text-gray-600 font-bold uppercase tracking-widest">Categorized</div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

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
    <div className="relative group bg-gray-900 rounded-lg overflow-hidden border border-gray-800 hover:border-giovanni-accent transition-all duration-300">
      <div className="aspect-square bg-gradient-to-br from-gray-800 to-gray-950 flex items-center justify-center overflow-hidden">
        {photo.path ? (
          <img src={photo.path} alt={photo.filename} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
        ) : (
          <Image className="w-12 h-12 text-gray-800 group-hover:scale-110 transition-transform" />
        )}
      </div>

      <div className="absolute inset-0 bg-gradient-to-t from-black via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
        <div className="absolute bottom-0 left-0 right-0 p-4">
          <div className="text-[10px] font-mono text-gray-400 mb-2 flex items-center gap-2">
            <Calendar className="w-3 h-3" />
            {photo.date.toLocaleDateString()}
          </div>

          {photo.engagement_score && (
            <div className="text-xs text-giovanni-accent font-black italic mb-2 flex items-center gap-2">
              <TrendingUp className="w-3 h-3" />
              {photo.engagement_score}% HIT PROBABILITY
            </div>
          )}

          {vibeInfo && (
            <div className="text-sm font-bold mb-2 uppercase text-white tracking-tight">
              {vibeInfo.emoji} {photo.vibe?.replace(/_/g, ' ')}
            </div>
          )}

          <div className="flex flex-wrap gap-1">
            {photo.tags.map(tag => (
              <span
                key={tag}
                className="text-[10px] px-2 py-0.5 bg-gray-800/80 text-gray-400 rounded-full font-bold uppercase"
              >
                #{tag}
              </span>
            ))}
          </div>
        </div>
      </div>

      {photo.suggested && (
        <div className="absolute top-3 right-3 bg-giovanni-accent text-white text-[10px] font-black italic px-3 py-1 rounded-full shadow-[0_0_15px_rgba(255,51,102,0.5)]">
          🔥 FIRE
        </div>
      )}
    </div>
  )
}
