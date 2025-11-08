import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { getAllTasks, getCurrentTask, getUpcomingTasks, TaskEntry } from "./GiuseppeScheduler";
import { useGiovanniStore } from "./GiovanniStore";
import { giovanni } from "./GiovanniPersonality";
import { Calendar, Mic, MicOff, Clock, Pill, Zap } from "lucide-react";

export function GiuseppePanel() {
  const [tasks, setTasks] = useState<TaskEntry[]>([]);
  const [recording, setRecording] = useState(false);
  const [currentTask, setCurrentTask] = useState<TaskEntry | null>(null);
  const [upcomingTasks, setUpcomingTasks] = useState<TaskEntry[]>([]);
  const { speak } = useGiovanniStore();

  useEffect(() => {
    loadAllTasks();
    // Refresh every minute
    const interval = setInterval(loadAllTasks, 60000);
    return () => clearInterval(interval);
  }, []);

  const loadAllTasks = async () => {
    try {
      const allTasks = await getAllTasks();
      setTasks(allTasks);

      const current = await getCurrentTask();
      setCurrentTask(current);

      const upcoming = await getUpcomingTasks(120); // Next 2 hours
      setUpcomingTasks(upcoming);
    } catch (error) {
      console.error("Schedule load error:", error);
    }
  };

  const toggleRecording = () => {
    setRecording(!recording);

    if (!recording) {
      // Starting recording
      speak("Recording started. Let that creative flow happen.", "swagger");
      // TODO: Integrate Web Audio / MediaRecorder here
      console.log("Starting recording...");
    } else {
      // Stopping recording
      speak("Recording stopped. That was fire. Want me to summarize it?", "hype");
      console.log("Stopping recording...");
    }
  };

  const formatTime = (utcDateString: string) => {
    const date = new Date(utcDateString);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const getTaskIcon = (task: TaskEntry) => {
    if (task.platforms.includes('medication')) {
      return <Pill className="w-5 h-5 text-red-400" />;
    }
    if (task.platforms.includes('reminder')) {
      return <Clock className="w-5 h-5 text-yellow-400" />;
    }
    return <Zap className="w-5 h-5 text-giovanni-accent" />;
  };

  return (
    <div className="space-y-6">
      {/* Current Task */}
      {currentTask && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="giovanni-glow"
        >
          <Card className="border-giovanni-primary bg-gradient-to-br from-giovanni-primary/10 to-transparent">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {getTaskIcon(currentTask)}
                <span>Now: {currentTask.label}</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-300 mb-4">{currentTask.caption}</p>
              {currentTask.hashtags && currentTask.hashtags.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {currentTask.hashtags.map((tag) => (
                    <span key={tag} className="text-xs px-2 py-1 bg-giovanni-accent/20 text-giovanni-accent rounded-full">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Recording Control */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {recording ? (
                <Mic className="w-5 h-5 text-red-500 animate-pulse" />
              ) : (
                <MicOff className="w-5 h-5 text-gray-500" />
              )}
              <div>
                <span className="font-medium block">Voice Recording</span>
                <span className="text-xs text-gray-400">
                  {recording ? "Recording in progress..." : "Ready to record"}
                </span>
              </div>
            </div>
            <Switch checked={recording} onCheckedChange={toggleRecording} />
          </div>
        </CardContent>
      </Card>

      {/* Upcoming Tasks */}
      {upcomingTasks.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              Coming Up
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {upcomingTasks.map((task, index) => (
                <motion.div
                  key={`${task.datetime_utc}-${task.label}`}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start gap-3 p-3 bg-gray-800/50 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors"
                >
                  {getTaskIcon(task)}
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-sm">{task.label}</span>
                      <span className="text-xs text-gray-400">{formatTime(task.datetime_utc)}</span>
                    </div>
                    <p className="text-xs text-gray-400">{task.caption}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* All Tasks Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Today's Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-giovanni-accent">{tasks.length}</div>
              <div className="text-xs text-gray-400">Total Tasks</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-red-400">
                {tasks.filter(t => t.platforms.includes('medication')).length}
              </div>
              <div className="text-xs text-gray-400">Medications</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-yellow-400">
                {tasks.filter(t => !t.platforms.includes('medication') && !t.platforms.includes('reminder')).length}
              </div>
              <div className="text-xs text-gray-400">Content Posts</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

