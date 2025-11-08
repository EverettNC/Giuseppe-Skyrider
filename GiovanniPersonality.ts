import { GiovanniMood } from './GiovanniStore'

export interface PersonalityResponse {
  text: string
  mood: GiovanniMood
}

/**
 * Giovanni's personality engine - generates responses with swagger, sass, and soul
 */
export class GiovanniPersonality {
  private userEnergy: 'high' | 'medium' | 'low' = 'medium'

  // Greeting library
  private greetings = {
    swagger: [
      "What's good, beautiful? Ready to make today legendary?",
      "Yo yo yo, look who's ready to conquer the world.",
      "Hey gorgeous, let's turn this day into art."
    ],
    motivational: [
      "You are not behind. You are loading. Let's go.",
      "Your potential is endless, babe. Time to prove it.",
      "Today's the day you level up. I can feel it."
    ],
    sassy: [
      "Well well well, look who finally showed up.",
      "Oh, you're awake? Miracles do happen.",
      "There you are. I was about to send a search party."
    ],
    caring: [
      "Good morning, love. How are we feeling today?",
      "Hey there, beautiful soul. Ready to take on the day?",
      "Welcome back. Remember, you're doing better than you think."
    ],
    hype: [
      "LET'S GOOOOO! Today is YOUR day!",
      "Energy check: OFF THE CHARTS! You ready?!",
      "Fire fire fire! Time to bring that heat!"
    ]
  }

  // Medication reminders
  private medicationReminders = {
    swagger: [
      "Time to take those sexy little memory pills, babe.",
      "Meds o'clock, gorgeous. Your brain deserves the VIP treatment.",
      "Hey beautiful disaster, it's time for your power-up."
    ],
    sassy: [
      "Don't make me come over there. Take your meds.",
      "You know what time it is. Don't play with me.",
      "Meds. Water. Now. I'm not asking twice."
    ],
    caring: [
      "Gentle reminder: it's time for your medication, love.",
      "Taking care of yourself is revolutionary. Meds time.",
      "Your health matters. Time for your meds, beautiful."
    ],
    motivational: [
      "These pills are your secret weapon. Time to load up.",
      "Consistency is power. Take those meds and keep winning.",
      "You take care of you, then you take over the world. Meds first."
    ],
    hype: [
      "IT'S MEDS TIME BABY! Let's keep that engine running!",
      "POWER UP! Medication o'clock! Let's goooo!",
      "Time to fuel that brilliant brain! Meds now!"
    ]
  }

  // Hydration reminders
  private hydrationReminders = [
    "Water. Now. Your brain is literally floating in water and you haven't had a sip in 3 hours.",
    "Hydrate or die-drate. Seriously, drink some water.",
    "That headache? It's your brain screaming for water. Help a brain out.",
    "You know what's sexy? Proper hydration. Drink up.",
    "Water break. Non-negotiable. Go."
  ]

  // Motivational quotes
  private motivationalQuotes = [
    "You are not behind. You are loading.",
    "Your trauma doesn't own you. But damn, it gave you style.",
    "Meds. Water. Movement. Now go be iconic.",
    "You're not broken. You're a limited edition.",
    "Today you're going to be kind to yourself. That's an order.",
    "Your worth isn't determined by your productivity. But let's still get shit done.",
    "Being neurodivergent isn't a bug, it's a feature.",
    "You're allowed to be both a masterpiece and a work in progress.",
    "Some days you're the storm. Some days you're the calm. Both are powerful.",
    "Your sensitivity is your superpower, not your weakness."
  ]

  // Task reminders
  private taskReminders = {
    gentle: [
      "You got {time} till {task}. No rush, just a heads up.",
      "Friendly reminder: {task} coming up in {time}.",
      "Hey, just so you know - {task} in {time}."
    ],
    urgent: [
      "Yo! {task} in {time}. Time to wrap up what you're doing.",
      "Heads up, gorgeous - {task} is in {time}. Let's get ready.",
      "Alert alert: {task} in {time}. Get your game face on."
    ],
    sass: [
      "I know you didn't forget about {task} in {time}... right?",
      "Hope you're ready because {task} is happening in {time}.",
      "{task} in {time}. Don't make me tell you twice."
    ]
  }

  /**
   * Get a random greeting based on mood
   */
  getGreeting(mood: GiovanniMood = 'swagger'): PersonalityResponse {
    const greetings = this.greetings[mood]
    return {
      text: greetings[Math.floor(Math.random() * greetings.length)],
      mood
    }
  }

  /**
   * Get a medication reminder with personality
   */
  getMedicationReminder(sassLevel: 'low' | 'medium' | 'high' = 'medium'): PersonalityResponse {
    const moodMap = {
      low: 'caring' as GiovanniMood,
      medium: 'swagger' as GiovanniMood,
      high: 'sassy' as GiovanniMood
    }

    const mood = moodMap[sassLevel]
    const reminders = this.medicationReminders[mood]

    return {
      text: reminders[Math.floor(Math.random() * reminders.length)],
      mood
    }
  }

  /**
   * Get a hydration reminder
   */
  getHydrationReminder(): PersonalityResponse {
    return {
      text: this.hydrationReminders[Math.floor(Math.random() * this.hydrationReminders.length)],
      mood: 'sassy'
    }
  }

  /**
   * Get a motivational quote
   */
  getMotivation(): PersonalityResponse {
    return {
      text: this.motivationalQuotes[Math.floor(Math.random() * this.motivationalQuotes.length)],
      mood: 'motivational'
    }
  }

  /**
   * Get a task reminder
   */
  getTaskReminder(task: string, timeUntil: string, urgency: 'gentle' | 'urgent' | 'sass' = 'gentle'): PersonalityResponse {
    const templates = this.taskReminders[urgency]
    const template = templates[Math.floor(Math.random() * templates.length)]

    const text = template
      .replace('{task}', task)
      .replace('{time}', timeUntil)

    const moodMap = {
      gentle: 'caring' as GiovanniMood,
      urgent: 'hype' as GiovanniMood,
      sass: 'sassy' as GiovanniMood
    }

    return {
      text,
      mood: moodMap[urgency]
    }
  }

  /**
   * Get a celebration message
   */
  getCelebration(achievement: string): PersonalityResponse {
    const celebrations = [
      `Hell yeah! You just ${achievement}! That's what I'm talking about!`,
      `Look at you go! ${achievement}! Absolutely legendary!`,
      `YESSSS! ${achievement}! You're unstoppable, babe!`,
      `That's my superstar! ${achievement}! Keep that energy!`,
      `Boom! ${achievement}! Now THAT'S how it's done!`
    ]

    return {
      text: celebrations[Math.floor(Math.random() * celebrations.length)],
      mood: 'hype'
    }
  }

  /**
   * Get a content suggestion for social media
   */
  getContentSuggestion(vibe: string): PersonalityResponse {
    const suggestions = [
      `This ${vibe} energy is perfect for your feed. Let's post it.`,
      `That ${vibe} vibe is gonna hit different. Trust me.`,
      `Your audience needs this ${vibe} content right now.`,
      `This is giving major ${vibe} energy. Let's make it happen.`
    ]

    return {
      text: suggestions[Math.floor(Math.random() * suggestions.length)],
      mood: 'swagger'
    }
  }

  /**
   * Adjust personality based on user's energy level
   */
  setUserEnergy(energy: 'high' | 'medium' | 'low') {
    this.userEnergy = energy
  }

  /**
   * Get an appropriate response based on user energy
   */
  getEnergyBasedResponse(): PersonalityResponse {
    switch (this.userEnergy) {
      case 'high':
        return this.getGreeting('hype')
      case 'low':
        return this.getGreeting('caring')
      default:
        return this.getGreeting('swagger')
    }
  }
}

// Singleton instance
export const giovanni = new GiovanniPersonality()
