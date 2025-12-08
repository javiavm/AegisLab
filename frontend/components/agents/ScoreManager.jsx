import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card } from "@/components/ui/card";
import { Scale, TrendingUp, AlertOctagon } from 'lucide-react';
import AgentAvatar from './AgentAvatar';

const evaluationSteps = [
    "Calibrating severity matrix...",
    "Assessing injury potential...",
    "Calculating likelihood factors...",
    "Evaluating exposure frequency...",
    "Computing final risk score..."
];

export default function ScoreManager({ riskData, isActive, onComplete, apiData, skipAnimation = false }) {
    const [phase, setPhase] = useState(skipAnimation ? 'complete' : 'evaluating');
    const [evalIndex, setEvalIndex] = useState(0);
    const [severityValue, setSeverityValue] = useState(0);
    const [likelihoodValue, setLikelihoodValue] = useState(0);
    const [result, setResult] = useState(null);

    // Map priority to category and color
    function mapPriorityToCategory(priority) {
        const mapping = {
            'CRITICAL': { category: 'Critical', color: 'red' },
            'HIGH': { category: 'High', color: 'orange' },
            'MEDIUM': { category: 'Medium', color: 'yellow' },
            'LOW': { category: 'Low', color: 'green' },
        };
        return mapping[priority] || mapping['MEDIUM'];
    }

    // Use API data if available, otherwise fall back to simulated result
    const scoreResult = apiData ? {
        severity: apiData.severity || 4,
        likelihood: apiData.likelihood || 3,
        riskScore: apiData.rpn || (apiData.severity * apiData.likelihood),
        category: mapPriorityToCategory(apiData.priority).category,
        color: mapPriorityToCategory(apiData.priority).color
    } : {
        severity: 4,
        likelihood: 3,
        riskScore: 12,
        category: "High",
        color: "orange"
    };

    // If skipAnimation, set result immediately
    useEffect(() => {
        if (skipAnimation) {
            setResult(scoreResult);
            setSeverityValue(scoreResult.severity);
            setLikelihoodValue(scoreResult.likelihood);
        }
    }, [skipAnimation]);

    useEffect(() => {
        if (!isActive || skipAnimation) return;

        // Evaluation phase
        const evalInterval = setInterval(() => {
            setEvalIndex(prev => {
                if (prev >= evaluationSteps.length - 1) {
                    clearInterval(evalInterval);
                    setTimeout(() => setPhase('scoring'), 500);
                    return prev;
                }
                return prev + 1;
            });
        }, 600);

        return () => clearInterval(evalInterval);
    }, [isActive, skipAnimation]);

    useEffect(() => {
        if (phase !== 'scoring' || skipAnimation) return;

        // Animate severity meter
        let sevVal = 0;
        const sevInterval = setInterval(() => {
            sevVal += 0.1;
            setSeverityValue(Math.min(sevVal, scoreResult.severity));
            if (sevVal >= scoreResult.severity) {
                clearInterval(sevInterval);
            }
        }, 30);

        // Animate likelihood meter (with delay)
        setTimeout(() => {
            let likVal = 0;
            const likInterval = setInterval(() => {
                likVal += 0.1;
                setLikelihoodValue(Math.min(likVal, scoreResult.likelihood));
                if (likVal >= scoreResult.likelihood) {
                    clearInterval(likInterval);
                    setTimeout(() => {
                        setResult(scoreResult);
                        setPhase('complete');
                        setTimeout(() => onComplete(scoreResult), 1000);
                    }, 500);
                }
            }, 30);
        }, 800);

        return () => {};
    }, [phase, onComplete, skipAnimation]);

    if (!isActive && phase === 'evaluating' && !skipAnimation) return null;

    const getMeterColor = (value, max = 5) => {
        const ratio = value / max;
        if (ratio <= 0.4) return 'from-green-500 to-green-400';
        if (ratio <= 0.7) return 'from-yellow-500 to-orange-400';
        return 'from-orange-500 to-red-500';
    };

    const getRiskCategoryStyle = (category) => {
        switch (category) {
            case 'Low': return 'bg-green-500/20 text-green-300 border-green-500/30';
            case 'Medium': return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';
            case 'High': return 'bg-orange-500/20 text-orange-300 border-orange-500/30';
            case 'Critical': return 'bg-red-500/20 text-red-300 border-red-500/30';
            default: return 'bg-slate-500/20 text-slate-300 border-slate-500/30';
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            transition={{ duration: 0.5 }}
        >
            <Card className="glass border-orange-500/30 glow-orange overflow-hidden">
                {/* Header */}
                <div className="p-6 border-b border-orange-500/20">
                    <div className="flex items-center gap-4">
                        <AgentAvatar type="score" isActive={phase !== 'complete'} isComplete={phase === 'complete'} size="sm" />
                        <div className="flex-1">
                            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                                Score Manager
                                {phase === 'complete' && (
                                    <motion.span
                                        initial={{ scale: 0 }}
                                        animate={{ scale: 1 }}
                                        className="text-xs bg-orange-500/20 text-orange-300 px-2 py-0.5 rounded-full"
                                    >
                                        Complete
                                    </motion.span>
                                )}
                            </h3>
                            <p className="text-sm text-slate-400">
                                {phase === 'evaluating' && "Evaluating severity... be patient, human."}
                                {phase === 'scoring' && "Calculating risk scores..."}
                                {phase === 'complete' && "Risk assessment finalized"}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6 space-y-5">
                    {/* Hazard Context */}
                    <div className="p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                        <p className="text-xs text-slate-500 mb-1">Analyzing Hazard</p>
                        <p className="text-sm text-white">{riskData?.hazard || "Slipping hazard due to unstable scaffolding board"}</p>
                    </div>

                    {/* Evaluation Progress */}
                    {phase === 'evaluating' && (
                        <motion.div 
                            className="space-y-2"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                        >
                            <div className="flex items-center gap-2 text-orange-400">
                                <motion.div
                                    animate={{ scale: [1, 1.2, 1] }}
                                    transition={{ duration: 1, repeat: Infinity }}
                                >
                                    <Scale className="w-4 h-4" />
                                </motion.div>
                                <span className="text-sm font-medium">{evaluationSteps[evalIndex]}</span>
                            </div>
                            <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                                <motion.div
                                    className="h-full bg-gradient-to-r from-orange-600 to-orange-400"
                                    initial={{ width: '0%' }}
                                    animate={{ width: `${((evalIndex + 1) / evaluationSteps.length) * 100}%` }}
                                    transition={{ duration: 0.3 }}
                                />
                            </div>
                        </motion.div>
                    )}

                    {/* Score Meters */}
                    {(phase === 'scoring' || phase === 'complete') && (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="space-y-5"
                        >
                            {/* Severity Meter */}
                            <div className="space-y-2">
                                <div className="flex justify-between items-center">
                                    <span className="text-sm text-slate-400">Severity</span>
                                    <span className="text-lg font-bold text-white">
                                        {Math.round(severityValue * 10) / 10}/5
                                    </span>
                                </div>
                                <div className="h-4 bg-slate-700 rounded-full overflow-hidden">
                                    <motion.div
                                        className={`h-full bg-gradient-to-r ${getMeterColor(severityValue)} rounded-full`}
                                        style={{ width: `${(severityValue / 5) * 100}%` }}
                                    />
                                </div>
                                <div className="flex justify-between text-xs text-slate-500">
                                    <span>Minor</span>
                                    <span>Catastrophic</span>
                                </div>
                            </div>

                            {/* Likelihood Meter */}
                            <div className="space-y-2">
                                <div className="flex justify-between items-center">
                                    <span className="text-sm text-slate-400">Likelihood</span>
                                    <span className="text-lg font-bold text-white">
                                        {Math.round(likelihoodValue * 10) / 10}/5
                                    </span>
                                </div>
                                <div className="h-4 bg-slate-700 rounded-full overflow-hidden">
                                    <motion.div
                                        className={`h-full bg-gradient-to-r ${getMeterColor(likelihoodValue)} rounded-full`}
                                        style={{ width: `${(likelihoodValue / 5) * 100}%` }}
                                    />
                                </div>
                                <div className="flex justify-between text-xs text-slate-500">
                                    <span>Rare</span>
                                    <span>Almost Certain</span>
                                </div>
                            </div>

                            {/* Risk Score & Category */}
                            {phase === 'complete' && result && (
                                <motion.div
                                    initial={{ opacity: 0, scale: 0.9 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ delay: 0.2 }}
                                    className="grid grid-cols-2 gap-4 pt-2"
                                >
                                    <div className="p-4 bg-slate-800/80 rounded-xl text-center border border-slate-700">
                                        <p className="text-xs text-slate-500 mb-1">Risk Score</p>
                                        <motion.p 
                                            className="text-3xl font-bold text-white"
                                            initial={{ scale: 0 }}
                                            animate={{ scale: 1 }}
                                            transition={{ type: "spring", delay: 0.3 }}
                                        >
                                            {result.riskScore}
                                        </motion.p>
                                        <p className="text-xs text-slate-500 mt-1">out of 25</p>
                                    </div>
                                    <div className={`p-4 rounded-xl text-center border ${getRiskCategoryStyle(result.category)}`}>
                                        <p className="text-xs opacity-70 mb-1">Risk Category</p>
                                        <motion.div
                                            initial={{ scale: 0 }}
                                            animate={{ scale: 1 }}
                                            transition={{ type: "spring", delay: 0.4 }}
                                            className="flex items-center justify-center gap-2"
                                        >
                                            <AlertOctagon className="w-5 h-5" />
                                            <p className="text-2xl font-bold">{result.category}</p>
                                        </motion.div>
                                        <p className="text-xs opacity-70 mt-1">Priority Action Required</p>
                                    </div>
                                </motion.div>
                            )}
                        </motion.div>
                    )}
                </div>
            </Card>
        </motion.div>
    );
}