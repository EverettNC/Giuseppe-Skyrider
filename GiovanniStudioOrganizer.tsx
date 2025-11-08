import { useState } from 'react'
import { motion } from 'framer-motion'
import { Box, Trash2, CheckCircle, AlertCircle, Lightbulb } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card'
import { Button } from './components/ui/button'
import { Input } from './components/ui/input'
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

  /**
   * Add new item to desk
   */
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

    speak(`${newItemName} added to ${zoneName}. Keep that organization flowing!`, 'caring')
  }

  /**
   * Remove item from desk
   */
  const removeItem = (zoneId: string, itemId: string) => {
    setZones(zones.map(zone =>
      zone.id === zoneId
        ? { ...zone, items: zone.items.filter(i => i.id !== itemId) }
        : zone
    ))

    speak('Decluttered! Your space, your rules.', 'swagger')
  }

  /**
   * Get organization suggestions from Giovanni
   */
  const getSuggestions = () => {
    const totalItems = zones.reduce((sum, zone) => sum + zone.items.length, 0)
    const chaoticZones = zones.filter(z => z.items.length > z.capacity)

    if (totalItems === 0) {
      speak("Your desk is empty. Either you're a minimalist god or you haven't started tracking yet.", 'sassy')
      return
    }

    if (chaoticZones.length > 0) {
      const zoneName = chaoticZones[0].name
      speak(
        `${zoneName} is looking a little crowded, babe. Time to redistribute or declutter. Organization isn't about perfection—it's about knowing where your chaos lives.`,
        'caring'
      )
    } else {
      speak(
        `Your desk game is strong! Everything's in its place. That's that executive energy I love to see.`,
        'hype'
      )
    }
  }

  /**
   * Calculate zone status
   */
  const getZoneStatus = (zone: DeskZone): 'clean' | 'cluttered' | 'chaotic' => {
    const ratio = zone.items.length / zone.capacity
    if (ratio < 0.5) return 'clean'
    if (ratio < 1) return 'cluttered'
    return 'chaotic'
  }

  return (
    <Card className="w-full max-w-6xl">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Box className="w-6 h-6 text-giovanni-accent" />
            <CardTitle>Studio & Desk Organizer</CardTitle>
          </div>
          <Button onClick={getSuggestions} variant="outline" size="sm">
            <Lightbulb className="w-4 h-4 mr-2" />
            Get Giovanni's Advice
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Overall stats */}
        <div className="grid grid-cols-3 gap-4">
          <StatCard
            label="Total Items"
            value={zones.reduce((sum, z) => sum + z.items.length, 0)}
            icon={<Box className="w-5 h-5" />}
            color="text-blue-400"
          />
          <StatCard
            label="Clean Zones"
            value={zones.filter(z => getZoneStatus(z) === 'clean').length}
            icon={<CheckCircle className="w-5 h-5" />}
            color="text-green-400"
          />
          <StatCard
            label="Needs Attention"
            value={zones.filter(z => getZoneStatus(z) === 'chaotic').length}
            icon={<AlertCircle className="w-5 h-5" />}
            color="text-red-400"
          />
        </div>

        {/* Desk zones */}
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

        {/* Organization tips from Giovanni */}
        <div className="bg-gradient-to-r from-giovanni-primary/20 to-giovanni-accent/20 rounded-lg p-4 border border-giovanni-primary/30">
          <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
            <Lightbulb className="w-4 h-4" />
            Giovanni's Organization Philosophy
          </h3>
          <p className="text-xs text-gray-300">
            "Organization isn't about having a perfect desk. It's about knowing where your shit is when you need it.
            Your creative chaos is valid—just make it work for you, not against you."
          </p>
        </div>
      </CardContent>
    </Card>
  )
}

/**
 * Individual desk zone card
 */
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
    clean: 'border-green-500/30 bg-green-500/5',
    cluttered: 'border-yellow-500/30 bg-yellow-500/5',
    chaotic: 'border-red-500/30 bg-red-500/5'
  }

  const statusIcons = {
    clean: <CheckCircle className="w-4 h-4 text-green-500" />,
    cluttered: <AlertCircle className="w-4 h-4 text-yellow-500" />,
    chaotic: <AlertCircle className="w-4 h-4 text-red-500" />
  }

  return (
    <div className={`bg-gray-800 rounded-lg p-4 border ${statusColors[status]}`}>
      {/* Zone header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-semibold flex items-center gap-2">
            {zone.name}
            {statusIcons[status]}
          </h3>
          <p className="text-xs text-gray-400">
            {zone.items.length} / {zone.capacity} items
          </p>
        </div>
        <Button
          size="sm"
          variant="outline"
          onClick={() => setIsAdding(!isAdding)}
        >
          {isAdding ? 'Cancel' : '+ Add Item'}
        </Button>
      </div>

      {/* Add item form */}
      {isAdding && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mb-4 p-3 bg-gray-900 rounded-lg border border-gray-700"
        >
          <Input
            placeholder="Item name..."
            value={newItemName}
            onChange={(e) => setNewItemName(e.target.value)}
            className="mb-2"
          />
          <div className="flex gap-2">
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
                className={`text-2xl hover:scale-110 transition-transform ${
                  selectedCategory === cat.name ? 'scale-125' : ''
                }`}
                title={cat.name}
              >
                {cat.icon}
              </button>
            ))}
          </div>
        </motion.div>
      )}

      {/* Items list */}
      <div className="space-y-2">
        {zone.items.length === 0 ? (
          <div className="text-center py-8 text-gray-500 text-sm">
            Empty zone. Add items to track them.
          </div>
        ) : (
          zone.items.map((item, index) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className="flex items-center justify-between p-2 bg-gray-900 rounded border border-gray-700 hover:border-gray-600 transition-colors"
            >
              <div className="flex items-center gap-2">
                <span className="text-lg">
                  {categories.find(c => c.name === item.category)?.icon}
                </span>
                <div>
                  <div className="text-sm font-medium">{item.name}</div>
                  <div className="text-xs text-gray-500">{item.category}</div>
                </div>
              </div>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => onRemoveItem(zone.id, item.id)}
                className="hover:text-red-400"
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

/**
 * Stat card component
 */
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
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <div className={`flex items-center gap-2 mb-2 ${color}`}>
        {icon}
        <span className="text-xs text-gray-400">{label}</span>
      </div>
      <div className="text-2xl font-bold">{value}</div>
    </div>
  )
}

/**
 * Default desk zones
 */
const defaultZones: DeskZone[] = [
  {
    id: 'zone-1',
    name: 'Main Workspace',
    items: [
      {
        id: 'item-1',
        name: 'Camera',
        category: 'equipment',
        location: 'Main Workspace',
        status: 'organized',
        lastSeen: new Date()
      }
    ],
    capacity: 5,
    status: 'clean'
  },
  {
    id: 'zone-2',
    name: 'Cable Station',
    items: [],
    capacity: 10,
    status: 'clean'
  },
  {
    id: 'zone-3',
    name: 'Props & Accessories',
    items: [],
    capacity: 8,
    status: 'clean'
  },
  {
    id: 'zone-4',
    name: 'Document Area',
    items: [],
    capacity: 6,
    status: 'clean'
  }
]
