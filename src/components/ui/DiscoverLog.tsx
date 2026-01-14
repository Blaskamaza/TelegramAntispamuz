import { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Globe, MessageCircle, Rss, RefreshCw } from 'lucide-react';
import './DiscoverLog.css';

interface DiscoveredSource {
    type: 'telegram' | 'facebook' | 'instagram' | 'youtube' | 'website_uz';
    url: string;
    addedAt: string;
}

// Mock data — в реальности загружать из data/fresh/discovered_sources_*.json
const MOCK_DISCOVERED: DiscoveredSource[] = [
    { type: 'telegram', url: 't.me/biznesuz_official', addedAt: '16:20' },
    { type: 'telegram', url: 't.me/startupuzb', addedAt: '16:20' },
    { type: 'facebook', url: 'facebook.com/groups/rabota_tashkent_2026', addedAt: '16:18' },
    { type: 'website_uz', url: 'olx.uz', addedAt: '16:15' },
    { type: 'youtube', url: 'youtube.com/@freelanceuzb', addedAt: '16:12' },
    { type: 'instagram', url: 'instagram.com/shop_tashkent', addedAt: '16:10' },
];

const TYPE_ICONS = {
    telegram: <MessageCircle size={16} />,
    facebook: <Globe size={16} />,
    instagram: <Globe size={16} />,
    youtube: <Globe size={16} />,
    website_uz: <Globe size={16} />,
};

const TYPE_COLORS = {
    telegram: '#0088cc',
    facebook: '#1877f2',
    instagram: '#e4405f',
    youtube: '#ff0000',
    website_uz: '#d4af37',
};

export function DiscoverLog() {
    const [sources] = useState<DiscoveredSource[]>(MOCK_DISCOVERED);
    const [isRefreshing, setIsRefreshing] = useState(false);

    const handleRefresh = () => {
        setIsRefreshing(true);
        setTimeout(() => setIsRefreshing(false), 2000);
    };

    const groupedSources = sources.reduce((acc, source) => {
        if (!acc[source.type]) {
            acc[source.type] = [];
        }
        acc[source.type].push(source);
        return acc;
    }, {} as Record<string, DiscoveredSource[]>);

    return (
        <div className="discover-log">
            <div className="discover-header">
                <div className="discover-title">
                    <Search size={20} />
                    <h3>🔍 Auto-Discovery</h3>
                </div>
                <button
                    className="refresh-btn"
                    onClick={handleRefresh}
                    disabled={isRefreshing}
                >
                    <RefreshCw size={16} className={isRefreshing ? 'spinning' : ''} />
                    {isRefreshing ? 'Ищем...' : 'Обновить'}
                </button>
            </div>

            <p className="discover-subtitle">
                Агент сам находит новые источники данных
            </p>

            <div className="discover-stats">
                {Object.entries(groupedSources).map(([type, items]) => (
                    <div
                        key={type}
                        className="stat-item"
                        style={{ borderColor: TYPE_COLORS[type as keyof typeof TYPE_COLORS] }}
                    >
                        <span className="stat-icon" style={{ color: TYPE_COLORS[type as keyof typeof TYPE_COLORS] }}>
                            {TYPE_ICONS[type as keyof typeof TYPE_ICONS]}
                        </span>
                        <span className="stat-count">{items.length}</span>
                        <span className="stat-type">{type}</span>
                    </div>
                ))}
            </div>

            <div className="discover-list">
                {sources.map((source, index) => (
                    <motion.div
                        key={source.url}
                        className="source-item"
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                    >
                        <span
                            className="source-icon"
                            style={{ color: TYPE_COLORS[source.type] }}
                        >
                            {TYPE_ICONS[source.type]}
                        </span>
                        <span className="source-url">{source.url}</span>
                        <span className="source-time">{source.addedAt}</span>
                    </motion.div>
                ))}
            </div>
        </div>
    );
}
