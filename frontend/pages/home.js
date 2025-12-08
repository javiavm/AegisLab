import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Sparkles, ArrowRight, ChevronRight, ArrowLeft } from 'lucide-react';
import ObservationForm from '../components/observation/ObservationForm.jsx';
import AgentTimeline from '../components/agents/AgentTimeline.jsx';
import RiskAnalyzer from '../components/agents/RiskAnalyzer.jsx';
import ScoreManager from '../components/agents/ScoreManager.jsx';
import ActionPlanner from '../components/agents/ActionPlanner.jsx';
import SummaryCard from '../components/summary/SummaryCard.jsx';
import { Button } from '../components/ui/button';
import {
    analyzeObservation,
    transformHazardToRiskData,
    transformScoredHazardToScoreData,
    transformActionPlanToActions,
} from '../services/api';

const WORKFLOW_STAGES = {
    FORM: 'form',
    RISK: 'risk',
    SCORE: 'score',
    ACTION: 'action',
    SUMMARY: 'summary'
};

export default function Home() {
    const [stage, setStage] = useState(WORKFLOW_STAGES.FORM);
    const [observation, setObservation] = useState(null);
    const [riskData, setRiskData] = useState(null);
    const [scoreData, setScoreData] = useState(null);
    const [actions, setActions] = useState(null);
    const [completedSteps, setCompletedSteps] = useState([]);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState(null);

    // Store raw API response for passing to components
    const [pipelineResult, setPipelineResult] = useState(null);

    // Track if each stage animation is complete (ready to show Continue button)
    const [riskReady, setRiskReady] = useState(false);
    const [scoreReady, setScoreReady] = useState(false);
    const [actionReady, setActionReady] = useState(false);

    const handleObservationSubmit = async (data) => {
        setObservation(data);
        setIsSubmitting(true);
        setError(null);

        try {
            // Call the backend API
            const result = await analyzeObservation(data);
            setPipelineResult(result);

            // Move to risk analysis stage
            setStage(WORKFLOW_STAGES.RISK);
        } catch (err) {
            console.error('Failed to analyze observation:', err);
            setError(err.message);
        } finally {
            setIsSubmitting(false);
        }
    };

    // When Risk Analyzer animation completes, show the data and enable Continue button
    const handleRiskComplete = useCallback((data) => {
        if (pipelineResult && pipelineResult.hazards.length > 0) {
            const transformedData = transformHazardToRiskData(
                pipelineResult.hazards[0],
                observation
            );
            setRiskData(transformedData);
        } else {
            setRiskData(data);
        }
        setRiskReady(true); // Enable Continue button instead of auto-advancing
    }, [pipelineResult, observation]);

    // Manual continue from Risk to Score
    const handleContinueToScore = () => {
        setCompletedSteps(prev => [...prev, 'risk']);
        setStage(WORKFLOW_STAGES.SCORE);
        setRiskReady(false);
    };

    // When Score Manager animation completes
    const handleScoreComplete = useCallback((data) => {
        if (pipelineResult && pipelineResult.scored_hazards.length > 0) {
            const transformedData = transformScoredHazardToScoreData(
                pipelineResult.scored_hazards[0]
            );
            setScoreData(transformedData);
        } else {
            setScoreData(data);
        }
        setScoreReady(true); // Enable Continue button instead of auto-advancing
    }, [pipelineResult]);

    // Manual continue from Score to Action
    const handleContinueToAction = () => {
        setCompletedSteps(prev => [...prev, 'score']);
        setStage(WORKFLOW_STAGES.ACTION);
        setScoreReady(false);
    };

    // When Action Planner animation completes
    const handleActionComplete = useCallback((data) => {
        if (pipelineResult && pipelineResult.action_plans.length > 0) {
            const transformedData = transformActionPlanToActions(
                pipelineResult.action_plans[0]
            );
            setActions(transformedData);
        } else {
            setActions(data);
        }
        setActionReady(true); // Enable Continue button instead of auto-advancing
    }, [pipelineResult]);

    // Manual continue from Action to Summary
    const handleContinueToSummary = () => {
        setCompletedSteps(prev => [...prev, 'action']);
        setStage(WORKFLOW_STAGES.SUMMARY);
        setActionReady(false);
    };

    const handleReset = () => {
        setStage(WORKFLOW_STAGES.FORM);
        setObservation(null);
        setRiskData(null);
        setScoreData(null);
        setActions(null);
        setCompletedSteps([]);
        setPipelineResult(null);
        setError(null);
        setRiskReady(false);
        setScoreReady(false);
        setActionReady(false);
        setViewingFromSummary(false);
    };

    // State to track if viewing from summary (to show "Back to Summary" button)
    const [viewingFromSummary, setViewingFromSummary] = useState(false);

    // Handle navigation from Summary to view specific agent results
    const handleViewAgent = (agentType) => {
        setViewingFromSummary(true);
        switch (agentType) {
            case 'risk':
                setStage(WORKFLOW_STAGES.RISK);
                setRiskReady(true); // Show continue button immediately
                break;
            case 'score':
                setStage(WORKFLOW_STAGES.SCORE);
                setScoreReady(true);
                break;
            case 'action':
                setStage(WORKFLOW_STAGES.ACTION);
                setActionReady(true);
                break;
            default:
                break;
        }
    };

    // Navigate back to summary from agent view
    const handleBackToSummary = () => {
        setViewingFromSummary(false);
        setStage(WORKFLOW_STAGES.SUMMARY);
    };

    const getCurrentStepIndex = () => {
        switch (stage) {
            case WORKFLOW_STAGES.RISK: return 0;
            case WORKFLOW_STAGES.SCORE: return 1;
            case WORKFLOW_STAGES.ACTION: return 2;
            default: return -1;
        }
    };

    const isAgentWorkflow = stage !== WORKFLOW_STAGES.FORM && stage !== WORKFLOW_STAGES.SUMMARY;

    return (
        <div className="min-h-screen py-8 px-4">
            {/* Header */}
            <motion.header
                className="text-center mb-12"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
            >
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800/50 rounded-full border border-slate-700 mb-6">
                    <Sparkles className="w-4 h-4 text-purple-400" />
                    <span className="text-sm text-slate-300">AI-Powered Safety AegisAI Workflow</span>
                </div>
                <h1 className="text-4xl md:text-5xl font-bold text-white mb-3">
                    <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-emerald-400 bg-clip-text text-transparent">
                        PoC AegisAI Agents
                    </span>
                </h1>
                <p className="text-slate-400 max-w-xl mx-auto">
                    Three AI agents collaborate to analyze safety observations,
                    assess risks, and create OSHA-compliant action plans in real-time.
                </p>
            </motion.header>

            {/* Agent Timeline (visible during workflow) */}
            <AnimatePresence>
                {isAgentWorkflow && (
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="mb-8"
                    >
                        <AgentTimeline
                            currentStep={getCurrentStepIndex()}
                            completedSteps={completedSteps}
                        />
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Main Content */}
            <div className="max-w-4xl mx-auto">
                <AnimatePresence mode="wait">
                    {stage === WORKFLOW_STAGES.FORM && (
                        <motion.div
                            key="form"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0, x: -50 }}
                        >
                            {error && (
                                <div className="mb-4 p-4 bg-red-500/20 border border-red-500/50 rounded-xl text-red-300 text-sm">
                                    <strong>Error:</strong> {error}
                                </div>
                            )}
                            <ObservationForm onSubmit={handleObservationSubmit} isSubmitting={isSubmitting} />
                        </motion.div>
                    )}

                    {stage === WORKFLOW_STAGES.RISK && (
                        <motion.div
                            key="risk"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                        >
                            <RiskAnalyzer
                                observation={observation}
                                isActive={stage === WORKFLOW_STAGES.RISK}
                                onComplete={handleRiskComplete}
                                apiData={pipelineResult?.hazards?.[0]}
                                skipAnimation={viewingFromSummary}
                            />
                            {riskReady && (
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="mt-6 flex justify-center gap-3"
                                >
                                    {viewingFromSummary ? (
                                        <Button
                                            onClick={handleBackToSummary}
                                            className="bg-gradient-to-r from-slate-600 to-slate-700 hover:from-slate-500 hover:to-slate-600 text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2"
                                        >
                                            <ArrowLeft className="w-4 h-4" />
                                            Back to Summary
                                        </Button>
                                    ) : (
                                        <Button
                                            onClick={handleContinueToScore}
                                            className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2"
                                        >
                                            Continue to Score Manager
                                            <ArrowRight className="w-4 h-4" />
                                        </Button>
                                    )}
                                </motion.div>
                            )}
                        </motion.div>
                    )}

                    {stage === WORKFLOW_STAGES.SCORE && (
                        <motion.div
                            key="score"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                        >
                            <ScoreManager
                                riskData={riskData}
                                isActive={stage === WORKFLOW_STAGES.SCORE}
                                onComplete={handleScoreComplete}
                                apiData={pipelineResult?.scored_hazards?.[0]}
                                skipAnimation={viewingFromSummary}
                            />
                            {scoreReady && (
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="mt-6 flex justify-center gap-3"
                                >
                                    {viewingFromSummary ? (
                                        <Button
                                            onClick={handleBackToSummary}
                                            className="bg-gradient-to-r from-slate-600 to-slate-700 hover:from-slate-500 hover:to-slate-600 text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2"
                                        >
                                            <ArrowLeft className="w-4 h-4" />
                                            Back to Summary
                                        </Button>
                                    ) : (
                                        <Button
                                            onClick={handleContinueToAction}
                                            className="bg-gradient-to-r from-purple-500 to-emerald-500 hover:from-purple-600 hover:to-emerald-600 text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2"
                                        >
                                            Continue to Action Planner
                                            <ArrowRight className="w-4 h-4" />
                                        </Button>
                                    )}
                                </motion.div>
                            )}
                        </motion.div>
                    )}

                    {stage === WORKFLOW_STAGES.ACTION && (
                        <motion.div
                            key="action"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                        >
                            <ActionPlanner
                                scoreData={scoreData}
                                isActive={stage === WORKFLOW_STAGES.ACTION}
                                onComplete={handleActionComplete}
                                apiData={pipelineResult?.action_plans}
                                skipAnimation={viewingFromSummary}
                            />
                            {actionReady && (
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="mt-6 flex justify-center gap-3"
                                >
                                    {viewingFromSummary ? (
                                        <Button
                                            onClick={handleBackToSummary}
                                            className="bg-gradient-to-r from-slate-600 to-slate-700 hover:from-slate-500 hover:to-slate-600 text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2"
                                        >
                                            <ArrowLeft className="w-4 h-4" />
                                            Back to Summary
                                        </Button>
                                    ) : (
                                        <Button
                                            onClick={handleContinueToSummary}
                                            className="bg-gradient-to-r from-emerald-500 to-blue-500 hover:from-emerald-600 hover:to-blue-600 text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2"
                                        >
                                            View Summary
                                            <ChevronRight className="w-4 h-4" />
                                        </Button>
                                    )}
                                </motion.div>
                            )}
                        </motion.div>
                    )}

                    {stage === WORKFLOW_STAGES.SUMMARY && (
                        <motion.div
                            key="summary"
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                        >
                            <SummaryCard
                                riskData={riskData}
                                scoreData={scoreData}
                                actions={actions}
                                onReset={handleReset}
                                hazardsCount={pipelineResult?.hazards?.length || 1}
                                onViewAgent={handleViewAgent}
                            />
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            {/* Footer */}
            <motion.footer
                className="mt-16 text-center"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
            >
                <div className="inline-flex items-center gap-2 text-slate-500 text-sm">
                    <Shield className="w-4 h-4" />
                    <span>Powered by AegisAI</span>
                </div>
            </motion.footer>
        </div>
    );
}