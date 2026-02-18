import React, { useState, useCallback, useRef } from 'react';
import { Upload, FileImage, Folder, FolderOpen, Loader2, X } from 'lucide-react';
import { API_BASE_URL } from '@/lib/api';

interface UploadZoneProps {
    eventId: string | null;
    onUploadStart: () => void;
    onUploadComplete: (link: string, count: number) => void;
}

export default function UploadZone({ eventId, onUploadStart, onUploadComplete }: UploadZoneProps) {
    const [isDragging, setIsDragging] = useState(false);
    const [files, setFiles] = useState<File[]>([]);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const onDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const onDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const onDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);

        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            const newFiles = Array.from(e.dataTransfer.files).filter(file => file.type.startsWith('image/'));
            setFiles(newFiles);
        }
    }, []);

    const handleFolderSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            const newFiles = Array.from(e.target.files).filter(file => file.type.startsWith('image/'));
            setFiles(newFiles);
        }
    };

    const handleUpload = async () => {
        if (!eventId || files.length === 0) return;

        setIsUploading(true);
        onUploadStart();
        setUploadProgress(5);

        try {
            const formData = new FormData();
            files.forEach(file => {
                formData.append('files', file);
            });

            // Simulate progress 
            const interval = setInterval(() => {
                setUploadProgress(prev => {
                    if (prev >= 90) return prev;
                    return prev + Math.random() * 10;
                });
            }, 500);

            const token = localStorage.getItem('access_token');
            // Assuming the backend handles the upload and starts processing
            const response = await fetch(`${API_BASE_URL}/uploads/?event_id=${eventId}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
                body: formData
            });

            clearInterval(interval);
            setUploadProgress(100);

            if (!response.ok) throw new Error('Upload failed');

            const data = await response.json();
            const link = data.share_link || `http://localhost:3000/event/${eventId}`; // Fallback

            // Pass data back to parent
            onUploadComplete(link, files.length);
            setFiles([]); // Reset local state

        } catch (error) {
            console.error('Upload error:', error);
            alert('Failed to upload photos');
            setUploadProgress(0);
            setIsUploading(false); // Only reset if error, otherwise parent handles view switch
        }
    };

    const totalSize = files.reduce((acc, file) => acc + file.size, 0);
    const formattedSize = (totalSize / (1024 * 1024)).toFixed(2) + ' MB';

    return (
        <div id="upload-zone" className="bg-white rounded-3xl shadow-xl shadow-slate-900/5 border border-slate-100 p-10 max-w-4xl mx-auto -mt-24 relative z-20">
            <input
                ref={fileInputRef}
                type="file"
                // @ts-ignore
                webkitdirectory=""
                directory=""
                multiple
                onChange={handleFolderSelect}
                className="hidden"
            />

            {files.length === 0 ? (
                // Empty State
                <div
                    onDragOver={onDragOver}
                    onDragLeave={onDragLeave}
                    onDrop={onDrop}
                    className={`
                        relative border-2 border-dashed rounded-2xl p-16 text-center transition-all duration-300 cursor-pointer group
                        ${isDragging
                            ? 'border-orange-500 bg-orange-50/50 scale-[0.99] ring-4 ring-orange-500/10'
                            : 'border-slate-200 hover:border-orange-300 hover:bg-slate-50'
                        }
                    `}
                    onClick={() => fileInputRef.current?.click()}
                >
                    <div className={`w-20 h-20 rounded-3xl flex items-center justify-center mx-auto mb-6 transition-all duration-300 shadow-lg ${isDragging ? 'bg-orange-100 text-orange-500 translate-y-2' : 'bg-white text-slate-400 shadow-slate-200'}`}>
                        <FolderOpen className="w-10 h-10" />
                    </div>
                    <h3 className="text-2xl font-bold text-slate-900 mb-2 group-hover:text-orange-600 transition-colors">
                        {isDragging ? 'Drop Folder Here' : 'Drag & Drop Event Folder'}
                    </h3>
                    <p className="text-slate-500 mb-8 text-lg">
                        or click to browse your computer
                    </p>
                    <button className="bg-slate-900 text-white px-8 py-3 rounded-xl font-bold hover:bg-slate-800 transition-all shadow-lg shadow-slate-900/10 hover:shadow-slate-900/20 active:scale-95">
                        Choose Folder
                    </button>
                    <p className="mt-8 text-xs text-slate-400 font-medium uppercase tracking-widest">
                        Supports High-Res Images
                    </p>
                </div>
            ) : (
                // Selected State
                <div className="text-center animate-in fade-in zoom-in-95 duration-300 py-8">
                    <div className="w-20 h-20 bg-blue-50 text-blue-600 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-blue-500/10">
                        <Folder className="w-10 h-10" />
                    </div>
                    <h3 className="text-2xl font-bold text-slate-900 mb-2">
                        Folder Selected
                    </h3>
                    <p className="text-slate-500 mb-8 text-lg">
                        Ready to upload <span className="font-bold text-slate-900">{files.length} images</span>
                        <span className="mx-2 text-slate-300">|</span>
                        {formattedSize}
                    </p>

                    {/* Progress Bar */}
                    {isUploading && (
                        <div className="mb-8 max-w-md mx-auto bg-slate-50 p-6 rounded-2xl border border-slate-100">
                            <div className="flex justify-between text-sm font-bold text-slate-600 mb-3">
                                <span className="flex items-center gap-2">
                                    <Loader2 className="w-4 h-4 animate-spin text-orange-500" />
                                    Uploading...
                                </span>
                                <span>{Math.round(uploadProgress)}%</span>
                            </div>
                            <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
                                <div
                                    className="bg-gradient-to-r from-orange-500 to-amber-500 h-full rounded-full transition-all duration-300 ease-out"
                                    style={{ width: `${uploadProgress}%` }}
                                />
                            </div>
                            <p className="text-xs text-slate-400 mt-3 text-center">Do not close this window</p>
                        </div>
                    )}

                    <div className="flex justify-center gap-4">
                        <button
                            onClick={() => setFiles([])}
                            disabled={isUploading}
                            className="px-8 py-4 text-slate-500 font-bold hover:bg-slate-50 rounded-xl transition-colors disabled:opacity-50"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={handleUpload}
                            disabled={isUploading || !eventId}
                            className="px-10 py-4 bg-orange-600 hover:bg-orange-500 text-white rounded-xl font-bold flex items-center gap-3 shadow-xl shadow-orange-600/20 transition-all hover:translate-y-[-2px] hover:shadow-orange-600/30 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none"
                        >
                            {isUploading ? (
                                <>
                                    Uploading...
                                </>
                            ) : (
                                <>
                                    <Upload className="w-5 h-5" />
                                    Start Upload
                                </>
                            )}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
