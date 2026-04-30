import React, { useState } from "react";
import GiovanniAvatar from "./GiovanniAvatar";
import GiovanniCommandCenter from "./GiovanniCommandCenter";
import GiovanniAnalyticsDashboard from "./GiovanniAnalyticsDashboard";
import GiuseppeNotesTaker from "./GiuseppeNotesTaker";
import GiuseppeBook from "./GiuseppeBook";
import GiuseppePanel from "./GiuseppePanel";
// "Nothing Vital Lives Below Root" - Imports corrected
import { Button } from "./button";
import { Card } from "./card";

export default function App() {
  const [activeTab, setActiveTab] = useState<"dashboard" | "notes" | "book" | "panel">("dashboard");

  return (
    <div className="min-h-screen bg-black text-white font-sans selection:bg-giovanni-primary/30">
      <GiovanniAvatar />
      <GiovanniCommandCenter />
      
      <nav className="fixed top-0 left-0 right-0 h-16 border-b border-gray-900 bg-black/80 backdrop-blur-md z-40 flex items-center justify-between px-8">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded bg-giovanni-primary rotate-45" />
          <span className="text-xl font-black italic tracking-tighter">GIOVANNI SKYRIDER</span>
        </div>
        
        <div className="flex gap-4">
          {(["dashboard", "notes", "book", "panel"] as const).map((tab) => (
            <Button
              key={tab}
              variant={activeTab === tab ? "default" : "ghost"}
              onClick={() => setActiveTab(tab)}
              className="uppercase text-[10px] font-bold tracking-[0.2em]"
            >
              {tab}
            </Button>
          ))}
        </div>
      </nav>

      <main className="pt-20 pb-8 px-8">
        {activeTab === "dashboard" && <GiovanniAnalyticsDashboard />}
        {activeTab === "notes" && <GiuseppeNotesTaker />}
        {activeTab === "book" && <GiuseppeBook />}
        {activeTab === "panel" && <GiuseppePanel />}
      </main>
    </div>
  );
}
