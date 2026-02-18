import React from 'react';
import { CheckCircle, Copy, ExternalLink, Link as LinkIcon, ArrowRight } from 'lucide-react';

interface UploadSuccessProps {
    totalImages: number;
    shareLink: string;
    onReset: () => void;
}

export default function UploadSuccess({ totalImages, shareLink, onReset }: UploadSuccessProps) {
    const copyLink = () => {
        navigator.clipboard.writeText(shareLink);
        alert('Link copied to clipboard!');
    };

    return (
        <div className="bg-white rounded-3xl shadow-2xl shadow-slate-900/10 border border-white/20 p-10 text-center max-w-xl mx-auto animate-in zoom-in-95 duration-500 relative overflow-hidden">
            {/* Background Decor */}
            <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-green-400 to-emerald-500"></div>
            <div className="absolute -right-20 -top-20 w-64 h-64 bg-green-50 rounded-full blur-3xl opacity-50 pointer-events-none"></div>

            <div className="w-24 h-24 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-8 text-green-500 shadow-inner ring-8 ring-green-50/50">
                <CheckCircle className="w-12 h-12" />
            </div>

            <h3 className="text-3xl font-bold text-slate-900 mb-3 tracking-tight">Upload Successful!</h3>
            <p className="text-slate-500 mb-8 max-w-sm mx-auto text-lg">
                <span className="font-semibold text-slate-900">{totalImages} images</span> have been uploaded and processed.
            </p>

            <div className="bg-slate-50 p-1 rounded-2xl flex items-center border border-slate-200 shadow-sm mb-8 transition-all hover:border-slate-300 hover:shadow-md active:scale-[0.99]">
                <div className="p-3 bg-white rounded-xl text-slate-400 shadow-sm border border-slate-100">
                    <LinkIcon className="w-5 h-5" />
                </div>
                <input
                    type="text"
                    value={shareLink}
                    readOnly
                    className="bg-transparent flex-1 text-sm font-medium text-slate-600 outline-none px-4 truncate"
                />
                <button
                    onClick={copyLink}
                    className="bg-white hover:bg-slate-100 text-slate-700 font-bold px-4 py-3 rounded-xl border border-slate-200 transition-colors flex items-center gap-2 text-sm shadow-sm"
                >
                    <Copy className="w-4 h-4" />
                    <span>Copy</span>
                </button>
            </div>

            <div className="flex flex-col gap-3">
                <a
                    href={shareLink}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full bg-slate-900 hover:bg-black text-white font-bold px-6 py-4 rounded-xl transition-all shadow-xl shadow-slate-900/20 flex items-center justify-center gap-2 group"
                >

                </a>

                <button
                    onClick={onReset}
                    className="w-full text-slate-500 hover:text-slate-700 font-semibold px-6 py-4 rounded-xl transition-colors flex items-center justify-center gap-2 hover:bg-slate-50"
                >
                    Upload another folder
                    <ArrowRight className="w-4 h-4" />
                </button>
            </div>
        </div>
    );
}
