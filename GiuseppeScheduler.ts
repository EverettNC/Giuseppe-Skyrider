// GiuseppeScheduler.ts
// Root-level logic controller for loading, managing, and querying schedule data.
// Follows Rules to Code By: proximity, visibility, and clarity.

export interface TaskEntry {
  platforms: string;
  datetime_utc: string;
  label: string;
  video_filename: string;
  thumbnail_filename: string;
  caption: string;
  hashtags: string;
}

let schedule: TaskEntry[] = [];

export async function loadSchedule(path: string = "/demo_schedule_2025w45.json") {
  const res = await fetch(path);
  if (!res.ok) throw new Error("Failed to load schedule JSON");
  schedule = await res.json();
  return schedule;
}

export function getAllTasks(): TaskEntry[] {
  return schedule;
}

export function getCurrentTask(now: Date = new Date()): TaskEntry | null {
  const nowTime = now.getTime();
  return (
    schedule.find((entry) => {
      const entryTime = new Date(entry.datetime_utc).getTime();
      return Math.abs(entryTime - nowTime) < 30 * 60 * 1000; // ±30 mins
    }) || null
  );
}

export function getUpcomingTasks(withinMinutes: number = 120): TaskEntry[] {
  const nowTime = Date.now();
  return schedule.filter((entry) => {
    const entryTime = new Date(entry.datetime_utc).getTime();
    return entryTime > nowTime && entryTime - nowTime <= withinMinutes * 60 * 1000;
  });
}

