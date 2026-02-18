'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Mail, Lock, Eye, EyeOff, LogIn, AlertCircle, ArrowLeft, Camera, Loader2 } from 'lucide-react';
import { fetchAPI } from '@/lib/api';

export default function PhotographerLogin() {
    const router = useRouter();
    const [formData, setFormData] = useState({
        email: '',
        password: '',
    });

    const [errors, setErrors] = useState<Record<string, string>>({});
    const [showPassword, setShowPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [rememberMe, setRememberMe] = useState(false);

    const validate = () => {
        const newErrors: Record<string, string> = {};
        if (!formData.email.trim()) newErrors.email = 'Email is required';
        if (!formData.password) newErrors.password = 'Password is required';
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        // Clear errors on input change
        if (errors[name]) {
            setErrors(prev => {
                const newErrors = { ...prev };
                delete newErrors[name];
                return newErrors;
            });
        }
    };

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!validate()) return;

        setIsLoading(true);
        setErrors({});

        try {
            const data = await fetchAPI('/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({
                    username: formData.email,
                    password: formData.password,
                }),
            });

            if (data.access_token) {
                localStorage.setItem('access_token', data.access_token);
                if (rememberMe) {
                    localStorage.setItem('remember_me', 'true');
                }
                router.push('/dashboard');
            } else {
                throw new Error('No access token received');
            }

        } catch (error: any) {
            setErrors({ form: error.message || 'Authentication failed' });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex bg-white font-sans text-slate-900">
            {/* Left Side: Visuals - 60% */}
            <div className="hidden lg:flex lg:w-[60%] relative overflow-hidden bg-black">
                {/* Background Image */}
                <div
                    className="absolute inset-0 bg-cover bg-center opacity-80"
                    style={{
                        backgroundImage: "url('https://images.unsplash.com/photo-1452587925148-ce544e77e70d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80')"
                    }}
                />
                <div className="absolute inset-0 bg-gradient-to-r from-black/90 via-black/60 to-transparent" />
                <div className="relative z-10 w-full h-full flex flex-col justify-center px-20">
                    <div className="space-y-6 max-w-lg">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="w-12 h-1 bg-orange-500 rounded-full"></div>
                            <Camera className="w-5 h-5 text-orange-500" />
                        </div>
                        <h1 className="text-5xl font-bold text-white leading-tight">
                            Welcome Back,<br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-orange-200">
                                Photographer
                            </span>
                        </h1>
                        <p className="text-lg text-gray-300 leading-relaxed font-light">
                            Login to upload new albums, manage your event gallery, and track your audience engagement in real-time.
                        </p>
                    </div>
                </div>
            </div>

            {/* Right Side: Login Form - 40% */}
            <div className="w-full lg:w-[40%] flex items-center justify-center p-8 bg-gray-50 relative">
                <Link href="/" className="absolute top-8 left-8 text-gray-400 hover:text-gray-600 transition-colors flex items-center gap-2 text-sm font-medium">
                    <ArrowLeft className="w-4 h-4" />
                    Back to Home
                </Link>

                <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-10 border border-gray-100">
                    <div className="mb-8">
                        <h2 className="text-2xl font-bold text-slate-900">Login</h2>
                        <p className="text-sm text-gray-500 mt-1">Access your photographer dashboard</p>
                    </div>

                    <form onSubmit={handleLogin} className="space-y-5">
                        {errors.form && (
                            <div className="bg-red-50 border border-red-100 text-red-600 px-4 py-3 rounded-lg text-sm flex items-center">
                                <AlertCircle className="w-4 h-4 mr-2" />
                                {errors.form}
                            </div>
                        )}

                        <div className="space-y-1.5">
                            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider ml-1">Email</label>
                            <div className="relative group">
                                <Mail className="absolute left-3.5 top-3.5 w-5 h-5 text-gray-400 group-focus-within:text-orange-500 transition-colors" />
                                <input
                                    type="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    placeholder="name@company.com"
                                    disabled={isLoading}
                                    className={`w-full bg-gray-50 border ${errors.email ? 'border-red-300 bg-red-50/30' : 'border-gray-200'} rounded-xl py-3 pl-11 pr-4 text-sm text-slate-800 placeholder-gray-400 focus:outline-none focus:border-orange-500 focus:ring-4 focus:ring-orange-500/10 transition-all duration-200 disabled:opacity-60`}
                                />
                            </div>
                            {errors.email && <p className="text-xs text-red-500 ml-1 mt-1">{errors.email}</p>}
                        </div>

                        <div className="space-y-1.5">
                            <div className="flex justify-between items-center ml-1">
                                <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Password</label>
                                <a href="#" className="text-xs text-orange-600 hover:text-orange-700 font-medium transition-colors">Forgot Password?</a>
                            </div>
                            <div className="relative group">
                                <Lock className="absolute left-3.5 top-3.5 w-5 h-5 text-gray-400 group-focus-within:text-orange-500 transition-colors" />
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    placeholder="Enter your password"
                                    disabled={isLoading}
                                    className={`w-full bg-gray-50 border ${errors.password ? 'border-red-300 bg-red-50/30' : 'border-gray-200'} rounded-xl py-3 pl-11 pr-11 text-sm text-slate-800 placeholder-gray-400 focus:outline-none focus:border-orange-500 focus:ring-4 focus:ring-orange-500/10 transition-all duration-200 disabled:opacity-60`}
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3.5 top-3.5 text-gray-400 hover:text-gray-600 transition-colors"
                                >
                                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                </button>
                            </div>
                            {errors.password && <p className="text-xs text-red-500 ml-1 mt-1">{errors.password}</p>}
                        </div>

                        {/* Remember Me */}
                        <div className="flex items-center">
                            <input
                                id="remember-me"
                                type="checkbox"
                                checked={rememberMe}
                                onChange={(e) => setRememberMe(e.target.checked)}
                                disabled={isLoading}
                                className="h-4 w-4 text-orange-500 border-gray-300 rounded focus:ring-orange-500"
                            />
                            <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-600 cursor-pointer select-none">
                                Remember me for 30 days
                            </label>
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className={`w-full py-3 rounded-xl font-bold shadow-lg transition-all transform flex items-center justify-center gap-2
                                ${isLoading ? 'bg-slate-800 text-white cursor-wait' : 'bg-orange-500 text-white shadow-orange-500/25 hover:bg-orange-600 hover:-translate-y-0.5'}`}
                        >
                            {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <LogIn className="w-4 h-4" />}
                            Login
                        </button>
                    </form>

                    <div className="mt-8 pt-6 border-t border-gray-100 text-center">
                        <p className="text-sm text-gray-500">
                            Don't have an account?{' '}
                            <Link href="/photographer/register" className="text-orange-600 font-semibold hover:text-orange-700 transition-colors">
                                Register now
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
