import { motion } from 'framer-motion';
import { AlertCircle, TrendingUp, Users, DollarSign, Lightbulb } from 'lucide-react';
import type { ReactNode } from 'react';
import './PainCard.css';

interface PainCardProps {
    category: string;
    frequency: number;
    potential: 'низкий' | 'средний' | 'высокий' | 'средний-высокий';
    priceHint: string;
    businessIdea: string;
    sources: string[];
    examples: string[];
    index?: number;
}

const CATEGORY_ICONS: Record<string, ReactNode> = {
    'Работа и заработок': <Users size={24} />,
    'Образование': <Lightbulb size={24} />,
    'Финансы': <DollarSign size={24} />,
    'Технологии': <AlertCircle size={24} />,
    'default': <TrendingUp size={24} />,
};

const POTENTIAL_COLORS = {
    'низкий': '#71717a',
    'средний': '#f59e0b',
    'высокий': '#10b981',
    'средний-высокий': '#3b82f6',
};

export function PainCard({
    category,
    frequency,
    potential,
    priceHint,
    businessIdea,
    sources,
    examples,
    index = 0,
}: PainCardProps) {
    const icon = CATEGORY_ICONS[category] || CATEGORY_ICONS['default'];
    const potentialColor = POTENTIAL_COLORS[potential] || POTENTIAL_COLORS['средний'];

    return (
        <motion.div
            className="pain-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
        >
            <div className="pain-card-header">
                <div className="pain-icon">{icon}</div>
                <div className="pain-info">
                    <h3 className="pain-category">{category}</h3>
                    <div className="pain-meta">
                        <span className="pain-frequency">📊 {frequency} упоминаний</span>
                        <span
                            className="pain-potential"
                            style={{ backgroundColor: potentialColor }}
                        >
                            {potential}
                        </span>
                    </div>
                </div>
            </div>

            <div className="pain-price">
                <span className="price-label">💰 Цена решения:</span>
                <span className="price-value">{priceHint}</span>
            </div>

            <div className="pain-idea">
                <h4>💡 Бизнес-идея</h4>
                <p>{businessIdea}</p>
            </div>

            <div className="pain-examples">
                <h4>📝 Примеры болей</h4>
                <ul>
                    {examples.slice(0, 3).map((example, i) => (
                        <li key={i}>"{example}"</li>
                    ))}
                </ul>
            </div>

            <div className="pain-sources">
                {sources.map((source, i) => (
                    <span key={i} className="source-tag">{source}</span>
                ))}
            </div>
        </motion.div>
    );
}
