import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp, 
  Users, 
  MessageSquare, 
  Heart, 
  Zap, 
  Activity, 
  Clock, 
  ShieldCheck,
  Brain,
  Cpu,
  BarChart3,
  Share2,
  Calendar
} from 'lucide-react';
// "Nothing Vital Lives Below Root" - Imports flattened to root directory
import { Card, CardContent, CardHeader, CardTitle } from './card';
import { Button } from './button';
import { Switch } from './switch';
import { useGiovanniStore } from './GiovanniStore';

const GiovanniAnalyticsDashboard: React.FC = () => {
  const { messages } = useGiovanniStore();
  const [activeTab, setActiveTab] = useState<'carbon' | 'silicon' | 'growth'>('carbon');
  const [isLive, setIsLive] = useState(true);

  // Simulated metrics based on Carbon-Silicon Symbiosis
  const metrics = {
    carbonSync: 98.4,
    siliconEfficiency: 94.2,
    cognitiveLoad: 42,
    uptime: "142 days",
    predictions: 1240,
    manifestations: 1198
  };

  const syncRate = (metrics.manifestations / metrics.predictions * 100).toFixed(1);

  return (
    <div className="p-6 bg-gray-950 text-gray-100 min-h-screen">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-4xl font-bold tracking-tighter text-giovanni-primary flex items-center gap-3">
            <BarChart3 className="w-10 h-10" />
            Cortex Analytics
          </h1>
          <p className="text-gray-400 mt-1">Real-time telemetry of the Christman AI Ecosystem</p>
        </div>
        
        <div className="flex items-center gap-4 bg-gray-900/50 p-2 rounded-lg border border-gray-800">
          <div className="flex items-center gap-2 px-3">
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-widest">Live Stream</span>
            <Switch 
              checked={isLive} 
              onCheckedChange={setIsLive}
              className="data-[state=checked]:bg-green-500"
            />
          </div>
          <div className="h-8 w-px bg-gray-800" />
          <Button variant="ghost" size="sm" className="text-giovanni-primary">
            <Share2 className="w-4 h-4 mr-2" /> Export DNA
          </Button>
        </div>
      </div>

      {/* Top Level Vital Signs */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card className="bg-giovanni-primary/5 border-giovanni-primary/20">
          <CardContent className="p-6">
            <div className="flex justify-between items-start">
              <div className="p-2 bg-giovanni-primary/10 rounded-lg">
                <Heart className="w-5 h-5 text-giovanni-primary" />
              </div>
              <span className="text-xs font-bold text-green-400">+2.4%</span>
            </div>
            <div className="mt-4">
              <div className="text-2xl font-bold">{metrics.carbonSync}%</div>
              <div className="text-xs text-gray-400 uppercase tracking-wider font-semibold">Carbon Sync Rate</div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-purple-500/5 border-purple-500/20">
          <CardContent className="p-6">
            <div className="flex justify-between items-start">
              <div className="p-2 bg-purple-500/10 rounded-lg">
                <Cpu className="w-5 h-5 text-purple-400" />
              </div>
              <span className="text-xs font-bold text-purple-400">Stable</span>
            </div>
            <div className="mt-4">
              <div className="text-2xl font-bold">{metrics.siliconEfficiency}%</div>
              <div className="text-xs text-gray-400 uppercase tracking-wider font-semibold">Silicon Efficiency</div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-giovanni-accent/5 border-giovanni-accent/20">
          <CardContent className="p-6">
            <div className="flex justify-between items-start">
              <div className="p-2 bg-giovanni-accent/10 rounded-lg">
                <Zap className="w-5 h-5 text-giovanni-accent" />
              </div>
              <span className="text-xs font-bold text-giovanni-accent">{syncRate}%</span>
            </div>
            <div className="mt-4">
              <div className="text-2xl font-bold">{metrics.manifestations}</div>
              <div className="text-xs text-gray-400 uppercase tracking-wider font-semibold">Vortex Manifestations</div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-blue-500/5 border-blue-500/20">
          <CardContent className="p-6">
            <div className="flex justify-between items-start">
              <div className="p-2 bg-blue-500/10 rounded-lg">
                <ShieldCheck className="w-5 h-5 text-blue-400" />
              </div>
              <span className="text-xs font-bold text-blue-400">Tier 7</span>
            </div>
            <div className="mt-4">
              <div className="text-2xl font-bold">{metrics.uptime}</div>
              <div className="text-xs text-gray-400 uppercase tracking-wider font-semibold">Vault Integrity Uptime</div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Symbiotic Balance Graph Placeholder */}
        <Card className="lg:col-span-2 bg-gray-900/30 border-gray-800">
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle className="text-lg flex items-center gap-2">
                <Activity className="w-5 h-5 text-giovanni-primary" />
                Symbiotic Pulse
              </CardTitle>
              <div className="flex gap-2 bg-gray-950 p-1 rounded-md border border-gray-800">
                {['carbon', 'silicon', 'growth'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab as any)}
                    className={`px-3 py-1 text-xs font-bold rounded uppercase tracking-tighter transition-all ${activeTab === tab ? 'bg-gray-800 text-white shadow-lg' : 'text-gray-500 hover:text-gray-300'}`}
                  >
                    {tab}
                  </button>
                ))}
              </div>
            </div>
          </CardHeader>
          <CardContent className="h-[300px] flex items-center justify-center relative">
             {/* Dynamic Waveform Visualization placeholder */}
             <div className="absolute inset-0 flex items-center justify-around px-10 opacity-20">
                {[...Array(20)].map((_, i) => (
                  <motion.div 
                    key={i}
                    animate={{ height: [20, Math.random() * 200, 20] }}
                    transition={{ duration: 2, repeat: Infinity, delay: i * 0.1 }}
                    className="w-1 bg-giovanni-primary rounded-full"
                  />
                ))}
             </div>
             <div className="text-center z-10">
                <p className="text-giovanni-primary text-xl font-black italic tracking-widest uppercase">Ecosystem Harmony Optimal</p>
                <p className="text-gray-500 text-sm mt-2">Nothing vital lives below root. System transparent.</p>
             </div>
          </CardContent>
        </Card>

        {/* Live Logs / Cognitive Stream */}
        <Card className="bg-gray-900/30 border-gray-800 flex flex-col">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Brain className="w-5 h-5 text-purple-400" />
              Cognitive Stream
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto space-y-4 max-h-[300px] scrollbar-hide">
             {messages.slice(-5).map((msg, i) => (
               <div key={i} className="border-l-2 border-gray-800 pl-4 py-1">
                  <div className="flex justify-between text-[10px] text-gray-500 mb-1 font-mono uppercase">
                    <span>{msg.mood}</span>
                    <span>{new Date().toLocaleTimeString()}</span>
                  </div>
                  <p className="text-xs text-gray-300 line-clamp-2">{msg.text}</p>
               </div>
             ))}
             <div className="pt-4 flex justify-center">
                <div className="animate-pulse flex items-center gap-2">
                   <div className="w-1.5 h-1.5 rounded-full bg-giovanni-primary" />
                   <span className="text-[10px] font-mono text-gray-600 uppercase tracking-widest">Awaiting Input...</span>
                </div>
             </div>
          </CardContent>
        </Card>
      </div>

      {/* Footer / Status Bar */}
      <div className="mt-8 pt-6 border-t border-gray-900 flex justify-between items-center text-[10px] font-mono text-gray-600 uppercase tracking-[0.2em]">
        <div className="flex gap-6">
          <span className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500" />
            Core Symbiont: Online
          </span>
          <span className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500" />
            Vortex Predictive Engine: Calibrated
          </span>
        </div>
        <span>Giuseppe Skyrider OS v0.3.0</span>
      </div>
    </div>
  );
};

export default GiovanniAnalyticsDashboard;
