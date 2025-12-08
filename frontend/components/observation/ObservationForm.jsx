import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card } from "@/components/ui/card";
import { MapPin, AlertTriangle, FileType, Users, Building2, Camera, Sparkles, Shield } from 'lucide-react';

const sites = [
    { id: 'site_1', name: 'Building A - 3rd Floor' },
    { id: 'site_2', name: 'Building A - Ground Level' },
    { id: 'site_3', name: 'Building B - Rooftop' },
    { id: 'site_4', name: 'Building C - Basement' },
    { id: 'site_5', name: 'Exterior - Parking Structure' },
];

const potentials = [
    { id: 'NEAR_MISS', label: 'Near Miss', icon: '⚠️' },
    { id: 'SAFE_PRACTICE', label: 'Safe Practice', icon: '✅' },
    { id: 'AT_RISK_BEHAVIOR', label: 'At-Risk Behavior', icon: '🚨' },
    { id: 'HAZARD', label: 'Hazard', icon: '⛔' },
    { id: 'OTHER', label: 'Other', icon: '📋' },
];

const types = [
    { id: 'AREA_FOR_IMPROVEMENT', label: 'Area for Improvement' },
    { id: 'POSITIVE_OBSERVATION', label: 'Positive Observation' },
    { id: 'UNSAFE_CONDITION', label: 'Unsafe Condition' },
    { id: 'UNSAFE_ACT', label: 'Unsafe Act' },
];

const tradeCategories = [
    { id: 'trade_cat_1', name: 'Scaffolding' },
    { id: 'trade_cat_2', name: 'Electrical' },
    { id: 'trade_cat_3', name: 'Plumbing' },
    { id: 'trade_cat_4', name: 'HVAC' },
    { id: 'trade_cat_5', name: 'General Labor' },
];

const tradePartners = [
    { id: 'partner_1', name: 'SafeScaffold Inc.' },
    { id: 'partner_2', name: 'ElectroPro Services' },
    { id: 'partner_3', name: 'BuildRight Contractors' },
];

export default function ObservationForm({ onSubmit, isSubmitting }) {
    const [formData, setFormData] = useState({
        site: '',
        potential: '',
        type: '',
        tradeCategoryId: '',
        tradePartnerId: '',
        description: '',
        photoId: null
    });
    
    const [photoPreview, setPhotoPreview] = useState(null);

    const handlePhotoChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setFormData({ ...formData, photoId: file.name });
            setPhotoPreview(URL.createObjectURL(file));
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit({
            ...formData,
            observedAt: new Date().toISOString()
        });
    };

    const isValid = formData.site && formData.potential && formData.type && formData.description;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
        >
            <Card className="glass border-slate-700/50 p-8 max-w-3xl mx-auto">
                {/* Header */}
                <div className="text-center mb-8">
                    <motion.div 
                        className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 mb-4"
                        animate={{ rotate: [0, 5, -5, 0] }}
                        transition={{ duration: 4, repeat: Infinity }}
                    >
                        <Shield className="w-8 h-8 text-white" />
                    </motion.div>
                    <h2 className="text-2xl font-bold text-white mb-2">Safety Observation</h2>
                    <p className="text-slate-400">Report what you observed. Our AI agents will analyze it instantly.</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Site & Potential Row */}
                    <div className="grid md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                            <Label className="text-slate-300 flex items-center gap-2">
                                <MapPin className="w-4 h-4 text-blue-400" />
                                Site Location
                            </Label>
                            <Select value={formData.site} onValueChange={(v) => setFormData({...formData, site: v})}>
                                <SelectTrigger className="bg-slate-800/50 border-slate-600 text-white h-12">
                                    <SelectValue placeholder="Select location..." />
                                </SelectTrigger>
                                <SelectContent className="bg-slate-800 border-slate-700">
                                    {sites.map(site => (
                                        <SelectItem key={site.id} value={site.name} className="text-white hover:bg-slate-700">
                                            {site.name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <Label className="text-slate-300 flex items-center gap-2">
                                <AlertTriangle className="w-4 h-4 text-orange-400" />
                                Potential
                            </Label>
                            <Select value={formData.potential} onValueChange={(v) => setFormData({...formData, potential: v})}>
                                <SelectTrigger className="bg-slate-800/50 border-slate-600 text-white h-12">
                                    <SelectValue placeholder="Select potential..." />
                                </SelectTrigger>
                                <SelectContent className="bg-slate-800 border-slate-700">
                                    {potentials.map(p => (
                                        <SelectItem key={p.id} value={p.id} className="text-white hover:bg-slate-700">
                                            <span className="flex items-center gap-2">
                                                <span>{p.icon}</span>
                                                {p.label}
                                            </span>
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    {/* Type & Trade Category Row */}
                    <div className="grid md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                            <Label className="text-slate-300 flex items-center gap-2">
                                <FileType className="w-4 h-4 text-purple-400" />
                                Observation Type
                            </Label>
                            <Select value={formData.type} onValueChange={(v) => setFormData({...formData, type: v})}>
                                <SelectTrigger className="bg-slate-800/50 border-slate-600 text-white h-12">
                                    <SelectValue placeholder="Select type..." />
                                </SelectTrigger>
                                <SelectContent className="bg-slate-800 border-slate-700">
                                    {types.map(t => (
                                        <SelectItem key={t.id} value={t.id} className="text-white hover:bg-slate-700">
                                            {t.label}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <Label className="text-slate-300 flex items-center gap-2">
                                <Building2 className="w-4 h-4 text-emerald-400" />
                                Trade Category
                            </Label>
                            <Select value={formData.tradeCategoryId} onValueChange={(v) => setFormData({...formData, tradeCategoryId: v})}>
                                <SelectTrigger className="bg-slate-800/50 border-slate-600 text-white h-12">
                                    <SelectValue placeholder="Select trade..." />
                                </SelectTrigger>
                                <SelectContent className="bg-slate-800 border-slate-700">
                                    {tradeCategories.map(tc => (
                                        <SelectItem key={tc.id} value={tc.id} className="text-white hover:bg-slate-700">
                                            {tc.name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    {/* Trade Partner */}
                    <div className="space-y-2">
                        <Label className="text-slate-300 flex items-center gap-2">
                            <Users className="w-4 h-4 text-cyan-400" />
                            Trade Partner
                        </Label>
                        <Select value={formData.tradePartnerId} onValueChange={(v) => setFormData({...formData, tradePartnerId: v})}>
                            <SelectTrigger className="bg-slate-800/50 border-slate-600 text-white h-12">
                                <SelectValue placeholder="Select partner..." />
                            </SelectTrigger>
                            <SelectContent className="bg-slate-800 border-slate-700">
                                {tradePartners.map(tp => (
                                    <SelectItem key={tp.id} value={tp.id} className="text-white hover:bg-slate-700">
                                        {tp.name}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>

                    {/* Description */}
                    <div className="space-y-2">
                        <Label className="text-slate-300">Description</Label>
                        <Textarea 
                            value={formData.description}
                            onChange={(e) => setFormData({...formData, description: e.target.value})}
                            placeholder="Describe what you observed in detail..."
                            className="bg-slate-800/50 border-slate-600 text-white min-h-[120px] resize-none"
                        />
                    </div>

                    {/* Photo Upload */}
                    <div className="space-y-2">
                        <Label className="text-slate-300 flex items-center gap-2">
                            <Camera className="w-4 h-4 text-pink-400" />
                            Photo (Optional)
                        </Label>
                        <div className="flex items-center gap-4">
                            <label className="flex-1 cursor-pointer">
                                <div className="border-2 border-dashed border-slate-600 rounded-xl p-6 text-center hover:border-slate-500 transition-colors">
                                    {photoPreview ? (
                                        <img src={photoPreview} alt="Preview" className="w-full h-32 object-cover rounded-lg" />
                                    ) : (
                                        <div className="text-slate-400">
                                            <Camera className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                            <p className="text-sm">Click to upload photo</p>
                                        </div>
                                    )}
                                </div>
                                <input type="file" accept="image/*" onChange={handlePhotoChange} className="hidden" />
                            </label>
                        </div>
                    </div>

                    {/* Submit Button */}
                    <motion.div
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                    >
                        <Button 
                            type="submit" 
                            disabled={!isValid || isSubmitting}
                            className="w-full h-14 bg-gradient-to-r from-blue-600 via-purple-600 to-emerald-600 hover:from-blue-500 hover:via-purple-500 hover:to-emerald-500 text-white font-semibold text-lg rounded-xl shadow-lg shadow-purple-500/25 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isSubmitting ? (
                                <span className="flex items-center gap-2">
                                    <motion.div 
                                        animate={{ rotate: 360 }}
                                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                    >
                                        <Sparkles className="w-5 h-5" />
                                    </motion.div>
                                    Activating AI Agents...
                                </span>
                            ) : (
                                <span className="flex items-center gap-2">
                                    <Sparkles className="w-5 h-5" />
                                    Analyze with AI Agents
                                </span>
                            )}
                        </Button>
                    </motion.div>
                </form>
            </Card>
        </motion.div>
    );
}