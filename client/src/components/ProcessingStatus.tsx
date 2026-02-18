import React from 'react';
import { CheckCircle2, Loader2, Database, ScanFace, FileCode, Check } from 'lucide-react';

export type ProcessingStep = 'uploading' | 'processing_faces' | 'generating_embeddings' | 'storing_vectors' | 'complete';

interface ProcessingStatusProps {
    status: ProcessingStep;
    totalFaces?: number;
}

export default function ProcessingStatus({ status, totalFaces = 0 }: ProcessingStatusProps) {
    const steps = [
        { id: 'processing_faces', label: 'Processing Faces', icon: ScanFace },
        { id: 'generating_embeddings', label: 'Generating Embeddings', icon: FileCode },
        { id: 'storing_vectors', label: 'Storing Vector IDs', icon: Database },
    ];

    // Helper to determine step state
    const getStepState = (stepId: string) => {
        const stepOrder = ['uploading', 'processing_faces', 'generating_embeddings', 'storing_vectors', 'complete'];
        const currentIndex = stepOrder.indexOf(status);
        const stepIndex = stepOrder.indexOf(stepId); // Corrected variable name

        // If step is before current status, it is completed
        if (currentIndex > stepIndex) return 'completed';
        // If step is the current status
        if (currentIndex === stepIndex) return 'current';
        // If step is after current status
        return 'waiting';
    };

    return (
        <div className="bg-white rounded-2xl shadow-xl shadow-slate-900/5 border border-slate-100 p-8 w-full max-w-2xl mx-auto animate-in fade-in zoom-in-95 duration-500">
            <div className="text-center mb-8">
                <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4 relative overflow-hidden">
                    {status === 'complete' ? (
                        <CheckCircle2 className="w-8 h-8 animate-in zoom-in spin-in-90 duration-300" />
                    ) : (
                        <>
                            <Loader2 className="w-8 h-8 animate-spin relative z-10" />
                            <div className="absolute inset-0 bg-blue-100/50 animate-pulse"></div>
                        </>
                    )}
                </div>
                <h2 className="text-2xl font-bold text-slate-900">
                    {status === 'complete' ? 'Processing Complete' : 'AI Processing in Background'}
                </h2>
                <p className="text-slate-500 mt-2">
                    {status === 'complete'
                        ? 'Your gallery is ready to be shared.'
                        : 'Please wait while we analyze your photos.'}
                </p>
            </div>

            <div className="space-y-4 relative">
                {/* Connecting Line */}
                <div className="absolute left-[27px] top-6 bottom-6 w-0.5 bg-slate-100 -z-10"></div>

                {steps.map((step) => {
                    const stepState = getStepState(step.id);
                    const StepIcon = step.icon;

                    return (
                        <div key={step.id} className={`relative flex items-center gap-4 p-4 rounded-xl transition-all duration-500 ${stepState === 'current' ? 'bg-blue-50/50 border border-blue-100' : 'bg-transparent border border-transparent'}`}>

                            {/* Icon Indicator */}
                            <div className={`w-14 h-14 rounded-full flex items-center justify-center border-4 transition-all duration-300 z-10 bg-white
                                ${stepState === 'completed' ? 'border-green-100 text-green-600' :
                                    stepState === 'current' ? 'border-blue-100 text-blue-600 shadow-lg shadow-blue-500/20' :
                                        'border-slate-50 text-slate-300'}
                            `}>
                                {stepState === 'completed' ? (
                                    <Check className="w-6 h-6" />
                                ) : (
                                    <StepIcon className={`w-6 h-6 ${stepState === 'current' ? 'animate-pulse' : ''}`} />
                                )}
                            </div>

                            {/* Text Content */}
                            <div className="flex-1">
                                <h3 className={`font-semibold text-lg transition-colors duration-300 ${stepState === 'waiting' ? 'text-slate-400' : 'text-slate-900'}`}>
                                    {step.label}
                                </h3>
                                {stepState === 'current' && (
                                    <p className="text-sm text-blue-500 font-medium animate-pulse">
                                        Working on it...
                                    </p>
                                )}
                                {stepState === 'completed' && step.id === 'processing_faces' && totalFaces > 0 && (
                                    <p className="text-sm text-green-600 font-medium animate-in fade-in slide-in-from-left-2">
                                        Found {totalFaces} faces
                                    </p>
                                )}
                            </div>

                            {/* Status Indicator Right */}
                            <div className="text-sm font-medium">
                                {stepState === 'completed' && <span className="px-3 py-1 rounded-full text-green-600 bg-green-50">Done</span>}
                                {stepState === 'current' && <span className="px-3 py-1 rounded-full text-blue-600 bg-blue-50 flex items-center gap-2"><Loader2 className="w-3 h-3 animate-spin" /> Processing</span>}
                                {stepState === 'waiting' && <span className="text-slate-300">Pending</span>}
                            </div>
                        </div>
                    );
                })}
            </div>

            {status === 'complete' && totalFaces > 0 && (
                <div className="mt-8 pt-6 border-t border-slate-100 text-center animate-in fade-in slide-in-from-bottom-4">
                    <p className="text-sm text-slate-500 mb-1">Total Faces Indexed</p>
                    <p className="text-3xl font-bold text-slate-900 tracking-tight">{totalFaces}</p>
                </div>
            )}
        </div>
    );
}
