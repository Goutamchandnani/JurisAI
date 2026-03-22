"use client";

import React, { useState } from 'react';
import { Upload, FileText, Send, Loader2, Scale, BookOpen, ShieldCheck, ChevronRight, Github, Linkedin, Heart } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [collectionName, setCollectionName] = useState<string | null>(null);
  const [query, setQuery] = useState('');
  const [chat, setChat] = useState<{ role: 'user' | 'ai'; content: string; sources?: any[] }[]>([]);
  const [isQuerying, setIsQuerying] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post(`${BACKEND_URL}/upload`, formData);
      setCollectionName(res.data.collection_name);
      setChat([{ role: 'ai', content: `Successfully processed ${file.name}. How can I assist you today?` }]);
    } catch (err) {
      console.error(err);
      setChat([{ role: 'ai', content: "Error uploading document. Please ensure the backend is running." }]);
    } finally {
      setIsUploading(false);
    }
  };

  const submitQuery = async (text: string) => {
    if (!text || !collectionName) return;

    setChat(prev => [...prev, { role: 'user', content: text }]);
    setIsQuerying(true);

    try {
      const res = await axios.post(`${BACKEND_URL}/query`, {
        collection_name: collectionName,
        query: text
      });
      setChat(prev => [...prev, { 
        role: 'ai', 
        content: res.data.answer, 
        sources: Array.isArray(res.data.sources) ? res.data.sources : [] 
      }]);
    } catch (err) {
      console.error(err);
      setChat(prev => [...prev, { role: 'ai', content: "Failed to fetch answer. Please try again." }]);
    } finally {
      setIsQuerying(false);
    }
  };

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query || !collectionName || isQuerying) return;
    const userMessage = query;
    setQuery('');
    await submitQuery(userMessage);
  };

  return (
    <main className="min-h-screen flex flex-col md:flex-row">
      {/* Sidebar - Legal Profile */}
      <aside className="w-full md:w-80 bg-navy-900 border-r border-white/5 p-6 flex flex-col">
        <div className="flex items-center gap-2 mb-10">
          <div className="w-10 h-10 bg-gradient-to-br from-gold-500 to-gold-400 rounded-lg flex items-center justify-center">
            <Scale className="text-navy-900 w-6 h-6" />
          </div>
          <h1 className="text-2xl font-serif font-bold gold-text tracking-wider">JURISAI</h1>
        </div>

        <div className="flex-1 space-y-8">
          <section>
            <h3 className="text-xs uppercase tracking-widest text-white/40 font-bold mb-4">Document Management</h3>
            <form onSubmit={handleUpload} className="space-y-4">
              <label 
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`flex flex-col items-center justify-center p-6 border-2 border-dashed rounded-xl cursor-pointer transition-colors ${
                  isDragging ? 'border-gold-500 bg-gold-500/10' : 'border-white/10 hover:border-gold-500/50 bg-white/5'
                }`}
              >
                <Upload className={`w-6 h-6 mb-2 transition-colors ${isDragging ? 'text-gold-400' : 'text-gold-500'}`} />
                <span className="text-xs text-white/60 text-center">
                  {file ? file.name : (isDragging ? "Drop PDF here" : "Select or drag Legal PDF")}
                </span>
                <input type="file" className="hidden" accept=".pdf" onChange={(e) => setFile(e.target.files?.[0] || null)} />
              </label>
              <button 
                type="submit" 
                disabled={!file || isUploading}
                className="w-full py-3 bg-gradient-to-r from-gold-500 to-gold-400 text-navy-900 rounded-lg font-bold text-sm uppercase tracking-tighter hover:brightness-110 active:scale-[0.98] transition-all disabled:opacity-30 flex items-center justify-center gap-2"
              >
                {isUploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4" />}
                Analyze Document
              </button>
            </form>
          </section>

          <section>
            <h3 className="text-xs uppercase tracking-widest text-white/40 font-bold mb-4">Quick Analysis</h3>
            <div className="space-y-2">
              {["Termination Clauses", "Confidentiality", "Governing Law"].map((item) => (
                <button 
                  key={item} 
                  disabled={!collectionName || isQuerying || isUploading}
                  onClick={() => submitQuery(`Please identify and summarize all ${item.toLowerCase()} in this document.`)}
                  className="w-full text-left p-3 glass-card text-xs text-white/70 hover:text-gold-500 transition-colors flex items-center justify-between group disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  {item}
                  <ChevronRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                </button>
              ))}
            </div>
          </section>

          {/* Credits Section */}
          <section className="pt-4 border-t border-white/5">
            <div className="flex flex-col gap-3">
              <div className="flex items-center gap-1.5 text-[10px] text-white/40 uppercase tracking-widest font-bold">
                Made with <Heart className="w-3 h-3 text-red-500 fill-current" /> by Goutam Chandnani
              </div>
              <div className="flex gap-4">
                <a href="https://www.linkedin.com/in/goutamchandnani/" target="_blank" rel="noopener noreferrer" className="text-white/30 hover:text-gold-500 transition-colors" aria-label="LinkedIn">
                  <Linkedin className="w-4 h-4" />
                </a>
                <a href="https://github.com/Goutamchandnani/JurisAI.git" target="_blank" rel="noopener noreferrer" className="text-white/30 hover:text-gold-500 transition-colors" aria-label="GitHub">
                  <Github className="w-4 h-4" />
                </a>
              </div>
            </div>
          </section>
        </div>

        <div className="mt-8 pt-6 border-t border-white/5">
            <p className="text-[10px] text-white/30 italic leading-relaxed">
              Disclaimer: This AI provide legal intelligence but does not constitute formal legal advice.
            </p>
        </div>
      </aside>

      {/* Main Content - Chat */}
      <section className="flex-1 flex flex-col bg-navy-800/50 relative">
        <header className="h-16 border-b border-white/5 flex items-center px-8 justify-between bg-navy-900/40 backdrop-blur-md sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <BookOpen className="w-5 h-5 text-gold-500" />
            <span className="text-sm font-medium text-white/80">
              {collectionName ? `Active: ${file?.name}` : "Awaiting Document Analysis"}
            </span>
          </div>
          <div className="hidden md:flex gap-4 text-[10px] uppercase tracking-widest text-white/40 font-bold">
             <span>v1.0 Pro</span>
             <span>API Status: Operational</span>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-8 space-y-6">
          {chat.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-center max-w-md mx-auto space-y-6 animate-fade-in">
                <Scale className="w-16 h-16 text-gold-500/20" />
                <div>
                   <h2 className="text-2xl font-serif gold-text mb-2">Welcome to JurisAI Intelligence</h2>
                   <p className="text-white/40 text-sm">Upload a legal contract or case study to perform deep semantic analysis and automated document intelligence.</p>
                </div>
            </div>
          )}

          {chat.map((msg, i) => (
            <div 
              key={i} 
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
            >
              <div className={`max-w-[85%] rounded-2xl p-5 ${
                msg.role === 'user' 
                  ? 'bg-gold-500 text-navy-900 font-medium ml-12' 
                  : 'glass-card text-white/90 mr-12'
              }`}>
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                
                {Array.isArray(msg.sources) && msg.sources.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-white/5 space-y-3">
                    <p className="text-[10px] uppercase tracking-tighter text-gold-500 font-bold">Verified Sources</p>
                    {msg.sources.map((src, j) => (
                      <div key={j} className="p-3 bg-black/20 rounded-lg border border-gold-500/10">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-[10px] text-white/60 truncate">{src.section || "Document"}</span>
                          <span className="text-[10px] font-bold text-gold-400">{src.similarity ? (src.similarity * 100).toFixed(1) : "0.0"}% Relevance</span>
                        </div>
                        <p className="text-[11px] text-white/50 italic line-clamp-2">"{src.text_preview || src.text || ""}"</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          {isQuerying && (
            <div className="flex justify-start animate-fade-in">
              <div className="glass-card p-5 flex items-center gap-3">
                 <Loader2 className="w-4 h-4 animate-spin text-gold-500" />
                 <span className="text-xs text-white/40 italic">Reviewing caselaw and document context...</span>
              </div>
            </div>
          )}
        </div>

        <footer className="p-6 bg-navy-900/60 backdrop-blur-xl border-t border-white/5">
           <form onSubmit={handleQuery} className="max-w-4xl mx-auto relative group">
              <input 
                type="text" 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={collectionName ? "Analyze specific clauses or terms..." : "Analyze a document to start querying..."}
                disabled={!collectionName || isQuerying}
                className="w-full bg-navy-800 border border-white/10 rounded-xl py-4 pl-6 pr-14 text-sm focus:outline-none focus:border-gold-500/50 transition-all placeholder:text-white/20 disabled:opacity-50"
              />
              <button 
                type="submit"
                disabled={!query || isQuerying}
                className="absolute right-2 top-2 bottom-2 w-10 bg-gold-500 rounded-lg flex items-center justify-center text-navy-900 hover:brightness-110 active:scale-95 transition-all disabled:opacity-0"
              >
                <Send className="w-4 h-4" />
              </button>
           </form>
        </footer>
      </section>
    </main>
  );
}
