'use client';

import React from 'react';
import { Image as ImageIcon, Calendar, ArrowRight } from 'lucide-react';

interface Event {
    id: string;
    event_id: number;
    name: string;
    created_at: string;
    is_active: boolean;
}

interface EventListProps {
    events: Event[];
    loading: boolean;
}

export default function EventList({ events, loading }: EventListProps) {
    if (loading) {
        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[1, 2, 3].map((i) => (
                    <div key={i} className="h-48 bg-gray-100 rounded-2xl animate-pulse" />
                ))}
            </div>
        );
    }

    if (events.length === 0) {
        return (
            <div className="text-center py-16 bg-gray-50 rounded-3xl border border-dashed border-gray-200">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4 text-gray-400">
                    <ImageIcon className="w-8 h-8" />
                </div>
                <h3 className="text-lg font-bold text-slate-800 mb-2">No Active Events</h3>
                <p className="text-gray-500 max-w-sm mx-auto">
                    You haven't created any events yet. Use the "New Event" button to get started.
                </p>
            </div>
        );
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {events.map((event) => (
                <div key={event.id} className="group relative bg-white rounded-2xl border border-gray-100 p-6 hover:shadow-xl transition-all hover:border-orange-100 overflow-hidden">
                    {/* Hover Gradient Line */}
                    <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-orange-400 to-pink-500 opacity-0 group-hover:opacity-100 transition-opacity" />

                    <div className="flex justify-between items-start mb-6">
                        <div className="w-12 h-12 rounded-xl bg-orange-50 text-orange-600 flex items-center justify-center font-bold text-lg">
                            {event.name.substring(0, 2).toUpperCase()}
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-bold ${event.is_active
                                ? 'bg-green-100 text-green-700'
                                : 'bg-gray-100 text-gray-600'
                            }`}>
                            {event.is_active ? 'ACTIVE' : 'ARCHIVED'}
                        </span>
                    </div>

                    <h3 className="text-xl font-bold text-slate-900 mb-1 group-hover:text-orange-600 transition-colors truncate">
                        {event.name}
                    </h3>
                    <p className="text-xs text-gray-400 font-mono mb-6">Event ID: #00{event.event_id}</p>

                    <div className="flex items-center justify-between border-t border-gray-100 pt-4">
                        <div className="flex items-center gap-2 text-sm text-gray-500">
                            <Calendar className="w-4 h-4" />
                            {new Date(event.created_at).toLocaleDateString()}
                        </div>

                        <button className="w-8 h-8 rounded-full bg-gray-50 flex items-center justify-center text-gray-400 group-hover:bg-orange-500 group-hover:text-white transition-all">
                            <ArrowRight className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            ))}
        </div>
    );
}
