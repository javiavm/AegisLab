import React from 'react';
import { motion } from 'framer-motion';
import AgentAvatar from './AgentAvatar';

export default function AgentTimeline({ currentStep, completedSteps }) {
    const steps = ['risk', 'score', 'action'];

    return (
        <div className="w-full max-w-2xl mx-auto mb-12">
            <div className="flex items-center justify-between relative">
                {/* Connection line */}
                <div className="absolute top-8 left-16 right-16 h-0.5 bg-slate-700" />

                {/* Progress line */}
                <motion.div
                    className="absolute top-8 left-16 h-0.5 bg-gradient-to-r from-blue-500 via-orange-500 to-emerald-500"
                    initial={{ width: 0 }}
                    animate={{
                        width: completedSteps.length === 0 ? 0 :
                            completedSteps.length === 1 ? '33%' :
                                completedSteps.length === 2 ? '66%' : '100%'
                    }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                />

                {steps.map((step, index) => (
                    <div key={step} className="relative z-10">
                        <AgentAvatar
                            type={step}
                            isActive={currentStep === index}
                            isComplete={completedSteps.includes(step)}
                            size="md"
                        />
                    </div>
                ))}
            </div>
        </div>
    );
}