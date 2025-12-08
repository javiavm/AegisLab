import React from 'react';
import { motion } from 'framer-motion';
import { Eye, Scale, Wrench } from 'lucide-react';

const agentConfig = {
    risk: {
        icon: Eye,
        color: 'blue',
        bgColor: 'bg-blue-500',
        borderColor: 'border-blue-400',
        glowClass: 'glow-blue',
        label: 'Risk Analyzer'
    },
    score: {
        icon: Scale,
        color: 'orange',
        bgColor: 'bg-orange-500',
        borderColor: 'border-orange-400',
        glowClass: 'glow-orange',
        label: 'Score Manager'
    },
    action: {
        icon: Wrench,
        color: 'green',
        bgColor: 'bg-emerald-500',
        borderColor: 'border-emerald-400',
        glowClass: 'glow-green',
        label: 'Action Planner'
    }
};

export default function AgentAvatar({ type, isActive, isComplete, size = 'md' }) {
    const config = agentConfig[type];
    const Icon = config.icon;

    const sizeClasses = {
        sm: 'w-10 h-10',
        md: 'w-16 h-16',
        lg: 'w-24 h-24'
    };

    const iconSizes = {
        sm: 'w-5 h-5',
        md: 'w-8 h-8',
        lg: 'w-12 h-12'
    };

    return (
        <div className="relative flex flex-col items-center gap-2">
            {/* Pulse rings when active */}
            {isActive && (
                <>
                    <motion.div
                        className={`absolute ${sizeClasses[size]} rounded-full ${config.bgColor} opacity-20`}
                        animate={{ scale: [1, 1.5, 1], opacity: [0.3, 0, 0.3] }}
                        transition={{ duration: 2, repeat: Infinity }}
                    />
                    <motion.div
                        className={`absolute ${sizeClasses[size]} rounded-full ${config.bgColor} opacity-10`}
                        animate={{ scale: [1, 2, 1], opacity: [0.2, 0, 0.2] }}
                        transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
                    />
                </>
            )}

            {/* Main avatar */}
            <motion.div
                className={`
                    ${sizeClasses[size]} rounded-2xl flex items-center justify-center
                    border-2 ${config.borderColor} transition-all duration-500
                    ${isActive ? `${config.glowClass} ${config.bgColor}/20` : 'bg-slate-800/50'}
                    ${isComplete ? `${config.bgColor}/30` : ''}
                `}
                animate={isActive ? {
                    y: [0, -5, 0],
                } : {}}
                transition={{ duration: 2, repeat: isActive ? Infinity : 0 }}
            >
                <Icon className={`${iconSizes[size]} ${isActive || isComplete ? 'text-white' : 'text-slate-500'}`} />
            </motion.div>

            {/* Label */}
            <span className={`text-xs font-medium ${isActive || isComplete ? 'text-white' : 'text-slate-500'}`}>
                {config.label}
            </span>

            {/* Completion checkmark */}
            {isComplete && (
                <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className={`absolute -top-1 -right-1 w-5 h-5 ${config.bgColor} rounded-full flex items-center justify-center`}
                >
                    <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                </motion.div>
            )}
        </div>
    );
}