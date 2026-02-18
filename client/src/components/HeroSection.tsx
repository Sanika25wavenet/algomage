'use client';

import React from 'react';

export default function HeroSection() {
    return (
        <div className="relative w-full h-[500px] flex items-center justify-center overflow-hidden bg-slate-900 border-b border-white/5">
            {/* Cinematic Background */}
            <div
                className="absolute inset-0 bg-cover bg-center z-0 opacity-40 scale-105 animate-slow-pan"
                style={{
                    backgroundImage: "url('https://images.unsplash.com/photo-1492684223066-81342ee5ff30?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80')"
                }}
            />

            {/* Gradient Overlays for Depth */}
            <div className="absolute inset-0 bg-gradient-to-b from-slate-900/90 via-slate-900/50 to-slate-900" />
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-orange-500/10 via-slate-900/0 to-slate-900/0" />

            {/* Content using glassmorphism hints */}
            <div className="relative z-10 text-center max-w-3xl px-6 mt-16">
                <div className="inline-flex items-center gap-2 px-3 py-1  border border-orange-500/20 text-orange-400 text-xs font-semibold uppercase tracking-wider mb-6 backdrop-blur-sm">

                </div>

                <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 tracking-tight tight-shadow">
                    Upload Your <br />
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-white to-slate-400">Event Folder</span>
                </h1>

                <p className="text-lg md:text-xl text-slate-300 max-w-2xl mx-auto font-light leading-relaxed mb-10">
                    Upload your event image folder.<span className="text-white font-medium"></span>
                </p>

                <button
                    onClick={() => document.getElementById('upload-zone')?.scrollIntoView({ behavior: 'smooth' })}
                    className="group relative inline-flex items-center gap-3 px-8 py-4 bg-white text-slate-900 rounded-full font-bold text-lg hover:bg-slate-100 transition-all duration-300 shadow-[0_0_40px_-10px_rgba(255,255,255,0.3)] hover:shadow-[0_0_60px_-15px_rgba(255,255,255,0.4)]"
                >
                    Select Event Folder
                    <span className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center group-hover:bg-slate-300 transition-colors">
                        ↓
                    </span>
                </button>
            </div>
        </div>
    );
}
