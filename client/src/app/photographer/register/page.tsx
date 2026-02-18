'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Mail, Lock, User, Camera, Eye, EyeOff, AlertCircle, ArrowLeft } from 'lucide-react';
import { fetchAPI } from '@/lib/api';

export default function PhotographerRegister() {
    const router = useRouter();
    const [formData, setFormData] = useState({
        eventName: '',
        name: '',
        email: '',
        password: '',
        confirmPassword: '',
    });

    const [errors, setErrors] = useState<Record<string, string>>({});
    const [showPassword, setShowPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    // Validate form fields
    const validate = () => {
        const newErrors: Record<string, string> = {};

        if (!formData.eventName.trim()) newErrors.eventName = 'Event Name is required';
        if (!formData.name.trim()) newErrors.name = 'Photographer Name is required';

        if (!formData.email.trim()) {
            newErrors.email = 'Email is required';
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = 'Invalid email address';
        }

        if (!formData.password) {
            newErrors.password = 'Password is required';
        } else if (formData.password.length < 8) {
            newErrors.password = 'Password must be at least 8 characters';
        }

        if (formData.password !== formData.confirmPassword) {
            newErrors.confirmPassword = 'Passwords do not match';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        // Clear error when user types
        if (errors[name]) {
            setErrors(prev => {
                const newErrors = { ...prev };
                delete newErrors[name];
                return newErrors;
            });
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!validate()) return;

        setIsLoading(true);
        setErrors({});

        try {
            await fetchAPI('/auth/register', {
                method: 'POST',
                body: JSON.stringify({
                    name: formData.name, // Using photographer name as user name
                    email: formData.email,
                    password: formData.password,
                    role: 'photographer',
                }),
            });

            alert('Registration successful! Redirecting to login...');
            router.push('/login');

        } catch (error: any) {
            setErrors({ form: error.message || 'Registration failed' });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex bg-white font-sans text-slate-900">
            {/* Left Side - 60% */}
            <div className="hidden lg:flex lg:w-[60%] relative overflow-hidden bg-black">
                {/* Background Image */}
                <div
                    className="absolute inset-0 bg-cover bg-center opacity-80"
                    style={{
                        backgroundImage: "url('https://images.unsplash.com/photo-1516035069371-29a1b244cc32?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80')"
                    }}
                />

                {/* Overlay Gradient */}
                <div className="absolute inset-0 bg-gradient-to-r from-black/90 via-black/50 to-transparent" />

                {/* Content Overlay */}
                <div className="relative z-10 w-full h-full flex flex-col justify-center px-20">
                    <div className="space-y-6">
                        {/* Decorative Element */}
                        <div className="w-16 h-1 bg-orange-500 rounded-full mb-8"></div>

                        <h1 className="text-6xl font-bold text-white leading-tight tracking-tight">
                            Click Your <br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-orange-600">
                                Adventures
                            </span> <br />
                            for Photocontest
                        </h1>

                        <p className="text-lg text-gray-300 max-w-xl leading-relaxed">
                            Join our community of professional photographers. manage your events,
                            share photos instantly with guests using AI-powered facial recognition.
                        </p>
                    </div>
                </div>

                {/* Decorative Dots/Grid */}
                <div className="absolute bottom-10 left-10 flex gap-2">
                    {[...Array(3)].map((_, i) => (
                        <div key={i} className="w-2 h-2 rounded-full bg-white/20"></div>
                    ))}
                </div>
            </div>

            {/* Right Side - 40% */}
            <div className="w-full lg:w-[40%] flex items-center justify-center p-8 bg-gray-50">
                <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-10 border border-gray-100">

                    <div className="mb-8 text-center">
                        <h2 className="text-2xl font-bold text-slate-800">Create Account</h2>
                        <p className="text-sm text-gray-500 mt-2">Enter your details to register</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-5">
                        {/* Global Error */}
                        {errors.form && (
                            <div className="bg-red-50 border border-red-100 text-red-600 px-4 py-3 rounded-lg text-sm flex items-center">
                                <AlertCircle className="w-4 h-4 mr-2" />
                                {errors.form}
                            </div>
                        )}

                        {/* Event Name */}
                        <div className="space-y-1">
                            <label className="text-xs font-semibold text-gray-600 uppercase tracking-wider ml-1">Event Name</label>
                            <input
                                type="text"
                                name="eventName"
                                value={formData.eventName}
                                onChange={handleChange}
                                placeholder="e.g. Summer Wedding 2026"
                                className={`w-full bg-gray-50 border ${errors.eventName ? 'border-red-400' : 'border-gray-200'} rounded-lg py-3 px-4 text-sm text-slate-800 focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500 transition-all`}
                            />
                            {errors.eventName && <p className="text-xs text-red-500 ml-1">{errors.eventName}</p>}
                        </div>

                        {/* Photographer Name */}
                        <div className="space-y-1">
                            <label className="text-xs font-semibold text-gray-600 uppercase tracking-wider ml-1">Photographer Name</label>
                            <input
                                type="text"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                placeholder="Your Full Name"
                                className={`w-full bg-gray-50 border ${errors.name ? 'border-red-400' : 'border-gray-200'} rounded-lg py-3 px-4 text-sm text-slate-800 focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500 transition-all`}
                            />
                            {errors.name && <p className="text-xs text-red-500 ml-1">{errors.name}</p>}
                        </div>

                        {/* Email */}
                        <div className="space-y-1">
                            <label className="text-xs font-semibold text-gray-600 uppercase tracking-wider ml-1">Email</label>
                            <input
                                type="email"
                                name="email"
                                value={formData.email}
                                onChange={handleChange}
                                placeholder="name@company.com"
                                className={`w-full bg-gray-50 border ${errors.email ? 'border-red-400' : 'border-gray-200'} rounded-lg py-3 px-4 text-sm text-slate-800 focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500 transition-all`}
                            />
                            {errors.email && <p className="text-xs text-red-500 ml-1">{errors.email}</p>}
                        </div>

                        {/* Password */}
                        <div className="space-y-1">
                            <label className="text-xs font-semibold text-gray-600 uppercase tracking-wider ml-1">Password</label>
                            <div className="relative">
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    placeholder="••••••••"
                                    className={`w-full bg-gray-50 border ${errors.password ? 'border-red-400' : 'border-gray-200'} rounded-lg py-3 px-4 pr-10 text-sm text-slate-800 focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500 transition-all`}
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-3 text-gray-400 hover:text-gray-600 transition-colors"
                                >
                                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                            </div>
                            {errors.password && <p className="text-xs text-red-500 ml-1">{errors.password}</p>}
                        </div>

                        {/* Confirm Password */}
                        <div className="space-y-1">
                            <label className="text-xs font-semibold text-gray-600 uppercase tracking-wider ml-1">Confirm Password</label>
                            <input
                                type="password"
                                name="confirmPassword"
                                value={formData.confirmPassword}
                                onChange={handleChange}
                                placeholder="••••••••"
                                className={`w-full bg-gray-50 border ${errors.confirmPassword ? 'border-red-400' : 'border-gray-200'} rounded-lg py-3 px-4 text-sm text-slate-800 focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500 transition-all`}
                            />
                            {errors.confirmPassword && <p className="text-xs text-red-500 ml-1">{errors.confirmPassword}</p>}
                        </div>

                        {/* Action Buttons */}
                        <div className="flex gap-4 pt-4">
                            <button
                                type="button"
                                onClick={() => router.push('/')}
                                className="flex-1 py-3 border border-gray-300 rounded-lg text-gray-600 font-medium hover:bg-gray-50 hover:text-gray-900 transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                disabled={isLoading}
                                className="flex-1 py-3 bg-orange-500 text-white rounded-lg font-medium hover:bg-orange-600 shadow-lg shadow-orange-500/30 transition-all transform hover:-translate-y-0.5 disabled:opacity-70 disabled:cursor-not-allowed flex justify-center items-center"
                            >
                                {isLoading ? (
                                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                ) : (
                                    'Confirm'
                                )}
                            </button>
                        </div>
                    </form>

                    <div className="mt-8 text-center">
                        <p className="text-sm text-gray-500">
                            Already have an account?{' '}
                            <Link href="/login" className="text-orange-500 font-semibold hover:text-orange-600 transition-colors">
                                Login here
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
