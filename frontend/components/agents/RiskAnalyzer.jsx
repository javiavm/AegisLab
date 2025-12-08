import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card } from "@/components/ui/card";
import { Eye, Search, AlertTriangle, CheckCircle2 } from 'lucide-react';
import AgentAvatar from './AgentAvatar';

const scanningPhrases = [
    "Initializing risk detection protocols...",
    "Scanning observation text for keywords...",
    "Cross-referencing OSHA hazard database...",
    "Analyzing environmental factors...",
    "Identifying potential risk vectors..."
];

export default function RiskAnalyzer({ observation, isActive, onComplete, apiData, skipAnimation = false }) {
    const [phase, setPhase] = useState(skipAnimation ? 'complete' : 'scanning');
    const [scanIndex, setScanIndex] = useState(0);
    const [result, setResult] = useState(null);
    const [typedText, setTypedText] = useState('');

    // Use API data if available, otherwise fall back to simulated result
    const analysisResult = apiData ? {
        hazard: apiData.description || "Hazard detected from observation",
        category: mapTaxonomyToCategory(apiData.taxonomy_ref),
        keywords: extractKeywords(apiData.description, observation?.description),
        confidence: Math.round((apiData.confidence || 0.85) * 100)
    } : {
        hazard: "Slipping hazard due to unstable scaffolding board",
        category: "Fall Protection / Scaffolding",
        keywords: ["scaffolding", "slipped", "falling"],
        confidence: 94
    };

    // Helper function to map taxonomy ref to category
    function mapTaxonomyToCategory(taxonomyRef) {
        const categoryMap = {
            'HAZ-FALL-001': 'Fall Protection / Scaffolding',
            'HAZ-FALL-002': 'Slip, Trip & Fall',
            'HAZ-ELEC-001': 'Electrical Safety',
            'HAZ-ELEC-002': 'Arc Flash / Shock',
            'HAZ-CHEM-001': 'Chemical Exposure',
            'HAZ-CHEM-002': 'Toxic Substances',
            'HAZ-MECH-001': 'Struck By / Caught In',
            'HAZ-MECH-002': 'Machinery Safety',
            'HAZ-ERGO-001': 'Ergonomic / Manual Handling',
            'HAZ-ERGO-002': 'Repetitive Motion',
            'HAZ-FIRE-001': 'Fire / Explosion',
            'HAZ-FIRE-002': 'Hot Work',
            'HAZ-GEN-001': 'General Safety',
            'HAZ-GEN-002': 'Housekeeping',
        };
        return categoryMap[taxonomyRef] || 'General Safety';
    }

    // Helper function to extract keywords
    function extractKeywords(hazardDesc, observationDesc) {
        const commonSafetyTerms = [
            'scaffolding', 'fall', 'falling', 'slip', 'trip', 'electrical', 'chemical',
            'fire', 'machinery', 'equipment', 'guard', 'barrier', 'harness', 'ppe',
            'hazard', 'unsafe', 'exposed', 'unprotected', 'damaged', 'broken',
        ];
        const text = `${hazardDesc || ''} ${observationDesc || ''}`.toLowerCase();
        const found = commonSafetyTerms.filter(term => text.includes(term));
        return found.length > 0 ? found.slice(0, 5) : ['safety', 'hazard', 'risk'];
    }

    // If skipAnimation, set result immediately
    useEffect(() => {
        if (skipAnimation) {
            setResult(analysisResult);
            setTypedText(analysisResult.hazard);
        }
    }, [skipAnimation]);

    useEffect(() => {
        if (!isActive || skipAnimation) return;

        // Scanning phase
        const scanInterval = setInterval(() => {
            setScanIndex(prev => {
                if (prev >= scanningPhrases.length - 1) {
                    clearInterval(scanInterval);
                    setTimeout(() => setPhase('analyzing'), 500);
                    return prev;
                }
                return prev + 1;
            });
        }, 800);

        return () => clearInterval(scanInterval);
    }, [isActive, skipAnimation]);

    useEffect(() => {
        if (phase !== 'analyzing' || skipAnimation) return;

        // Type out the result
        const fullText = analysisResult.hazard;
        let index = 0;
        const typeInterval = setInterval(() => {
            setTypedText(fullText.slice(0, index));
            index++;
            if (index > fullText.length) {
                clearInterval(typeInterval);
                setTimeout(() => {
                    setResult(analysisResult);
                    setPhase('complete');
                    setTimeout(() => onComplete(analysisResult), 1000);
                }, 500);
            }
        }, 30);

        return () => clearInterval(typeInterval);
    }, [phase, onComplete, skipAnimation]);

    if (!isActive && phase === 'scanning' && !skipAnimation) return null;

    return (
        <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            transition={{ duration: 0.5 }}
        >
            <Card className="glass border-blue-500/30 glow-blue overflow-hidden">
                {/* Header */}
                <div className="p-6 border-b border-blue-500/20">
                    <div className="flex items-center gap-4">
                        <AgentAvatar type="risk" isActive={phase !== 'complete'} isComplete={phase === 'complete'} size="sm" />
                        <div className="flex-1">
                            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                                Risk Analyzer
                                {phase === 'complete' && (
                                    <motion.span
                                        initial={{ scale: 0 }}
                                        animate={{ scale: 1 }}
                                        className="text-xs bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded-full"
                                    >
                                        Complete
                                    </motion.span>
                                )}
                            </h3>
                            <p className="text-sm text-slate-400">
                                {phase === 'scanning' && "Let me take a closer look... 🔍"}
                                {phase === 'analyzing' && "Hazard detected! Analyzing..."}
                                {phase === 'complete' && "Analysis complete"}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6 space-y-4">
                    {/* Observation Text with Scan Effect */}
                    <div className="relative">
                        <div className={`p-4 bg-slate-800/50 rounded-xl border border-slate-700 ${phase === 'scanning' ? 'scan-effect' : ''}`}>
                            <p className="text-sm text-slate-300 leading-relaxed">
                                "{observation.description}"
                            </p>
                        </div>

                        {/* Scanning overlay */}
                        {phase === 'scanning' && (
                            <motion.div
                                className="absolute inset-0 pointer-events-none"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                            >
                                <div className="absolute inset-0 bg-gradient-to-b from-blue-500/10 to-transparent rounded-xl" />
                            </motion.div>
                        )}
                    </div>

                    {/* Scanning Status */}
                    {phase === 'scanning' && (
                        <motion.div
                            className="space-y-2"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                        >
                            <div className="flex items-center gap-2 text-blue-400">
                                <motion.div
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                                >
                                    <Search className="w-4 h-4" />
                                </motion.div>
                                <span className="text-sm font-medium">{scanningPhrases[scanIndex]}</span>
                            </div>
                            <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                                <motion.div
                                    className="h-full bg-gradient-to-r from-blue-600 to-blue-400"
                                    initial={{ width: '0%' }}
                                    animate={{ width: `${((scanIndex + 1) / scanningPhrases.length) * 100}%` }}
                                    transition={{ duration: 0.3 }}
                                />
                            </div>
                        </motion.div>
                    )}

                    {/* Analysis Result */}
                    {(phase === 'analyzing' || phase === 'complete') && (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="space-y-4"
                        >
                            {/* Detected Hazard */}
                            <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-xl">
                                <div className="flex items-start gap-3">
                                    <div className="p-2 bg-blue-500/20 rounded-lg">
                                        <AlertTriangle className="w-5 h-5 text-blue-400" />
                                    </div>
                                    <div className="flex-1">
                                        <h4 className="text-sm font-medium text-blue-300 mb-1">Potential Hazard Detected</h4>
                                        <p className="text-white font-medium">
                                            {phase === 'complete' ? result.hazard : typedText}
                                            {phase === 'analyzing' && (
                                                <motion.span
                                                    animate={{ opacity: [1, 0] }}
                                                    transition={{ duration: 0.5, repeat: Infinity }}
                                                    className="inline-block w-0.5 h-4 bg-blue-400 ml-0.5 align-middle"
                                                />
                                            )}
                                        </p>
                                    </div>
                                </div>
                            </div>

                            {/* Details */}
                            {phase === 'complete' && (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    transition={{ delay: 0.3 }}
                                    className="grid grid-cols-2 gap-3"
                                >
                                    <div className="p-3 bg-slate-800/50 rounded-lg">
                                        <p className="text-xs text-slate-500 mb-1">Category</p>
                                        <p className="text-sm text-white font-medium">{result.category}</p>
                                    </div>
                                    <div className="p-3 bg-slate-800/50 rounded-lg">
                                        <p className="text-xs text-slate-500 mb-1">Confidence</p>
                                        <p className="text-sm text-white font-medium">{result.confidence}%</p>
                                    </div>
                                    <div className="col-span-2 p-3 bg-slate-800/50 rounded-lg">
                                        <p className="text-xs text-slate-500 mb-2">Keywords Detected</p>
                                        <div className="flex flex-wrap gap-2">
                                            {result.keywords.map((kw, i) => (
                                                <motion.span
                                                    key={kw}
                                                    initial={{ opacity: 0, scale: 0.8 }}
                                                    animate={{ opacity: 1, scale: 1 }}
                                                    transition={{ delay: i * 0.1 }}
                                                    className="px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded-md"
                                                >
                                                    {kw}
                                                </motion.span>
                                            ))}
                                        </div>
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