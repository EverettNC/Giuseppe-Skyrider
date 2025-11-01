import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";

export default function GiuseppePanel() {
  const [schedule, setSchedule] = useState([]);
  const [recording, setRecording] = useState(false);
  const [currentTask, setCurrentTask] = useState(null);

  useEffect(() => {
    fetch("/demo_schedule_2025w45.json")
      .then((res) => res.json())
      .then(setSchedule)
      .catch((err) => console.error("Schedule load error:", err));
  }, []);

  const toggleRecording = () => {
    setRecording(!recording);
    // Integrate Web Audio / MediaRecorder here
    console.log(recording ? "Stopping recording..." : "Starting recording...");
  };

  return (
    <div className="fixed right-4 top-4 w-96 p-4 bg-white shadow-2xl rounded-2xl border z-50">
      <h2 className="text-xl font-bold mb-2">Giuseppe Scheduler</h2>

      {currentTask ? (
        <Card className="mb-4">
          <CardContent>
            <h3 className="font-semibold">Now: {currentTask.label}</h3>
            <p className="text-sm text-muted">{currentTask.caption}</p>
          </CardContent>
        </Card>
      ) : (
        <p className="text-sm mb-4">No active task.</p>
      )}

      <div className="flex items-center justify-between mb-4">
        <span className="font-medium">Recording:</span>
        <Switch checked={recording} onCheckedChange={toggleRecording} />
      </div>

      <Button variant="outline" onClick={() => setCurrentTask(schedule[0])}>
        Load First Task
      </Button>
    </div>
  );
}

