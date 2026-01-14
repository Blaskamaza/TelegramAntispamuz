import { motion } from 'framer-motion';
import {
    LayoutDashboard,
    Compass,
    TrendingUp,
    Bot,
    Settings,
    ChevronLeft,
    Zap,
} from 'lucide-react';
import { useAppStore } from '../../stores/useAppStore';
import './Sidebar.css';

const NAV_ITEMS = [
    { id: 'dashboard', label: 'Дашборд', icon: LayoutDashboard, path: '/' },
    { id: 'quests', label: 'Квесты', icon: Compass, path: '/quests' },
    { id: 'trends', label: 'Тренды', icon: TrendingUp, path: '/trends' },
    { id: 'agents', label: 'Агенты', icon: Bot, path: '/agents' },
    { id: 'settings', label: 'Настройки', icon: Settings, path: '/settings' },
] as const;

export function Sidebar() {
    const { sidebarOpen, toggleSidebar, currentView, setCurrentView, userStats } = useAppStore();

    return (
        <motion.aside
            className={`sidebar ${sidebarOpen ? 'open' : 'collapsed'}`}
            initial={false}
            animate={{ width: sidebarOpen ? 260 : 72 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
        >
            {/* Логотип */}
            <div className="sidebar-header">
                <div className="logo">
                    <div className="logo-icon">
                        <Zap size={24} />
                    </div>
                    {sidebarOpen && (
                        <motion.span
                            className="logo-text"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.1 }}
                        >
                            AI Pipeline
                        </motion.span>
                    )}
                </div>
                <button className="toggle-btn" onClick={toggleSidebar}>
                    <ChevronLeft
                        size={20}
                        style={{ transform: sidebarOpen ? 'rotate(0deg)' : 'rotate(180deg)' }}
                    />
                </button>
            </div>

            {/* Навигация */}
            <nav className="sidebar-nav">
                {NAV_ITEMS.map((item) => {
                    const Icon = item.icon;
                    const isActive = currentView === item.id;

                    return (
                        <button
                            key={item.id}
                            className={`nav-item ${isActive ? 'active' : ''}`}
                            onClick={() => setCurrentView(item.id as typeof currentView)}
                        >
                            <div className="nav-icon">
                                <Icon size={20} />
                            </div>
                            {sidebarOpen && (
                                <motion.span
                                    className="nav-label"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    transition={{ delay: 0.1 }}
                                >
                                    {item.label}
                                </motion.span>
                            )}
                            {isActive && (
                                <motion.div
                                    className="nav-indicator"
                                    layoutId="nav-indicator"
                                    transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                                />
                            )}
                        </button>
                    );
                })}
            </nav>

            {/* Статистика пользователя */}
            {sidebarOpen && (
                <motion.div
                    className="sidebar-footer"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.2 }}
                >
                    <div className="user-stats">
                        <div className="level-badge">
                            <span className="level-number">{userStats.level}</span>
                            <span className="level-label">LVL</span>
                        </div>
                        <div className="xp-info">
                            <div className="xp-text">{userStats.totalXp} XP</div>
                            <div className="xp-bar">
                                <div
                                    className="xp-fill"
                                    style={{ width: `${(userStats.totalXp % 500) / 5}%` }}
                                />
                            </div>
                        </div>
                    </div>
                </motion.div>
            )}
        </motion.aside>
    );
}
