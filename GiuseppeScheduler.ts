// GiuseppeScheduler.ts
// Root-level logic controller for loading, managing, and querying schedule data.
// Follows Rules to Code By: proximity, visibility, and clarity.

export interface TaskEntry {
  platforms: string[];
  datetime_utc: string;
  label: string;
  video_filename: string;
  thumbnail_filename: string;
  caption: string;
  hashtags: string[];
  metadata?: {
    type?: string;
    importance?: string;
    sass_level?: string;
    vibe?: string;
    target_engagement?: string;
    [key: string]: any;
  };
}

interface ScheduleData {
  schedule: TaskEntry[];
}

let schedule: TaskEntry[] = [];
let isLoaded = false;

export async function loadSchedule(path: string = "/demo_schedule_2025w45.json"): Promise<TaskEntry[]> {
  try {
    const res = await fetch(path);
    if (!res.ok) throw new Error("Failed to load schedule JSON");
    const data: ScheduleData = await res.json();
    schedule = data.schedule || [];
    isLoaded = true;
    return schedule;
  } catch (error) {
    console.error("Error loading schedule:", error);
    throw error;
  }
}

export async function getAllTasks(): Promise<TaskEntry[]> {
  if (!isLoaded) {
    await loadSchedule();
  }
  return schedule;
}

export async function getCurrentTask(now: Date = new Date()): Promise<TaskEntry | null> {
  if (!isLoaded) {
    await loadSchedule();
  }

  const nowTime = now.getTime();
  return (
    schedule.find((entry) => {
      const entryTime = new Date(entry.datetime_utc).getTime();
      return Math.abs(entryTime - nowTime) < 30 * 60 * 1000; // ±30 mins
    }) || null
  );
}

export async function getUpcomingTasks(withinMinutes: number = 120): Promise<TaskEntry[]> {
  if (!isLoaded) {
    await loadSchedule();
  }

  const nowTime = Date.now();
  return schedule.filter((entry) => {
    const entryTime = new Date(entry.datetime_utc).getTime();
    return entryTime > nowTime && entryTime - nowTime <= withinMinutes * 60 * 1000;
  });
}

