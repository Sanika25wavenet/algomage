'use client';

import React from 'react';
import { LogOut } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function Navbar({ onLogout }: { onLogout: () => void }) {
    const router = useRouter();

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-900/80 backdrop-blur-xl border-b border-white/5">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-20">
                    {/* Logo */}
                    <div className="flex items-center gap-3 cursor-pointer group" onClick={() => router.push('/dashboard')}>

                        <h1 className="text-xl font-bold text-white tracking-tight">
                            Algomage<span className="text-orange-500"></span>
                        </h1>
                    </div>

                    {/* Right Side: Profile & Logout */}
                    <div className="flex items-center gap-6">
                        <div className="hidden md:flex items-center gap-3 px-4 py-2 bg-white/5 rounded-full border border-white/5">

                            <div className="flex flex-col">
                                <span className="text-sm font-semibold text-white leading-none">Photographer</span>

                            </div>
                        </div>
                        <button
                            onClick={onLogout}
                            className="text-gray-400 hover:text-white transition-colors p-2 rounded-lg hover:bg-white/10"
                            title="Sign Out"
                        >
                            <LogOut className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
}
