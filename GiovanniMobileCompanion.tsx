import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Smartphone, Calendar, Mic, Share2 } from 'lucide-react'
import { Button } from './components/ui/button'
import { Card, CardContent } from './components/ui/card'
import { getUpcomingTasks, TaskEntry } from './GiuseppeScheduler'
import { useNotesStore, type Note } from './GiuseppeNotesStore'
import { useGiovanniStore } from './GiovanniStore'

export function GiovanniMobileCompanion() {
  const recentNotes = useNotesStore((state) => state.notes.slice(0, 3))
  const { speak } = useGiovanniStore()
  const [upcomingTasks, setUpcomingTasks] = useState<TaskEntry[]>([])

  useEffect(() => {
    getUpcomingTasks(180)
      .then((tasks) => setUpcomingTasks(tasks))
      .catch((error) => console.error('mobile companion task error', error))
  }, [])

  const shareSnapshot = async () => {
    const summary = buildShareText(upcomingTasks, recentNotes)

    try {
      if (typeof navigator !== 'undefined' && navigator.share) {
        await navigator.share({ title: 'Giovanni Snapshot', text: summary })
      } else if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(summary)
      }
      speak('Snapshot pushed. Check your phone.', 'swagger')
    } catch (error) {
      console.warn('share failed', error)
      speak('Could not share to your phone. Copying failed.', 'sassy')
    }
  }

  return (
    <div className="flex justify-center">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-br from-gray-900 via-gray-950 to-black p-4 rounded-[2.5rem] shadow-2xl w-full max-w-md"
      >
        <div className="flex items-center justify-between text-gray-400 mb-4 px-2">
          <div className="flex items-center gap-2">
            <Smartphone className="w-5 h-5" />
            <span className="uppercase tracking-widest text-xs">Giovanni Pocket</span>
          </div>
          <Button size="sm" variant="ghost" onClick={shareSnapshot} className="text-giovanni-accent">
            <Share2 className="w-4 h-4 mr-1" />Sync
          </Button>
        </div>

        <div className="space-y-4">
          <Card className="bg-gray-900/70 border-gray-800">
            <CardContent className="p-4 space-y-2">
              <div className="flex items-center gap-2 text-gray-400 text-sm">
                <Calendar className="w-4 h-4 text-giovanni-accent" />
                Upcoming Tasks
              </div>
              {upcomingTasks.length === 0 ? (
                <p className="text-xs text-gray-500">Nothing scheduled. Use this moment.</p>
              ) : (
                upcomingTasks.slice(0, 3).map((task) => (
                  <div key={task.label} className="flex items-center justify-between text-xs text-gray-300">
                    <span>{task.label}</span>
                    <span className="text-gray-500">
                      {new Date(task.datetime_utc).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}
                    </span>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          <Card className="bg-gray-900/70 border-gray-800">
            <CardContent className="p-4 space-y-2">
              <div className="flex items-center gap-2 text-gray-400 text-sm">
                <Mic className="w-4 h-4 text-giovanni-accent" />
                Recent Notes
              </div>
              {recentNotes.length === 0 ? (
                <p className="text-xs text-gray-500">No notes yet. Tell me something and I'll sync it.</p>
              ) : (
                recentNotes.map((note) => (
                  <div key={note.id} className="text-xs text-gray-300 border-b border-gray-800 pb-2 last:border-none">
                    <div className="flex justify-between text-[10px] text-gray-500">
                      <span className="uppercase">{note.type}</span>
                      <span>{new Date(note.timestamp).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}</span>
                    </div>
                    <p>{note.summary || note.content}</p>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      </motion.div>
    </div>
  )
}

function buildShareText(tasks: TaskEntry[], notes: Note[]): string {
  const nextTask = tasks[0]
  const noteSnippet = notes[0]?.summary || notes[0]?.content || 'No notes yet'
  const taskLine = nextTask ? `${nextTask.label} at ${new Date(nextTask.datetime_utc).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}` : 'Open block'
  return `Next: ${taskLine}\nLast note: ${noteSnippet}`
}
