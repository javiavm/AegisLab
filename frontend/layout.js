import React from 'react';

export default function Layout({ children }) {
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white font-sans">
            <style>{`
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
                
                :root {
                    --agent-blue: #3b82f6;
                    --agent-orange: #f97316;
                    --agent-green: #10b981;
                }
                
                * {
                    font-family: 'Inter', sans-serif;
                }
                
                .glow-blue {
                    box-shadow: 0 0 40px rgba(59, 130, 246, 0.3), 0 0 80px rgba(59, 130, 246, 0.1);
                }
                
                .glow-orange {
                    box-shadow: 0 0 40px rgba(249, 115, 22, 0.3), 0 0 80px rgba(249, 115, 22, 0.1);
                }
                
                .glow-green {
                    box-shadow: 0 0 40px rgba(16, 185, 129, 0.3), 0 0 80px rgba(16, 185, 129, 0.1);
                }
                
                .glass {
                    background: rgba(255, 255, 255, 0.03);
                    backdrop-filter: blur(20px);
                    border: 1px solid rgba(255, 255, 255, 0.08);
                }
                
                .typewriter {
                    overflow: hidden;
                    white-space: nowrap;
                    animation: typing 2s steps(40, end);
                }
                
                @keyframes typing {
                    from { width: 0 }
                    to { width: 100% }
                }
                
                @keyframes pulse-ring {
                    0% { transform: scale(0.8); opacity: 0.5; }
                    50% { transform: scale(1.2); opacity: 0; }
                    100% { transform: scale(0.8); opacity: 0.5; }
                }
                
                @keyframes scan-line {
                    0% { transform: translateY(-100%); }
                    100% { transform: translateY(100%); }
                }
                
                .scan-effect::after {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 2px;
                    background: linear-gradient(90deg, transparent, var(--agent-blue), transparent);
                    animation: scan-line 1.5s ease-in-out infinite;
                }
                
                @keyframes float {
                    0%, 100% { transform: translateY(0px); }
                    50% { transform: translateY(-10px); }
                }
                
                .float-animation {
                    animation: float 3s ease-in-out infinite;
                }
            `}</style>

            {/* Ambient background particles */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl" />
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-orange-500/5 rounded-full blur-3xl" />
                <div className="absolute top-1/2 right-1/3 w-64 h-64 bg-green-500/5 rounded-full blur-3xl" />
            </div>

            <div className="relative z-10">
                {children}
            </div>
        </div>
    );
}