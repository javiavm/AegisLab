import React, { useState, useEffect, useMemo, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card } from "@/components/ui/card";
import { Wrench, FileText, Cog, Hammer, Clock, User, Package } from 'lucide-react';
import AgentAvatar from './AgentAvatar';

const planningSteps = [
    "Consulting OSHA standards database...",
    "Matching hazard to corrective templates...",
    "Generating action recommendations...",
    "Attaching regulatory citations...",
    "Finalizing action plan..."
];

// Default action items for fallback
const defaultActionItems = [
    {
        id: 1,
        title: "Install guardrails on scaffolding platform",
        description: "Add standard guardrails (42\" top rail, 21\" mid rail) to all open sides",
        oshaCode: "OSHA 1926.451(g)(1)",
        priority: "Immediate",
        icon: Hammer,
        controlType: 'ENGINEERING',
        responsibleRole: 'safety_engineer',
        durationMinutes: 120,
        materials: ['guardrails', 'fixings'],
    },
    {
        id: 2,
        title: "Perform daily stability check",
        description: "Implement pre-shift inspection protocol for all scaffolding components",
        oshaCode: "OSHA 1926.451(f)(3)",
        priority: "Daily",
        icon: FileText,
        controlType: 'ADMINISTRATIVE',
        responsibleRole: 'supervisor',
        durationMinutes: 30,
        materials: ['inspection_checklist'],
    },
    {
        id: 3,
        title: "Provide anti-slip footgear to workers",
        description: "Issue slip-resistant footwear and verify proper fit before platform access",
        oshaCode: "OSHA 1926.95(a)",
        priority: "Before Next Shift",
        icon: Cog,
        controlType: 'PPE',
        responsibleRole: 'safety_officer',
        durationMinutes: 60,
        materials: ['safety_boots'],
    }
];

// Map control type to priority
function mapControlTypeToPriority(controlType) {
    const mapping = {
        'ELIMINATION': 'Immediate',
        'SUBSTITUTION': 'Immediate',
        'ENGINEERING': 'Before Next Shift',
        'ADMINISTRATIVE': 'Daily',
        'PPE': 'Before Next Shift',
    };
    return mapping[controlType] || 'Daily';
}

// Map control type to icon
function getIconForControlType(controlType) {
    const mapping = {
        'ELIMINATION': Hammer,
        'SUBSTITUTION': Hammer,
        'ENGINEERING': Wrench,
        'ADMINISTRATIVE': FileText,
        'PPE': Cog,
    };
    return mapping[controlType] || Cog;
}

// Format control type for display
function formatControlType(controlType) {
    const mapping = {
        'ELIMINATION': 'Elimination',
        'SUBSTITUTION': 'Substitution',
        'ENGINEERING': 'Engineering',
        'ADMINISTRATIVE': 'Administrative',
        'PPE': 'PPE',
    };
    return mapping[controlType] || controlType;
}

// Format role for display
function formatRole(role) {
    if (!role) return 'Assigned';
    return role.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
}

// Format duration
function formatDuration(minutes) {
    if (!minutes) return 'TBD';
    if (minutes < 60) return `${minutes} min`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
}

export default function ActionPlanner({ scoreData, isActive, onComplete, apiData, skipAnimation = false }) {
    const [phase, setPhase] = useState(skipAnimation ? 'complete' : 'planning');
    const [planIndex, setPlanIndex] = useState(0);
    const [visiblePlans, setVisiblePlans] = useState([]);
    const [isFinished, setIsFinished] = useState(skipAnimation);
    const generatingStarted = useRef(skipAnimation);

    // Memoize action plans to prevent recreation on every render
    // apiData is now an array of action plans
    const actionPlans = useMemo(() => {
        if (apiData && Array.isArray(apiData) && apiData.length > 0) {
            return apiData.map((plan, planIdx) => ({
                id: plan.plan_id || `plan-${planIdx + 1}`,
                planNumber: planIdx + 1,
                standards: plan.standards_refs || [],
                costEstimate: plan.cost_estimate,
                leadTimeDays: plan.lead_time_days,
                tasks: (plan.tasks || []).map((task, taskIdx) => ({
                    id: `${planIdx}-${taskIdx}`,
                    title: task.title,
                    description: task.description,
                    oshaCode: plan.standards_refs?.[0] || 'OSHA General Duty',
                    priority: mapControlTypeToPriority(task.control_type),
                    icon: getIconForControlType(task.control_type),
                    controlType: task.control_type,
                    responsibleRole: task.responsible_role,
                    durationMinutes: task.duration_minutes,
                    materials: task.material_requirements || [],
                })),
            }));
        }
        // Fallback to single default plan
        return [{
            id: 'default-plan',
            planNumber: 1,
            standards: ['OSHA 1926.451'],
            costEstimate: null,
            leadTimeDays: null,
            tasks: defaultActionItems,
        }];
    }, [apiData]);

    // Total tasks count for progress display
    const totalTasks = useMemo(() =>
        actionPlans.reduce((sum, plan) => sum + plan.tasks.length, 0),
        [actionPlans]
    );

    const visibleTasksCount = useMemo(() =>
        visiblePlans.reduce((sum, plan) => sum + plan.tasks.length, 0),
        [visiblePlans]
    );

    // If skipAnimation, set all plans as visible immediately
    useEffect(() => {
        if (skipAnimation && actionPlans.length > 0) {
            setVisiblePlans(actionPlans);
        }
    }, [skipAnimation, actionPlans]);

    useEffect(() => {
        if (!isActive || skipAnimation) return;

        // Planning phase
        const planInterval = setInterval(() => {
            setPlanIndex(prev => {
                if (prev >= planningSteps.length - 1) {
                    clearInterval(planInterval);
                    setTimeout(() => setPhase('generating'), 500);
                    return prev;
                }
                return prev + 1;
            });
        }, 700);

        return () => clearInterval(planInterval);
    }, [isActive, skipAnimation]);

    useEffect(() => {
        if (phase !== 'generating') return;
        // Prevent running multiple times
        if (generatingStarted.current) return;
        generatingStarted.current = true;

        // Reveal action plans one by one
        const timeouts = [];
        actionPlans.forEach((plan, index) => {
            const timeout = setTimeout(() => {
                setVisiblePlans(prev => [...prev, plan]);
                if (index === actionPlans.length - 1) {
                    setTimeout(() => {
                        setPhase('complete');
                        setIsFinished(true);
                        // Pass all tasks from all plans to onComplete
                        const allTasks = actionPlans.flatMap(p => p.tasks);
                        setTimeout(() => onComplete(allTasks), 1000);
                    }, 800);
                }
            }, index * 1200);
            timeouts.push(timeout);
        });

        return () => timeouts.forEach(t => clearTimeout(t));
    }, [phase, onComplete, actionPlans]);

    if (!isActive && phase === 'planning' && !skipAnimation) return null;

    const getPriorityStyle = (priority) => {
        switch (priority) {
            case 'Immediate': return 'bg-red-500/20 text-red-300';
            case 'Daily': return 'bg-yellow-500/20 text-yellow-300';
            case 'Before Next Shift': return 'bg-blue-500/20 text-blue-300';
            default: return 'bg-slate-500/20 text-slate-300';
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            transition={{ duration: 0.5 }}
        >
            <Card className="glass border-emerald-500/30 glow-green overflow-hidden">
                {/* Header */}
                <div className="p-6 border-b border-emerald-500/20">
                    <div className="flex items-center gap-4">
                        <AgentAvatar type="action" isActive={phase !== 'complete'} isComplete={phase === 'complete'} size="sm" />
                        <div className="flex-1">
                            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                                Action Planner
                                {phase === 'complete' && (
                                    <motion.span
                                        initial={{ scale: 0 }}
                                        animate={{ scale: 1 }}
                                        className="text-xs bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded-full"
                                    >
                                        Complete
                                    </motion.span>
                                )}
                            </h3>
                            <p className="text-sm text-slate-400">
                                {phase === 'planning' && "Crafting your OSHA-compliant action plan 🛠️✨"}
                                {phase === 'generating' && "Building corrective actions..."}
                                {phase === 'complete' && "Action plan ready for implementation"}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6 space-y-4">
                    {/* Risk Context */}
                    <div className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                        <div className="p-2 bg-orange-500/20 rounded-lg">
                            <span className="text-lg">⚠️</span>
                        </div>
                        <div>
                            <p className="text-xs text-slate-500">Risk Level</p>
                            <p className="text-sm text-white font-medium">
                                {scoreData?.category || "High"} Risk (Score: {scoreData?.riskScore || 12}/25)
                            </p>
                        </div>
                    </div>

                    {/* Planning Progress */}
                    {phase === 'planning' && (
                        <motion.div
                            className="space-y-2"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                        >
                            <div className="flex items-center gap-2 text-emerald-400">
                                <motion.div
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                                >
                                    <Cog className="w-4 h-4" />
                                </motion.div>
                                <span className="text-sm font-medium">{planningSteps[planIndex]}</span>
                            </div>
                            <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                                <motion.div
                                    className="h-full bg-gradient-to-r from-emerald-600 to-emerald-400"
                                    initial={{ width: '0%' }}
                                    animate={{ width: `${((planIndex + 1) / planningSteps.length) * 100}%` }}
                                    transition={{ duration: 0.3 }}
                                />
                            </div>
                        </motion.div>
                    )}

                    {/* Action Plans */}
                    {(phase === 'generating' || phase === 'complete') && (
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <h4 className="text-sm font-medium text-slate-400">Action Plans</h4>
                                <span className="text-xs text-emerald-400">
                                    {visiblePlans.length}/{actionPlans.length} plans generated
                                </span>
                            </div>

                            <AnimatePresence>
                                {visiblePlans.map((plan) => (
                                    <motion.div
                                        key={plan.id}
                                        initial={{ opacity: 0, y: 20, scale: 0.95 }}
                                        animate={{ opacity: 1, y: 0, scale: 1 }}
                                        transition={{ duration: 0.4 }}
                                        className="border border-emerald-500/30 rounded-xl overflow-hidden"
                                    >
                                        {/* Plan Header */}
                                        <div className="p-4 bg-emerald-500/10 border-b border-emerald-500/20">
                                            <div className="flex items-center justify-between mb-2">
                                                <h5 className="text-sm font-semibold text-white flex items-center gap-2">
                                                    <span className="w-6 h-6 rounded-full bg-emerald-500/30 flex items-center justify-center text-xs text-emerald-300">
                                                        {plan.planNumber}
                                                    </span>
                                                    Action Plan #{plan.planNumber}
                                                </h5>
                                                <div className="flex items-center gap-3 text-xs">
                                                    {plan.costEstimate && (
                                                        <span className="text-slate-400">
                                                            Est. Cost: <span className="text-emerald-300">${plan.costEstimate.toFixed(2)}</span>
                                                        </span>
                                                    )}
                                                    {plan.leadTimeDays && (
                                                        <span className="text-slate-400">
                                                            Lead Time: <span className="text-emerald-300">{plan.leadTimeDays} day(s)</span>
                                                        </span>
                                                    )}
                                                </div>
                                            </div>
                                            {plan.standards.length > 0 && (
                                                <div className="flex flex-wrap gap-1">
                                                    {plan.standards.slice(0, 3).map((std, idx) => (
                                                        <span key={idx} className="text-xs bg-slate-700/50 text-slate-300 px-2 py-0.5 rounded">
                                                            {std}
                                                        </span>
                                                    ))}
                                                    {plan.standards.length > 3 && (
                                                        <span className="text-xs text-slate-500">+{plan.standards.length - 3} more</span>
                                                    )}
                                                </div>
                                            )}
                                        </div>

                                        {/* Tasks */}
                                        <div className="p-4 space-y-3">
                                            <div className="text-xs text-slate-500 mb-2">
                                                {plan.tasks.length} Task(s)
                                            </div>
                                            {plan.tasks.map((task) => (
                                                <div
                                                    key={task.id}
                                                    className="p-3 bg-slate-800/50 border border-slate-700/50 rounded-lg"
                                                >
                                                    <div className="flex items-start gap-3">
                                                        <div className="p-1.5 bg-emerald-500/20 rounded-lg mt-0.5">
                                                            <task.icon className="w-3.5 h-3.5 text-emerald-400" />
                                                        </div>
                                                        <div className="flex-1 min-w-0">
                                                            <div className="flex items-start justify-between gap-2 mb-1">
                                                                <h6 className="text-sm font-medium text-white">
                                                                    {task.title}
                                                                </h6>
                                                                <span className={`text-xs px-2 py-0.5 rounded-full shrink-0 ${getPriorityStyle(task.priority)}`}>
                                                                    {task.priority}
                                                                </span>
                                                            </div>
                                                            <p className="text-xs text-slate-400 mb-2">
                                                                {task.description}
                                                            </p>

                                                            {/* Task Details Grid */}
                                                            <div className="grid grid-cols-2 gap-2 mt-2">
                                                                <div className="flex items-center gap-1.5 text-xs">
                                                                    <Wrench className="w-3 h-3 text-slate-500" />
                                                                    <span className="text-slate-500">Control:</span>
                                                                    <span className="text-slate-300">{formatControlType(task.controlType)}</span>
                                                                </div>
                                                                <div className="flex items-center gap-1.5 text-xs">
                                                                    <User className="w-3 h-3 text-slate-500" />
                                                                    <span className="text-slate-500">Assigned:</span>
                                                                    <span className="text-slate-300">{formatRole(task.responsibleRole)}</span>
                                                                </div>
                                                                <div className="flex items-center gap-1.5 text-xs">
                                                                    <Clock className="w-3 h-3 text-slate-500" />
                                                                    <span className="text-slate-500">Duration:</span>
                                                                    <span className="text-slate-300">{formatDuration(task.durationMinutes)}</span>
                                                                </div>
                                                                {task.materials && task.materials.length > 0 && (
                                                                    <div className="flex items-center gap-1.5 text-xs">
                                                                        <Package className="w-3 h-3 text-slate-500" />
                                                                        <span className="text-slate-500">Materials:</span>
                                                                        <span className="text-slate-300 truncate" title={task.materials.join(', ')}>
                                                                            {task.materials.join(', ')}
                                                                        </span>
                                                                    </div>
                                                                )}
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </motion.div>
                                ))}
                            </AnimatePresence>

                            {/* Generation indicator */}
                            {phase === 'generating' && visiblePlans.length < actionPlans.length && (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="flex items-center justify-center gap-2 py-4 text-emerald-400"
                                >
                                    <motion.div
                                        animate={{ rotate: 360 }}
                                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                    >
                                        <Cog className="w-4 h-4" />
                                    </motion.div>
                                    <span className="text-sm">Generating next action plan...</span>
                                </motion.div>
                            )}
                        </div>
                    )}
                </div>
            </Card>
        </motion.div>
    );
}