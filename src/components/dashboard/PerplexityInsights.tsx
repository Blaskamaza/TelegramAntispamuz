import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import './PerplexityInsights.css';

interface PerplexityData {
    timestamp: string;
    region: string;
    trends: {
        hot_topics: Array<{ topic: string; category: string; heat_score: number; source: string }>;
        trending_searches: string[];
    };
    pains: {
        pains: Array<{ pain: string; category: string; severity: string; business_opportunity: string }>;
    };
    opportunities: {
        opportunities: Array<{ title: string; type: string; potential: string }>;
    };
}

export function PerplexityInsights() {
    const [data, setData] = useState<PerplexityData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetch('/data/latest_perplexity.json')
            .then(res => {
                if (!res.ok) throw new Error('Data not found. Run "python agents/perplexity_suite.py full"');
                return res.json();
            })
            .then(setData)
            .catch(err => {
                console.error(err);
                setError(err.message);
            })
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="perplexity-loading">🔄 Загрузка данных Perplexity...</div>;
    if (error) return <div className="perplexity-error">⚠️ {error}</div>;
    if (!data) return null;

    return (
        <div className="perplexity-insights">
            <div className="insights-header">
                <h2>🧠 Perplexity Intelligence ({data.region})</h2>
                <span className="timestamp">Обновлено: {new Date(data.timestamp).toLocaleString()}</span>
            </div>

            <div className="insights-grid">
                {/* Тренды */}
                <motion.div
                    className="insight-card trends-card"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <h3>🔥 Горячие Тренды</h3>
                    <div className="trends-list">
                        {data.trends.hot_topics.slice(0, 3).map((topic, i) => (
                            <div key={i} className="trend-item">
                                <span className="heat-score">🔥 {topic.heat_score}</span>
                                <div className="trend-info">
                                    <h4>{topic.topic}</h4>
                                    <p>{topic.category}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </motion.div>

                {/* Боли */}
                <motion.div
                    className="insight-card pains-card"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                >
                    <h3>💊 Боли Рынка</h3>
                    <div className="pains-list">
                        {data.pains.pains.slice(0, 3).map((pain, i) => (
                            <div key={i} className="pain-item">
                                <span className={`severity ${pain.severity}`}>{pain.severity}</span>
                                <p>"{pain.pain}"</p>
                                <small>💡 {pain.business_opportunity}</small>
                            </div>
                        ))}
                    </div>
                </motion.div>

                {/* Возможности */}
                <motion.div
                    className="insight-card opportunities-card"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                >
                    <h3>🎯 Возможности</h3>
                    <div className="opportunities-list">
                        {data.opportunities.opportunities.slice(0, 3).map((opp, i) => (
                            <div key={i} className="opportunity-item">
                                <h4>{opp.title}</h4>
                                <span className="potential-badge">{opp.potential}</span>
                            </div>
                        ))}
                    </div>
                </motion.div>
            </div>
        </div>
    );
}
