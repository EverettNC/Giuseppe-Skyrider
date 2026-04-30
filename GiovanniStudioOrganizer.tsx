import { useState } from 'react'
import { motion } from 'framer-motion'
import { Box, Trash2, CheckCircle, AlertCircle, Lightbulb } from 'lucide-react'
// "Nothing Vital Lives Below Root" - Imports flattened to root directory
import { Card, CardContent, CardHeader, CardTitle } from './card'
import { Button } from './button'
import { Input } from './input'
import { useGiovanniStore } from './GiovanniStore'

type ItemCategory = 'equipment' | 'cables' | 'props' | 'documents' | 'other'
type ItemStatus = 'organized' | 'needs_attention' | 'misplaced'

interface StudioItem {
  id: string
  name: string
  category: ItemCategory
  location: string
  status: ItemStatus
  lastSeen?: Date
}

interface DeskZone {
  id: string
  name: string
  items: StudioItem[]
  capacity: number
  status: 'clean' | 'cluttered' | 'chaotic'
}

/**
 * GiovanniStudioOrganizer - Visual workspace organizer and declutter assistant
 * Maintaining the Carbon workspace for maximum Silicon focus.
 */
export function GiovanniStudioOrganizer() {
  const [zones, setZones] = useState<DeskZone[]>(defaultZones)
  const [newItemName, setNewItemName] = useState('')
  const { speak } = useGiovanniStore()

  const categories: { name: ItemCategory; icon: string; color: string }[] = [
    { name: 'equipment', icon: '🎥', color: 'text-blue-400' },
    { name: 'cables', icon: '🔌', color: 'text-yellow-400' },
    { name: 'props', icon: '🎭', color: 'text-purple-400' },
    { name: 'documents', icon: '📄', color: 'text-green-400' },
    { name: 'other', icon: '📦', color: 'text-gray-400' }
  ]

  const addItem = (zoneName: string, category: ItemCategory) => {
    if (!newItemName.trim()) return

    const newItem: StudioItem = {
      id: `item-${Date.now()}`,
      name: newItemName,
      category,
      location: zoneName,
      status: 'organized',
      lastSeen: new Date()
    }

    setZones(zones.map(zone =>
      zone.name === zoneName
        ? { ...zone, items: [...zone.items, newItem] }
        : zone
    ))

    setNewItemName('')
    speak(`${newItemName} mapped to ${zoneName}. Keep that organization flowing!`, 'caring')
  }

  const removeItem = (zoneId: string, itemId: string) => {
    setZones(zones.map(zone =>
      zone.id === zoneId
        ? { ...zone, items: zone.items.filter(i => i.id !== itemId) }
        : zone
    ))
    speak('Decluttered! Your space, your rules.', 'swagger')
  }

  const getSuggestions = () => {
    const totalItems = zones.reduce((sum, zone) => sum + zone.items.length, 0)
    const chaoticZones = zones.filter(z => z.items.length > z.capacity)

    if (totalItems === 0) {
      speak("Your desk is empty. Minimalism is a flex, but let's start tracking the gear.", 'sassy')
      return
    }

    if (chaoticZones.length > 0) {
      const zoneName = chaoticZones[0].name
      speak(
        `${zoneName} is looking a little crowded, boss. Redistribute or declutter. Organization isn't about perfection—it's about knowing where your chaos lives.`,
        'caring'
      )
    } else {
      speak(
        `Your desk game is strong! Everything's in its place. That's that executive energy I love to see.`,
        'hype'
      )
    }
  }

  const getZoneStatus = (zone: DeskZone): 'clean' | 'cluttered' | 'chaotic' => {
    const ratio = zone.items.length / zone.capacity
    if (ratio < 0.5) return 'clean'
    if (ratio < 1) return 'cluttered'
    return 'chaotic'
  }

  return (
    <Card className="w-full max-w-6xl bg-gray-950 border-gray-800 text-gray-100">
      <CardHeader className="border-b border-gray-900 pb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Box className="w-6 h-6 text-giovanni-accent" />
            <CardTitle className="text-2xl font-bold uppercase tracking-tight italic">Studio Organizer</CardTitle>
          </div>
          <Button 
            onClick={getSuggestions} 
            variant="outline" 
            size="sm"
            className="border-gray-800 hover:border-giovanni-accent text-gray-400 hover:text-white transition-all font-bold"
          >
            <Lightbulb className="w-4 h-4 mr-2" />
            GET GIOVANNI'S ADVICE
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-6 pt-6">
        {/* Overall Vital Signs */}
        <div className="grid grid-cols-3 gap-4">
          <StatCard
            label="Total Assets"
            value={zones.reduce((sum, z) => sum + z.items.length, 0)}
            icon={<Box className="w-5 h-5" />}
            color="text-blue-400"
          />
          <StatCard
            label="Optimized Zones"
            value={zones.filter(z => getZoneStatus(z) === 'clean').length}
            icon={<CheckCircle className="w-5 h-5" />}
            color="text-green-400"
          />
          <StatCard
            label="Chaotic Points"
            value={zones.filter(z => getZoneStatus(z) === 'chaotic').length}
            icon={<AlertCircle className="w-5 h-5" />}
            color="text-red-400"
          />
        </div>

        {/* The Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {zones.map((zone, index) => (
            <motion.div
              key={zone.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <DeskZoneCard
                zone={zone}
                status={getZoneStatus(zone)}
                categories={categories}
                onAddItem={addItem}
                onRemoveItem={removeItem}
                newItemName={newItemName}
                setNewItemName={setNewItemName}
              />
            </motion.div>
          ))}
        </div>

        {/* Philosophy Footer */}
        <div className="bg-gradient-to-r from-giovanni-primary/10 to-transparent rounded-lg p-4 border border-giovanni-primary/20">
          <h3 className="text-xs font-black mb-1 flex items-center gap-2 uppercase tracking-widest text-giovanni-primary">
            <Lightbulb className="w-4 h-4" />
            Sovereign Organization
          </h3>
          <p className="text-[10px] text-gray-500 font-medium leading-relaxed">
            "Organization isn't about having a perfect desk. It's about knowing where your gear is when the inspiration hits.
            Your creative chaos is valid—just make it work for you, not against you."
          </p>
        </div>
      </CardContent>
    </Card>
  )
}

function DeskZoneCard({
  zone,
  status,
  categories,
  onAddItem,
  onRemoveItem,
  newItemName,
  setNewItemName
}: {
  zone: DeskZone
  status: 'clean' | 'cluttered' | 'chaotic'
  categories: { name: ItemCategory; icon: string; color: string }[]
  onAddItem: (zoneName: string, category: ItemCategory) => void
  onRemoveItem: (zoneId: string, itemId: string) => void
  newItemName: string
  setNewItemName: (name: string) => void
}) {
  const [isAdding, setIsAdding] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<ItemCategory>('equipment')

  const statusColors = {
    clean: 'border-green-500/20 bg-green-500/5',
    cluttered: 'border-yellow-500/20 bg-yellow-500/5',
    chaotic: 'border-red-500/20 bg-red-500/5'
  }

  return (
    <div className={`bg-gray-900/40 backdrop-blur-md rounded-lg p-5 border ${statusColors[status]} transition-all`}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-bold text-lg tracking-tight uppercase">
            {zone.name}
          </h3>
          <p className="text-[10px] text-gray-500 font-mono">
            CAPACITY: {zone.items.length} / {zone.capacity}
          </p>
        </div>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => setIsAdding(!isAdding)}
          className="text-[10px] font-black uppercase tracking-widest text-giovanni-accent hover:bg-giovanni-accent/10"
        >
          {isAdding ? 'CANCEL' : '+ ADD ASSET'}
        </Button>
      </div>

      {isAdding && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="mb-4 p-4 bg-gray-950 rounded-lg border border-gray-800"
        >
          <Input
            placeholder="Asset name..."
            value={newItemName}
            onChange={(e) => setNewItemName(e.target.value)}
            className="mb-3 bg-gray-900 border-gray-800 font-bold"
          />
          <div className="flex justify-around items-center pt-2">
            {categories.map(cat => (
              <button
                key={cat.name}
                onClick={() => {
                  setSelectedCategory(cat.name)
                  if (newItemName.trim()) {
                    onAddItem(zone.name, cat.name)
                    setIsAdding(false)
                  }
                }}
                className={`text-2xl hover:scale-125 transition-transform p-2 rounded-full hover:bg-gray-800 ${
                  selectedCategory === cat.name ? 'bg-gray-800 scale-110 shadow-[0_0_10px_rgba(255,255,255,0.1)]' : 'grayscale opacity-50'
                }`}
                title={cat.name}
              >
                {cat.icon}
              </button>
            ))}
          </div>
        </motion.div>
      )}

      <div className="space-y-2">
        {zone.items.length === 0 ? (
          <div className="text-center py-10 text-gray-700 text-xs font-mono uppercase tracking-widest">
            Awaiting Hardware
          </div>
        ) : (
          zone.items.map((item, index) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className="flex items-center justify-between p-3 bg-gray-950/50 rounded border border-gray-800 group hover:border-gray-600 transition-colors"
            >
              <div className="flex items-center gap-3">
                <span className="text-xl">
                  {categories.find(c => c.name === item.category)?.icon}
                </span>
                <div>
                  <div className="text-sm font-bold text-gray-200 uppercase tracking-tight">{item.name}</div>
                  <div className="text-[9px] text-gray-600 font-black uppercase tracking-[0.2em]">{item.category}</div>
                </div>
              </div>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => onRemoveItem(zone.id, item.id)}
                className="opacity-0 group-hover:opacity-100 text-gray-600 hover:text-red-400 transition-all"
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </motion.div>
          ))
        )}
      </div>
    </div>
  )
}

function StatCard({
  label,
  value,
  icon,
  color
}: {
  label: string
  value: number
  icon: React.ReactNode
  color: string
}) {
  return (
    <div className="bg-gray-900/40 backdrop-blur-md rounded-lg p-4 border border-gray-800">
      <div className={`flex items-center gap-2 mb-2 ${color} opacity-80`}>
        {icon}
        <span className="text-[10px] text-gray-500 font-black uppercase tracking-widest">{label}</span>
      </div>
      <div className="text-2xl font-black tracking-tighter">{value}</div>
    </div>
  )
}

const defaultZones: DeskZone[] = [
  {
    id: 'zone-1',
    name: 'Primary Command',
    items: [
      {
        id: 'item-1',
        name: 'Mac Studio M2',
        category: 'equipment',
        location: 'Primary Command',
        status: 'organized',
        lastSeen: new Date()
      }
    ],
    capacity: 5,
    status: 'clean'
  },
  {
    id: 'zone-2',
    name: 'Vocal Chain',
    items: [],
    capacity: 8,
    status: 'clean'
  },
  {
    id: 'zone-3',
    name: 'Visual Assets',
    items: [],
    capacity: 6,
    status: 'clean'
  },
  {
    id: 'zone-4',
    name: 'Cognitive Hub',
    items: [],
    capacity: 6,
    status: 'clean'
  }
]
