import { useEffect, useRef } from 'react'
import { useGiovanniStore } from './GiovanniStore'
import { giovanni } from './GiovanniPersonality'
import { TaskEntry, getCurrentTask, getUpcomingTasks } from './GiuseppeScheduler'

/**
 * GiovanniReminders - Proactive reminder system with personality
 * Monitors schedule and triggers notifications through Giovanni
 */
export function GiovanniReminders() {
  const { speak } = useGiovanniStore()
  const lastReminderRef = useRef<string | null>(null)
  const checkIntervalRef = useRef<number>()

  useEffect(() => {
    // Check for tasks every minute
    const checkReminders = async () => {
      try {
        // Check current task
        const currentTask = await getCurrentTask()

        if (currentTask) {
          const taskId = `${currentTask.datetime_utc}-${currentTask.label}`

          // Only remind once per task
          if (lastReminderRef.current !== taskId) {
            handleTask(currentTask)
            lastReminderRef.current = taskId
          }
        }

        // Check upcoming tasks (within next 15 minutes)
        const upcomingTasks = await getUpcomingTasks(15)

        upcomingTasks.forEach((task) => {
          const minutesUntil = getMinutesUntil(task.datetime_utc)

          // Remind at 15 min, 10 min, and 5 min marks
          if ([15, 10, 5].includes(minutesUntil)) {
            const taskId = `${task.datetime_utc}-${task.label}-${minutesUntil}`

            if (lastReminderRef.current !== taskId) {
              handleUpcomingTask(task, minutesUntil)
              lastReminderRef.current = taskId
            }
          }
        })
      } catch (error) {
        console.error('Error checking reminders:', error)
      }
    }

    // Initial check
    checkReminders()

    // Set up interval (check every 60 seconds)
    checkIntervalRef.current = window.setInterval(checkReminders, 60000)

    // Cleanup
    return () => {
      if (checkIntervalRef.current) {
        clearInterval(checkIntervalRef.current)
      }
    }
  }, [speak])

  /**
   * Handle current task based on type
   */
  const handleTask = (task: TaskEntry) => {
    const metadata = task.metadata || {}

    if (task.platforms.includes('medication')) {
      // Medication reminder
      const sassLevel = metadata.sass_level || 'medium'
      const response = giovanni.getMedicationReminder(sassLevel as 'low' | 'medium' | 'high')

      // Use custom caption if available, otherwise use generated
      const message = task.caption || response.text

      speak(message, response.mood)
    } else if (task.platforms.includes('reminder')) {
      // General reminder (hydration, breaks, etc.)
      const type = metadata.type || 'general'

      let response
      if (type === 'wellness' && task.label.includes('Hydration')) {
        response = giovanni.getHydrationReminder()
      } else {
        response = { text: task.caption, mood: 'caring' as const }
      }

      speak(response.text, response.mood)
    } else {
      // Content posting task
      const vibe = metadata.vibe || 'powerful_bitch_energy'
      const response = giovanni.getContentSuggestion(vibe)

      speak(`Time to post: ${task.label}. ${response.text}`, response.mood)
    }
  }

  /**
   * Handle upcoming task warnings
   */
  const handleUpcomingTask = (task: TaskEntry, minutesUntil: number) => {
    const timeStr = `${minutesUntil} minute${minutesUntil !== 1 ? 's' : ''}`

    let urgency: 'gentle' | 'urgent' | 'sass' = 'gentle'

    if (minutesUntil <= 5) {
      urgency = 'urgent'
    } else if (task.metadata?.importance === 'critical') {
      urgency = 'sass'
    }

    const response = giovanni.getTaskReminder(task.label, timeStr, urgency)
    speak(response.text, response.mood)
  }

  /**
   * Calculate minutes until a given UTC datetime
   */
  const getMinutesUntil = (datetimeUtc: string): number => {
    const now = new Date()
    const target = new Date(datetimeUtc)
    const diffMs = target.getTime() - now.getTime()
    return Math.floor(diffMs / 60000)
  }

  // This component doesn't render anything
  return null
}

/**
 * Hydration reminder hook - checks every hour
 */
export function useHydrationReminder() {
  const { speak } = useGiovanniStore()

  useEffect(() => {
    // Remind to drink water every 2 hours
    const interval = setInterval(() => {
      const response = giovanni.getHydrationReminder()
      speak(response.text, response.mood)
    }, 2 * 60 * 60 * 1000) // 2 hours

    return () => clearInterval(interval)
  }, [speak])
}

/**
 * Morning motivation hook - triggers at session start
 */
export function useMorningMotivation() {
  const { speak } = useGiovanniStore()

  useEffect(() => {
    // Give user a moment to settle in
    const timeout = setTimeout(() => {
      const response = giovanni.getGreeting('swagger')
      speak(response.text, response.mood)
    }, 2000)

    return () => clearTimeout(timeout)
  }, [speak])
}
