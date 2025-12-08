import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Shield, AlertTriangle, BarChart3, ClipboardCheck, Sparkles, RefreshCw, Heart, Eye } from 'lucide-react';
import AgentAvatar from '../agents/AgentAvatar';

export default function SummaryCard({ riskData, scoreData, actions, onReset, hazardsCount = 1, onViewAgent }) {
    const [showImpact, setShowImpact] = useState(false);

    useEffect(() => {
        const timer = setTimeout(() => setShowImpact(true), 1500);
        return () => clearTimeout(timer);
    }, []);

    const handleAgentClick = (agentType) => {
        if (onViewAgent) {
            onViewAgent(agentType);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
            className="max-w-3xl mx-auto"
        >
            <Card className="glass border-purple-500/30 overflow-hidden">
                {/* Celebration Header */}
                <div className="relative p-8 text-center overflow-hidden">
                    {/* Animated background */}
                    <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 via-purple-600/20 to-emerald-600/20" />
                    <motion.div
                        className="absolute inset-0"
                        animate={{
                            background: [
                                'radial-gradient(circle at 20% 50%, rgba(59,130,246,0.1) 0%, transparent 50%)',
                                'radial-gradient(circle at 80% 50%, rgba(16,185,129,0.1) 0%, transparent 50%)',
                                'radial-gradient(circle at 50% 50%, rgba(249,115,22,0.1) 0%, transparent 50%)',
                                'radial-gradient(circle at 20% 50%, rgba(59,130,246,0.1) 0%, transparent 50%)',
                            ]
                        }}
                        transition={{ duration: 6, repeat: Infinity }}
                    />

                    <div className="relative">
                        <motion.div
                            initial={{ scale: 0, rotate: -180 }}
                            animate={{ scale: 1, rotate: 0 }}
                            transition={{ type: "spring", duration: 0.8 }}
                            className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 mb-4 shadow-lg shadow-purple-500/30"
                        >
                            <Sparkles className="w-10 h-10 text-white" />
                        </motion.div>

                        <motion.h2
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.3 }}
                            className="text-2xl md:text-3xl font-bold text-white mb-2"
                        >
                            Analysis Complete
                        </motion.h2>

                        <motion.p
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.5 }}
                            className="text-slate-400"
                        >
                            Your AI safety agents worked together to protect your team
                        </motion.p>
                    </div>
                </div>

                {/* Agent Collaboration */}
                <div className="px-8 py-6 border-t border-slate-700/50">
                    <p className="text-xs text-slate-500 text-center mb-4">Click on any agent to view their analysis</p>
                    <div className="flex items-center justify-center gap-4 mb-6">
                        <button
                            onClick={() => handleAgentClick('risk')}
                            className="group relative cursor-pointer transition-transform hover:scale-110"
                            title="View Risk Analysis"
                        >
                            <AgentAvatar type="risk" isComplete={true} size="sm" />
                            <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                                <Eye className="w-2.5 h-2.5 text-white" />
                            </div>
                        </button>
                        <motion.div
                            className="w-12 h-0.5 bg-gradient-to-r from-blue-500 to-orange-500"
                            initial={{ scaleX: 0 }}
                            animate={{ scaleX: 1 }}
                            transition={{ delay: 0.2, duration: 0.5 }}
                        />
                        <button
                            onClick={() => handleAgentClick('score')}
                            className="group relative cursor-pointer transition-transform hover:scale-110"
                            title="View Risk Score"
                        >
                            <AgentAvatar type="score" isComplete={true} size="sm" />
                            <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-orange-500 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                                <Eye className="w-2.5 h-2.5 text-white" />
                            </div>
                        </button>
                        <motion.div
                            className="w-12 h-0.5 bg-gradient-to-r from-orange-500 to-emerald-500"
                            initial={{ scaleX: 0 }}
                            animate={{ scaleX: 1 }}
                            transition={{ delay: 0.4, duration: 0.5 }}
                        />
                        <button
                            onClick={() => handleAgentClick('action')}
                            className="group relative cursor-pointer transition-transform hover:scale-110"
                            title="View Action Plans"
                        >
                            <AgentAvatar type="action" isComplete={true} size="sm" />
                            <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-emerald-500 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                                <Eye className="w-2.5 h-2.5 text-white" />
                            </div>
                        </button>
                    </div>
                </div>

                {/* Stats Summary */}
                <div className="px-8 pb-6">
                    <div className="grid grid-cols-3 gap-4 mb-6">
                        <motion.button
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.3 }}
                            onClick={() => handleAgentClick('risk')}
                            className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-xl text-center cursor-pointer hover:bg-blue-500/20 hover:border-blue-500/40 transition-all hover:scale-105"
                        >
                            <AlertTriangle className="w-6 h-6 text-blue-400 mx-auto mb-2" />
                            <p className="text-2xl font-bold text-white">{hazardsCount}</p>
                            <p className="text-xs text-slate-400">{hazardsCount === 1 ? 'Hazard Found' : 'Hazards Found'}</p>
                            <p className="text-xs text-blue-400 mt-2 opacity-0 hover:opacity-100 transition-opacity">Click to view</p>
                        </motion.button>

                        <motion.button
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.4 }}
                            onClick={() => handleAgentClick('score')}
                            className="p-4 bg-orange-500/10 border border-orange-500/20 rounded-xl text-center cursor-pointer hover:bg-orange-500/20 hover:border-orange-500/40 transition-all hover:scale-105"
                        >
                            <BarChart3 className="w-6 h-6 text-orange-400 mx-auto mb-2" />
                            <p className="text-2xl font-bold text-white">{scoreData?.riskScore || 12}</p>
                            <p className="text-xs text-slate-400">Risk Score</p>
                            <p className="text-xs text-orange-400 mt-2 opacity-0 hover:opacity-100 transition-opacity">Click to view</p>
                        </motion.button>

                        <motion.button
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.5 }}
                            onClick={() => handleAgentClick('action')}
                            className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-center cursor-pointer hover:bg-emerald-500/20 hover:border-emerald-500/40 transition-all hover:scale-105"
                        >
                            <ClipboardCheck className="w-6 h-6 text-emerald-400 mx-auto mb-2" />
                            <p className="text-2xl font-bold text-white">{actions?.length || 3}</p>
                            <p className="text-xs text-slate-400">Actions Created</p>
                            <p className="text-xs text-emerald-400 mt-2 opacity-0 hover:opacity-100 transition-opacity">Click to view</p>
                        </motion.button>
                    </div>

                    {/* Impact Message */}
                    {showImpact && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="p-6 bg-gradient-to-br from-slate-800/80 to-slate-900/80 rounded-2xl border border-slate-700 text-center mb-6"
                        >
                            <div className="flex items-center justify-center gap-2 mb-3">
                                <Heart className="w-5 h-5 text-red-400" />
                                <h3 className="text-lg font-semibold text-white">Saving Lives Together</h3>
                                <Heart className="w-5 h-5 text-red-400" />
                            </div>
                            <p className="text-slate-400 text-sm leading-relaxed max-w-md mx-auto">
                                Your safety agents are working 24/7 to keep workers safe.
                                Every observation you report helps prevent accidents and saves lives.
                            </p>
                            <motion.div
                                className="flex items-center justify-center gap-1 mt-4"
                                animate={{ scale: [1, 1.05, 1] }}
                                transition={{ duration: 2, repeat: Infinity }}
                            >
                                <Shield className="w-4 h-4 text-emerald-400" />
                                <span className="text-xs text-emerald-400 font-medium">Protected by AegisAI</span>
                            </motion.div>
                        </motion.div>
                    )}

                    {/* Action Buttons */}
                    <div className="flex flex-col sm:flex-row gap-3">
                        <Button
                            onClick={onReset}
                            className="flex-1 h-12 bg-gradient-to-r from-blue-600 via-purple-600 to-emerald-600 hover:from-blue-500 hover:via-purple-500 hover:to-emerald-500 text-white font-semibold rounded-xl"
                        >
                            <RefreshCw className="w-4 h-4 mr-2" />
                            Report Another Observation
                        </Button>
                    </div>
                </div>
            </Card>
        </motion.div>
    );
}