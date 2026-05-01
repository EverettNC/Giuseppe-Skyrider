import { useEffect, useState, useRef } from "react";
import { motion } from "framer-motion";
// "Nothing Vital Lives Below Root" - Imports flattened
import { Card, CardContent, CardHeader, CardTitle } from "./card";
import { Button } from "./button";
import { Switch } from "./switch";
import { getAllTasks, getCurrentTask, getUpcomingTasks, addTask, TaskEntry } from "./GiuseppeScheduler";
import { useGiovanniStore } from "./GiovanniStore";
import { giovanni } from "./GiovanniPersonality";
import { Calendar, Mic, MicOff, Clock, Pill, Zap, Loader2 } from "lucide-react";

export function GiuseppePanel() {
  const [tasks, setTasks] = useState<TaskEntry[]>([]);
  const [recording, setRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [actionState, setActionState] = useState<"idle" | "adapting">("idle");
  const [currentTask, setCurrentTask] = useState<TaskEntry | null>(null);
  const [upcomingTasks, setUpcomingTasks] = useState<TaskEntry[]>([]);
  const { speak, setFacsState } = useGiovanniStore();

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);

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
      
      const upcoming = await getUpcomingTasks(120);
      setUpcomingTasks(upcoming);
    } catch (error) {
      console.error("Failed to load tasks", error);
    }
  };

  const toggleRecording = () => {
    if (recording) {
      setRecording(false);
      setIsProcessing(true);
      // Simulate processing latency
      setTimeout(() => {
        setIsProcessing(false);
        setActionState("adapting");
        speak("I heard that. Adjusting the timeline now.", "motivational");
        setTimeout(() => setActionState("idle"), 3000);
      }, 1500);
    } else {
      setRecording(true);
      speak("I'm listening. Tell me what changed.", "caring");
    }
  };

  const formatTime = (isoString: string) => {
    return new Date(isoString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="flex flex-col h-full gap-4 p-4 text-gray-100 bg-gray-950">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-giovanni-primary tracking-tight">Giuseppe Panel</h2>
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-400">Autonomy Core:</span>
          <Switch checked={true} disabled className="data-[state=checked]:bg-green-500" />
        </div>
      </div>

      {/* Carbon Input / Action Center */}
      <Card className={`border-2 transition-colors ${recording ? 'border-red-500/50 bg-red-500/10' : isProcessing ? 'border-yellow-500/50 bg-yellow-500/10' : actionState === 'adapting' ? 'border-green-500/50 bg-green-500/10' : 'border-gray-800'}`}>
        <CardContent className="p-6 flex flex-col items-center justify-center text-center gap-4">
          {recording ? (
            <motion.div animate={{ scale: [1, 1.1, 1] }} transition={{ repeat: Infinity, duration: 1.5 }} className="w-16 h-16 rounded-full bg-red-500 flex items-center justify-center shadow-[0_0_30px_rgba(239,68,68,0.5)]">
              <Mic className="w-8 h-8 text-white" />
            </motion.div>
          ) : isProcessing ? (
            <div className="w-16 h-16 rounded-full bg-yellow-500/20 flex items-center justify-center">
              <Loader2 className="w-8 h-8 text-yellow-500 animate-spin" />
            </div>
          ) : actionState === 'adapting' ? (
            <div className="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center">
              <Zap className="w-8 h-8 text-green-500" />
            </div>
          ) : (
            <Button onClick={toggleRecording} variant="outline" className="w-16 h-16 rounded-full border-gray-700 bg-gray-900 hover:bg-gray-800 hover:border-giovanni-primary group">
              <MicOff className="w-8 h-8 text-gray-500 group-hover:text-giovanni-primary transition-colors" />
            </Button>
          )}

          <div>
            <h3 className="text-lg font-semibold">
              {recording ? "Listening to Carbon..." : isProcessing ? "Synthesizing Intent..." : actionState === 'adapting' ? "Timeline Adapted" : "Awaiting Override"}
            </h3>
            <p className="text-sm text-gray-400">
              {recording ? "Speak your changes clearly." : isProcessing ? "Processing paralinguistic markers." : "Tap mic to inject lived truth."}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Quick Add Task Button */}
      <div className="flex justify-end -mt-2 mb-2">
        <Button 
          onClick={() => {
            const date = new Date();
            date.setMinutes(date.getMinutes() + 10); // 10 mins from now
            addTask({
              platforms: ["reminder"],
              datetime_utc: date.toISOString(),
              label: "Review Silicon Metrics",
              caption: "Quick check-in on the cognitive mesh performance.",
              video_filename: "",
              thumbnail_filename: "",
              hashtags: ["#metrics"],
              metadata: { type: "general" }
            });
            loadAllTasks();
            speak("Task added to the timeline.", "motivational");
          }}
          className="bg-giovanni-primary hover:bg-giovanni-primary/80 text-white text-xs py-1 h-8"
        >
          <Calendar className="w-3 h-3 mr-2" /> Inject Task (+10m)
        </Button>
      </div>

      {/* Current/Next Task Focus */}
      {currentTask ? (
        <Card className="border-giovanni-accent/50 bg-giovanni-accent/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-giovanni-accent flex items-center gap-2">
              <Zap className="w-4 h-4" /> Active Imperative
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex justify-between items-start mb-2">
              <div className="text-xl font-bold">{currentTask.label}</div>
              <div className="text-sm font-mono text-giovanni-accent">{formatTime(currentTask.datetime_utc)}</div>
            </div>
            <p className="text-sm text-gray-300 mb-4">{currentTask.caption}</p>
            <div className="flex flex-wrap gap-2">
              {currentTask.platforms.map(p => (
                <span key={p} className="text-xs px-2 py-1 bg-gray-900 rounded border border-gray-700 uppercase tracking-wider">{p}</span>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-400 flex items-center gap-2">
              <Clock className="w-4 h-4" /> Next Up (Within 2 Hours)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {upcomingTasks.length === 0 ? (
                <p className="text-sm text-gray-500">Timeline is clear.</p>
              ) : upcomingTasks.map((task, i) => (
                <motion.div key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }} className="flex items-start gap-3 p-2 rounded hover:bg-gray-900/50 transition-colors">
                  <div className={`mt-0.5 ${task.platforms.includes('medication') ? 'text-red-400' : 'text-giovanni-primary'}`}>
                    {task.platforms.includes('medication') ? <Pill className="w-4 h-4" /> : <Calendar className="w-4 h-4" />}
                  </div>
                  <div className="flex-1">
                    <div className="flex justify-between">
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
