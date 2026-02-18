'use client';

import React from 'react';

interface StatsCardProps {
    title: string;
    value: string | number;
    icon: React.ReactNode;
    trend?: string;
    trendUp?: boolean;
}

export default function StatsCard({ title, value, icon, trend, trendUp }: StatsCardProps) {
    return (
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between mb-4">
                <div className="text-gray-500 font-medium text-sm">{title}</div>
                <div className="p-2 bg-gray-50 rounded-lg text-gray-400">
                    {icon}
                </div>
            </div>

            <div className="flex items-end gap-2">
                <h3 className="text-3xl font-bold text-slate-800">{value}</h3>
                {trend && (
                    <span className={`text-xs font-medium px-2 py-1 rounded-full mb-1 ${trendUp ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'
                        }`}>
                        {trend}
                    </span>
                )}
            </div>
        </div>
    );
}
