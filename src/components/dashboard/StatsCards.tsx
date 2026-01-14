import { motion } from 'framer-motion';
import { Rocket, TrendingUp, Zap, Trophy } from 'lucide-react';
import { useAppStore } from '../../stores/useAppStore';
import './StatsCards.css';

export function StatsCards() {
    const { quests, userStats } = useAppStore();

    const stats = [
        {
            id: 'quests',
            label: 'Активных квестов',
            value: quests.length,
            icon: Rocket,
            color: 'var(--accent-primary)',
            gradient: 'linear-gradient(135deg, #7c3aed 0%, #a855f7 100%)',
        },
        {
            id: 'xp',
            label: 'Всего XP',
            value: userStats.totalXp,
            icon: Zap,
            color: 'var(--accent-warning)',
            gradient: 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)',
        },
        {
            id: 'completed',
            label: 'Завершено',
            value: userStats.questsCompleted,
            icon: Trophy,
            color: 'var(--accent-success)',
            gradient: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)',
        },
        {
            id: 'revenue',
            label: 'Доход ($)',
            value: userStats.revenueGenerated,
            icon: TrendingUp,
            color: 'var(--accent-info)',
            gradient: 'linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%)',
        },
    ];

    return (
        <div className="stats-grid">
            {stats.map((stat, index) => {
                const Icon = stat.icon;
                return (
                    <motion.div
                        key={stat.id}
                        className="stat-card"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                    >
                        <div className="stat-icon" style={{ background: stat.gradient }}>
                            <Icon size={24} color="white" />
                        </div>
                        <div className="stat-content">
                            <span className="stat-value">{stat.value.toLocaleString()}</span>
                            <span className="stat-label">{stat.label}</span>
                        </div>
                    </motion.div>
                );
            })}
        </div>
    );
}
