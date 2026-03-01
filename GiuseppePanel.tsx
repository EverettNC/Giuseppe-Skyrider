import { useEffect, useState, useRef } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { getAllTasks, getCurrentTask, getUpcomingTasks, TaskEntry } from "./GiuseppeScheduler";
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

      const upcoming = await getUpcomingTasks(120); // Next 2 hours
      setUpcomingTasks(upcoming);
    } catch (error) {
      console.error("Schedule load error:", error);
    }
  };

  const handleExecuteAction = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/execute_action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action_id: currentTask?.label || "general_action" })
      });
      if (response.ok) {
        speak("Action confirmed. Adapting my confidence weights positively.", "hype");
      }
    } catch (error) {
      console.error("Execute action failed:", error);
    }
  };

  const handleDenyAction = async () => {
    setActionState("adapting");
    try {
      const response = await fetch('http://localhost:8001/api/deny_action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action_id: currentTask?.label || "general_action" })
      });
      if (response.ok) {
        // Suppress terminal proposals, adopt caution
        speak("Understood. Imposing stricter boundaries. Adjusting my neural weights.", "caring");
      }
    } catch (error) {
      console.error("Deny action failed:", error);
    } finally {
      setTimeout(() => setActionState("idle"), 3000);
    }
  };

  const toggleRecording = async () => {
    if (!recording) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        chunksRef.current = [];

        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) {
            chunksRef.current.push(e.data);
          }
        };

        mediaRecorder.onstop = async () => {
          const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
          setIsProcessing(true);

          try {
            const formData = new FormData();
            formData.append('audio_blob', blob, 'recording.webm');

            if (currentTask) {
              formData.append('schedule_context', JSON.stringify(currentTask));
            }

            const response = await fetch('http://localhost:8001/api/think', {
              method: 'POST',
              body: formData
            });

            if (!response.ok) {
              throw new Error(`Think API failed: ${response.statusText}`);
            }

            const data = await response.json();

            // ============================================================
            // FACS BLENDSHAPE BRIDGE: Push muscle coordinates to the Avatar
            // ============================================================
            if (data.vortex?.avatar_state?.facs_blendshapes) {
              setFacsState(data.vortex.avatar_state.facs_blendshapes);
              console.log("[CARBON->SILICON] FACS Blendshapes pushed to Avatar store.");
            }

            // Speak the response text
            if (data.text) {
              speak(data.text, "swagger");
            }
          } catch (error) {
            console.error("Failed to process recording:", error);
            speak("Sorry, my silicon brain had a hiccup.", "sassy");
          } finally {
            setIsProcessing(false);
            stream.getTracks().forEach(track => track.stop());
          }
        };

        mediaRecorder.start();
        setRecording(true);
        speak("Recording started. Let that creative flow happen.", "swagger");
        console.log("Starting recording...");
      } catch (err) {
        console.error("Microphone access denied:", err);
        speak("I need microphone access to hear you.", "sassy");
      }
    } else {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
        setRecording(false);
        console.log("Stopping recording...");
      }
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
              {isProcessing ? (
                <Loader2 className="w-5 h-5 text-giovanni-accent animate-spin" />
              ) : recording ? (
                <Mic className="w-5 h-5 text-red-500 animate-pulse" />
              ) : (
                <MicOff className="w-5 h-5 text-gray-500" />
              )}
              <div>
                <span className="font-medium block">Voice Recording</span>
                <span className="text-xs text-gray-400">
                  {isProcessing ? "Silicon is thinking..." : recording ? "Recording in progress..." : "Ready to record"}
                </span>
              </div>
            </div>
            <Switch checked={recording} onCheckedChange={toggleRecording} disabled={isProcessing} />
          </div>

          {/* Action Approval / Denial */}
          <div className="mt-4 pt-4 border-t border-gray-800 flex flex-col gap-2">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-400">Carbon Approval Protocol</span>
              {actionState === "adapting" && (
                <span className="text-xs text-yellow-400 animate-pulse font-mono flex items-center gap-2">
                  <Zap className="w-3 h-3" />
                  Silicon adapting to Carbon boundary...
                </span>
              )}
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Button
                variant="outline"
                className="bg-green-500/10 text-green-400 border-green-500/20 hover:bg-green-500/20"
                onClick={handleExecuteAction}
              >
                [EXECUTE ACTION]
              </Button>
              <Button
                variant="outline"
                className="bg-red-500/10 text-red-400 border-red-500/20 hover:bg-red-500/20"
                onClick={handleDenyAction}
              >
                [DENY ACTION]
              </Button>
            </div>
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

