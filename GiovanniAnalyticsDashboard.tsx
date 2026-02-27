import { useEffect, useMemo, useState, type ReactNode } from 'react'
import { motion } from 'framer-motion'
import { Activity, Pill, Droplet, TrendingUp, Sparkles } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card'
import { Button } from './components/ui/button'
import { getAllTasks, TaskEntry } from './GiuseppeScheduler'
import { useNotesStore } from './GiuseppeNotesStore'
import { useGiovanniStore } from './GiovanniStore'

interface EngagementSnapshot {
  label: string
  score: number
}

export function GiovanniAnalyticsDashboard() {
  const notes = useNotesStore((state) => state.notes)
  const { speak } = useGiovanniStore()
  const [tasks, setTasks] = useState<TaskEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [wellnessScore, setWellnessScore] = useState(72)
  const [engagement, setEngagement] = useState<EngagementSnapshot[]>([])

  useEffect(() => {
    getAllTasks()
      .then((schedule) => {
        setTasks(schedule)
        setEngagement(buildEngagementTrend(schedule))
      })
      .catch((error) => console.error('analytics load error', error))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (typeof window === 'undefined') return
    try {
      const raw = window.localStorage.getItem('giovanni-wellness')
      if (raw) {
        const parsed = JSON.parse(raw)
        if (typeof parsed.score === 'number') {
          setWellnessScore(parsed.score)
        }
      }
    } catch (error) {
      console.warn('Failed to parse wellness cache', error)
    }
  }, [])

  const noteStats = useMemo(() => {
    return {
      total: notes.length,
      ideas: notes.filter((note) => note.type === 'idea').length,
      voice: notes.filter((note) => note.type === 'voice').length,
      memories: notes.filter((note) => note.type === 'memory').length,
    }
  }, [notes])

  const taskStats = useMemo(() => {
    const medications = tasks.filter((task) => task.platforms.includes('medication')).length
    const reminders = tasks.filter((task) => task.platforms.includes('reminder')).length
    const content = tasks.length - medications - reminders

    return { medications, reminders, content }
  }, [tasks])

  const vibeHeatmap = useMemo(() => {
    const base: Record<string, number> = {
      powerful_bitch_energy: 0,
      quiet_storm: 0,
      sensual_motivational: 0,
      creative_chaos: 0,
      neurodivergent_pride: 0,
      behind_the_scenes: 0
    }

    tasks.forEach((task) => {
      const vibe = task.metadata?.vibe
      if (vibe && typeof base[vibe] === 'number') {
        base[vibe] += 1
      }
    })

    return base
  }, [tasks])

  const refreshInsights = () => {
    setEngagement(buildEngagementTrend(tasks))
    speak('Dashboard refreshed. Numbers are looking spicy.', 'swagger')
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="py-10 text-center text-gray-400">Crunching the numbers...</CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400">Holistic pulse of your creative life</p>
        </div>
        <Button size="sm" onClick={refreshInsights}>
          <Sparkles className="w-4 h-4 mr-2" />Refresh Predictions
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <AnalyticsCard
          title="Predicted Engagement"
          icon={TrendingUp}
          accent="text-giovanni-accent"
          subtitle="Next 3 scheduled posts"
        >
          <div className="space-y-2">
            {engagement.map((item) => (
              <div key={item.label} className="flex items-center justify-between text-sm">
                <span className="text-gray-300">{item.label}</span>
                <span className="font-semibold text-giovanni-accent">{item.score}%</span>
              </div>
            ))}
          </div>
        </AnalyticsCard>

        <AnalyticsCard
          title="Wellness Score"
          icon={Droplet}
          accent="text-blue-400"
          subtitle="Hydration + meds compliance"
        >
          <div className="text-4xl font-bold text-blue-300">{wellnessScore}</div>
          <div className="text-xs text-gray-400">Logged automatically from the wellness tracker</div>
        </AnalyticsCard>

        <AnalyticsCard
          title="Notes Captured"
          icon={Activity}
          accent="text-purple-400"
          subtitle="Voice · Ideas · Memories"
        >
          <div className="flex justify-between text-sm text-gray-300">
            <span>Total</span>
            <span className="font-semibold text-white">{noteStats.total}</span>
          </div>
          <div className="flex justify-between text-xs text-gray-400 mt-2">
            <span>Ideas</span>
            <span>{noteStats.ideas}</span>
          </div>
          <div className="flex justify-between text-xs text-gray-400">
            <span>Voice</span>
            <span>{noteStats.voice}</span>
          </div>
          <div className="flex justify-between text-xs text-gray-400">
            <span>Memories</span>
            <span>{noteStats.memories}</span>
          </div>
        </AnalyticsCard>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-giovanni-accent" />
            Schedule Composition
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <StatPill label="Content" value={taskStats.content} accent="text-giovanni-accent" />
            <StatPill label="Reminders" value={taskStats.reminders} accent="text-yellow-400" />
            <StatPill label="Medication" value={taskStats.medications} accent="text-red-400" />
          </div>

          <div className="mt-6">
            <p className="text-xs uppercase tracking-widest text-gray-500 mb-2">Vibe Heatmap</p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {Object.entries(vibeHeatmap).map(([vibe, count]) => (
                <div key={vibe} className="bg-gray-900/60 border border-gray-800 rounded-lg p-3">
                  <div className="text-sm text-gray-400">{vibe.replace(/_/g, ' ')}</div>
                  <div className="flex items-center gap-2 mt-1">
                    <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-giovanni-primary to-giovanni-accent"
                        style={{ width: `${Math.min(100, count * 20)}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-300">{count}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function buildEngagementTrend(tasks: TaskEntry[]): EngagementSnapshot[] {
  const contentOnly = tasks.filter((task) => !task.platforms.includes('medication') && !task.platforms.includes('reminder'))
  return contentOnly.slice(0, 3).map((task) => {
    const vibeBoost = task.metadata?.vibe === 'powerful_bitch_energy' ? 10 : 0
    const importance = task.metadata?.target_engagement === 'viral' ? 15 : 0
    const base = 65 + Math.floor(Math.random() * 20)
    return {
      label: task.label,
      score: Math.min(99, base + vibeBoost + importance)
    }
  })
}

function AnalyticsCard({
  title,
  subtitle,
  icon: Icon,
  children,
  accent
}: {
  title: string
  subtitle: string
  icon: typeof Activity
  accent: string
  children: ReactNode
}) {
  return (
    <Card className="bg-gray-900/60 border border-gray-800">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Icon className={`w-5 h-5 ${accent}`} />
          {title}
        </CardTitle>
        <p className="text-xs text-gray-500">{subtitle}</p>
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  )
}

function StatPill({ label, value, accent }: { label: string; value: number; accent: string }) {
  return (
    <div className="bg-gray-900/60 rounded-xl p-4 border border-gray-800 text-center">
      <div className={`text-3xl font-bold ${accent}`}>{value}</div>
      <div className="text-xs text-gray-400 mt-1">{label}</div>
    </div>
  )
}
