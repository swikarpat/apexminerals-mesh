"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { ReactFlow, Background, Controls, MiniMap, Node, Edge, useNodesState, useEdgesState } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { ShieldAlert, ShieldCheck, Activity, Database, Lock, Search, Play, Loader2, RefreshCw } from 'lucide-react';
import axios from 'axios';

export default function CommandCenter() {
  const [prompt, setPrompt] = useState("Procure 15 MT NdFeB from Supplier #REF-8839 for $450,000.");
  const [isAuditing, setIsAuditing] = useState(false);
  const [auditResult, setAuditResult] = useState<any>(null);
  
  // React Flow State
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [isGraphLoading, setIsGraphLoading] = useState(false);

  // --- API Call: Fetch Live Graph from Neo4j ---
  const fetchGraphData = useCallback(async () => {
    setIsGraphLoading(true);
    try {
      // Hitting the Day 2 FastAPI endpoint
      const response = await axios.get('http://localhost:8000/api/graph/trace/US Defense Prime');
      
      // The backend returns a stringified JSON-RPC response, so we parse it
      const rpcData = JSON.parse(response.data.trace);
      const traceResults = rpcData.result; // Array of { supplier, material, qty }

      // 1. Create the Target Node (US Defense Prime)
      const newNodes: Node[] = [
        { 
          id: 'target', 
          position: { x: 800, y: 250 }, 
          data: { label: 'US Defense Prime' }, 
          style: { background: '#1e3a8a', color: '#fff', border: '1px solid #3b82f6', borderRadius: '8px', padding: '15px', fontWeight: 'bold' } 
        }
      ];
      
      const newEdges: Edge[] = [];

      // 2. Dynamically create Source Nodes and Edges based on Neo4j data
      traceResults.forEach((record: any, index: number) => {
        const isShadow = record.supplier.includes("Shadow");
        const nodeId = `source-${index}`;
        
        newNodes.push({
          id: nodeId,
          position: { x: 100, y: 100 + (index * 150) },
          data: { label: `${record.supplier}\n(${record.qty} MT)` },
          style: { 
            background: isShadow ? '#7f1d1d' : '#064e3b', 
            color: '#fff', 
            border: `1px solid ${isShadow ? '#ef4444' : '#10b981'}`, 
            borderRadius: '8px', 
            padding: '10px',
            textAlign: 'center'
          }
        });

        newEdges.push({
          id: `e-${nodeId}-target`,
          source: nodeId,
          target: 'target',
          animated: true,
          label: record.material,
          style: { stroke: isShadow ? '#ef4444' : '#10b981', strokeWidth: isShadow ? 3 : 2 }
        });
      });

      setNodes(newNodes);
      setEdges(newEdges);

    } catch (error) {
      console.error("Failed to fetch graph:", error);
    } finally {
      setIsGraphLoading(false);
    }
  }, [setNodes, setEdges]);

  // Load graph on initial render
  useEffect(() => {
    fetchGraphData();
  }, [fetchGraphData]);

  // --- API Call: Zero-Trust Clean Room ---
  const handleAudit = async () => {
    if (!prompt) return;
    setIsAuditing(true);
    try {
      const response = await axios.post('http://localhost:8000/api/clean-room/redact', { text: prompt });
      setAuditResult(response.data);
    } catch (error) {
      console.error("Error connecting to backend:", error);
    } finally {
      setIsAuditing(false);
    }
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-300 font-sans">
      
      {/* LEFT SIDEBAR */}
      <div className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col z-20">
        <div className="p-6 border-b border-slate-800">
          <h1 className="text-xl font-bold text-cyan-400 flex items-center gap-2">
            <Activity className="w-5 h-5" /> ApexMinerals
          </h1>
          <p className="text-xs text-slate-500 mt-1">Zero-Trust Agentic Mesh</p>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <button className="w-full flex items-center gap-3 px-4 py-2 bg-slate-800 text-white rounded-md">
            <Database className="w-4 h-4 text-cyan-400" /> Graph Explorer
          </button>
          <button className="w-full flex items-center gap-3 px-4 py-2 hover:bg-slate-800/50 rounded-md transition">
            <Lock className="w-4 h-4 text-emerald-400" /> Data Clean Room
          </button>
          <button className="w-full flex items-center gap-3 px-4 py-2 hover:bg-slate-800/50 rounded-md transition">
            <ShieldAlert className="w-4 h-4 text-red-400" /> Policy Simulator
          </button>
        </nav>
      </div>

      {/* MAIN CONTENT AREA */}
      <div className="flex-1 flex flex-col relative">
        
        {/* TOP NAV BAR */}
        <header className="h-16 bg-slate-900/90 backdrop-blur border-b border-slate-800 flex items-center justify-between px-6 z-20">
          <div className="flex items-center gap-2 w-1/2">
            <div className="flex items-center gap-2 bg-slate-950 border border-slate-700 rounded-md px-3 py-1.5 w-full focus-within:border-cyan-500 transition">
              <Search className="w-4 h-4 text-slate-500" />
              <input 
                type="text" 
                placeholder="Enter procurement prompt..." 
                className="bg-transparent border-none outline-none text-sm w-full text-slate-200 placeholder-slate-600"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAudit()}
              />
            </div>
            <button 
              onClick={handleAudit}
              disabled={isAuditing}
              className="bg-cyan-600 hover:bg-cyan-500 text-white px-4 py-1.5 rounded-md text-sm font-medium flex items-center gap-2 transition disabled:opacity-50"
            >
              {isAuditing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              Audit
            </button>
          </div>
          
          <div className="flex items-center gap-4">
            <button onClick={fetchGraphData} className="text-slate-400 hover:text-white flex items-center gap-2 text-sm">
              <RefreshCw className={`w-4 h-4 ${isGraphLoading ? 'animate-spin' : ''}`} /> Sync Neo4j
            </button>
            <div className="flex items-center gap-2 text-xs bg-emerald-950/30 text-emerald-400 border border-emerald-900 px-3 py-1 rounded-full">
              <ShieldCheck className="w-3 h-3" /> ITAR Vault Active
            </div>
          </div>
        </header>

        {/* LIVE CLEAN ROOM RESULTS PANEL */}
        {auditResult && (
          <div className="absolute top-20 left-1/2 transform -translate-x-1/2 w-3/4 z-30 bg-slate-900 border border-slate-700 rounded-lg shadow-2xl p-4 animate-in fade-in slide-in-from-top-4">
            <div className="flex items-center gap-2 mb-3 border-b border-slate-800 pb-2">
              <Lock className="w-4 h-4 text-emerald-400" />
              <h3 className="text-sm font-bold text-white">Zero-Trust Clean Room Output</h3>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-slate-950 p-3 rounded border border-slate-800">
                <p className="text-xs text-slate-500 mb-1">Raw Input (Local)</p>
                <p className="text-sm text-slate-300">{auditResult.original}</p>
              </div>
              <div className="bg-slate-950 p-3 rounded border border-emerald-900/50">
                <p className="text-xs text-emerald-500 mb-1">Redacted Output (Sent to LLM)</p>
                <p className="text-sm text-emerald-300 font-mono">{auditResult.redacted}</p>
              </div>
            </div>
          </div>
        )}

        {/* GRAPH CANVAS */}
        <main className="flex-1 relative z-0">
          <div className="absolute top-4 left-4 z-10 bg-slate-900/80 backdrop-blur border border-slate-700 p-4 rounded-lg shadow-xl max-w-sm">
            <h2 className="text-white font-semibold mb-2">Live Neo4j Supply Chain Trace</h2>
            <p className="text-xs text-slate-400 mb-3">
              Tracing origin for <span className="text-cyan-400">US Defense OEM</span>. 
              Data is pulled directly from local Docker Graph Database.
            </p>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between"><span className="text-slate-500">Total Nodes:</span> <span className="text-white">{nodes.length}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Sanction Risk:</span> <span className="text-red-400 font-bold">DETECTED</span></div>
            </div>
          </div>

          <ReactFlow 
            nodes={nodes} 
            edges={edges} 
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
            className="bg-slate-950"
          >
            <Background color="#334155" gap={16} />
            <Controls className="bg-slate-800 border-slate-700 fill-white" />
            <MiniMap nodeColor="#3b82f6" maskColor="rgba(15, 23, 42, 0.8)" className="bg-slate-900" />
          </ReactFlow>
        </main>
      </div>
    </div>
  );
}