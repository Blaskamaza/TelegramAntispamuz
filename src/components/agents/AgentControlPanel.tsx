import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Play,
    Square,
    RefreshCw,
    ChevronDown,
    ChevronUp,
    Terminal,
    CheckCircle,
    XCircle,
    Clock,
    Loader2
} from 'lucide-react';
import './AgentControlPanel.css';

// Типы агентов
interface Agent {
    id: string;
    name: string;
    file: string;
    icon: string;
    status: 'idle' | 'running' | 'success' | 'error';
    lastRun: string | null;
    lastResult: {
        items?: number;
        pains?: number;
        sources?: number;
        duration?: number;
    } | null;
    logs: string[];
}

// Начальное состояние агентов
const INITIAL_AGENTS: Agent[] = [
    {
        id: 'google_trends',
        name: 'Google Trends',
        file: 'google_trends.py',
        icon: '📊',
        status: 'idle',
        lastRun: null,
        lastResult: null,
        logs: [],
    },
    {
        id: 'youtube',
        name: 'YouTube Scanner',
        file: 'youtube_scanner.py',
        icon: '📺',
        status: 'idle',
        lastRun: null,
        lastResult: null,
        logs: [],
    },
    {
        id: 'telegram',
        name: 'Telegram Scanner',
        file: 'tg_scanner.py',
        icon: '📱',
        status: 'idle',
        lastRun: null,
        lastResult: null,
        logs: [],
    },
    {
        id: 'facebook',
        name: 'Facebook Groups',
        file: 'fb_groups.py',
        icon: '📘',
        status: 'idle',
        lastRun: null,
        lastResult: null,
        logs: [],
    },
    {
        id: 'rss',
        name: 'RSS Scraper',
        file: 'rss_scraper.py',
        icon: '📰',
        status: 'idle',
        lastRun: null,
        lastResult: null,
        logs: [],
    },
    {
        id: 'channel_discovery',
        name: 'Channel Discovery',
        file: 'channel_discovery.py',
        icon: '🔍',
        status: 'idle',
        lastRun: null,
        lastResult: null,
        logs: [],
    },
    {
        id: 'pain_extractor',
        name: 'Pain Extractor',
        file: 'pain_extractor.py',
        icon: '🧠',
        status: 'idle',
        lastRun: null,
        lastResult: null,
        logs: [],
    },
];

// Симуляция результатов агентов
const MOCK_RESULTS: Record<string, Agent['lastResult']> = {
    google_trends: { items: 14, pains: 14, duration: 2.3 },
    youtube: { items: 18, pains: 632, duration: 5.1 },
    telegram: { items: 40, pains: 32, duration: 3.2 },
    facebook: { items: 25, pains: 25, sources: 6, duration: 4.0 },
    rss: { items: 13, pains: 13, duration: 1.8 },
    channel_discovery: { sources: 20, duration: 2.5 },
    pain_extractor: { pains: 264, items: 8, duration: 3.7 },
};

const MOCK_LOGS: Record<string, string[]> = {
    google_trends: [
        '🔍 Google Trends Agent starting...',
        '📍 Region: Uzbekistan (UZ)',
        'ℹ️ pytrends not installed, using mock data',
        '📊 Results: 14 keywords, Growing: 14',
        '🔥 Top: DTM test +150%, IT курсы +89.7%',
        '✅ Saved to data/fresh/trends/uz_2026-01-13.json',
    ],
    youtube: [
        '📺 YouTube Scanner Agent starting...',
        '🔍 Searching: qanday pul ishlash',
        '🔍 Searching: как заработать в Ташкенте',
        '📊 Total videos: 18, comments: 900',
        '🎯 Pains found: 632',
        '✅ Saved to data/fresh/youtube/',
    ],
    telegram: [
        '📱 Telegram Scanner starting...',
        '📡 Channels: 12',
        '🔍 Scanning: @tashkent_help - 5 posts, 5 pains',
        '🔍 Scanning: @freelanceuz - 4 posts, 4 pains',
        '📊 Total pains: 32',
        '✅ Saved to data/fresh/telegram/',
    ],
    facebook: [
        '📘 Facebook Groups starting...',
        '👥 Groups: 6',
        '🔍 Scanning: RabotaUzbekistan - 5 pains',
        '🔍 Scanning: ITUzbekistan - 4 pains',
        '📊 Total pains: 25, New groups: 6',
        '✅ Saved to data/fresh/facebook/',
    ],
    rss: [
        '📰 RSS Scraper starting...',
        '📡 Feeds: 4',
        '🔍 Fetching: daryo.uz - 4 articles',
        '🔍 Fetching: kun.uz - 3 articles',
        '📊 Total pains: 13',
        '✅ Saved to data/fresh/rss/',
    ],
    channel_discovery: [
        '🔎 Channel Discovery starting...',
        '🔍 Searching: telegram канал бизнес узбекистан',
        '🔍 Searching: facebook группа работа ташкент',
        '📊 telegram: 7, facebook: 3, instagram: 3',
        '📝 Updated discovery log: 20 new sources',
        '✅ Saved discovered_sources.json',
    ],
    pain_extractor: [
        '🧠 Pain Extractor starting...',
        '📂 Loading fresh data from 5 sources...',
        '🔍 Pain texts found: 264',
        '🧠 Analyzing with AI...',
        '📊 Categories: 8',
        '🔥 Top: Работа (136), Финансы (41), Покупки (18)',
        '✅ Saved top_pains_2026-01-13.md',
    ],
};

export function AgentControlPanel() {
    const [agents, setAgents] = useState<Agent[]>(INITIAL_AGENTS);
    const [expandedAgent, setExpandedAgent] = useState<string | null>(null);
    const [isRunningAll, setIsRunningAll] = useState(false);

    // Запуск одного агента
    const runAgent = useCallback(async (agentId: string) => {
        setAgents(prev => prev.map(a =>
            a.id === agentId
                ? { ...a, status: 'running', logs: ['⏳ Starting...'] }
                : a
        ));

        // Симуляция работы агента
        const logs = MOCK_LOGS[agentId] || ['Running...'];

        for (let i = 0; i < logs.length; i++) {
            await new Promise(r => setTimeout(r, 500));
            setAgents(prev => prev.map(a =>
                a.id === agentId
                    ? { ...a, logs: logs.slice(0, i + 1) }
                    : a
            ));
        }

        // Завершение
        await new Promise(r => setTimeout(r, 300));
        setAgents(prev => prev.map(a =>
            a.id === agentId
                ? {
                    ...a,
                    status: 'success',
                    lastRun: new Date().toLocaleTimeString('ru-RU'),
                    lastResult: MOCK_RESULTS[agentId] || null,
                }
                : a
        ));
    }, []);

    // Остановка агента
    const stopAgent = useCallback((agentId: string) => {
        setAgents(prev => prev.map(a =>
            a.id === agentId
                ? { ...a, status: 'idle', logs: [...a.logs, '⏹ Stopped by user'] }
                : a
        ));
    }, []);

    // Запуск всех агентов
    const runAllAgents = useCallback(async () => {
        setIsRunningAll(true);

        for (const agent of agents) {
            if (agent.status !== 'running') {
                await runAgent(agent.id);
                await new Promise(r => setTimeout(r, 200));
            }
        }

        setIsRunningAll(false);
    }, [agents, runAgent]);

    // Сброс всех агентов
    const resetAllAgents = useCallback(() => {
        setAgents(INITIAL_AGENTS);
    }, []);

    // Подсчёт статистики
    const stats = {
        total: agents.length,
        running: agents.filter(a => a.status === 'running').length,
        success: agents.filter(a => a.status === 'success').length,
        error: agents.filter(a => a.status === 'error').length,
    };

    const getStatusIcon = (status: Agent['status']) => {
        switch (status) {
            case 'running': return <Loader2 className="status-icon spinning" size={16} />;
            case 'success': return <CheckCircle className="status-icon success" size={16} />;
            case 'error': return <XCircle className="status-icon error" size={16} />;
            default: return <Clock className="status-icon idle" size={16} />;
        }
    };

    const getStatusText = (status: Agent['status']) => {
        switch (status) {
            case 'running': return 'Running';
            case 'success': return 'Done';
            case 'error': return 'Error';
            default: return 'Ready';
        }
    };

    return (
        <div className="agent-control-panel">
            {/* Header */}
            <div className="panel-header">
                <div className="panel-title">
                    <span className="panel-icon">🤖</span>
                    <h2>Agent Control Panel</h2>
                </div>
                <div className="panel-actions">
                    <button
                        className="action-btn primary"
                        onClick={runAllAgents}
                        disabled={isRunningAll}
                    >
                        {isRunningAll ? (
                            <><Loader2 className="spinning" size={16} /> Running...</>
                        ) : (
                            <><Play size={16} /> Run All</>
                        )}
                    </button>
                    <button
                        className="action-btn secondary"
                        onClick={resetAllAgents}
                    >
                        <RefreshCw size={16} /> Reset
                    </button>
                </div>
            </div>

            {/* Stats Bar */}
            <div className="stats-bar">
                <div className="stat">
                    <span className="stat-value">{stats.total}</span>
                    <span className="stat-label">Total</span>
                </div>
                <div className="stat running">
                    <span className="stat-value">{stats.running}</span>
                    <span className="stat-label">Running</span>
                </div>
                <div className="stat success">
                    <span className="stat-value">{stats.success}</span>
                    <span className="stat-label">Done</span>
                </div>
                <div className="stat error">
                    <span className="stat-value">{stats.error}</span>
                    <span className="stat-label">Errors</span>
                </div>
            </div>

            {/* Agent List */}
            <div className="agent-list">
                {agents.map((agent) => (
                    <motion.div
                        key={agent.id}
                        className={`agent-item ${agent.status}`}
                        layout
                    >
                        <div
                            className="agent-main"
                            onClick={() => setExpandedAgent(
                                expandedAgent === agent.id ? null : agent.id
                            )}
                        >
                            <div className="agent-icon">{agent.icon}</div>

                            <div className="agent-info">
                                <div className="agent-name">{agent.name}</div>
                                <div className="agent-file">{agent.file}</div>
                            </div>

                            <div className="agent-status">
                                {getStatusIcon(agent.status)}
                                <span className={`status-text ${agent.status}`}>
                                    {getStatusText(agent.status)}
                                </span>
                            </div>

                            {agent.lastResult && (
                                <div className="agent-result">
                                    {agent.lastResult.pains && (
                                        <span className="result-item">🎯 {agent.lastResult.pains}</span>
                                    )}
                                    {agent.lastResult.items && (
                                        <span className="result-item">📦 {agent.lastResult.items}</span>
                                    )}
                                    {agent.lastResult.sources && (
                                        <span className="result-item">🔗 {agent.lastResult.sources}</span>
                                    )}
                                </div>
                            )}

                            <div className="agent-actions">
                                {agent.status === 'running' ? (
                                    <button
                                        className="agent-btn stop"
                                        onClick={(e) => { e.stopPropagation(); stopAgent(agent.id); }}
                                    >
                                        <Square size={14} />
                                    </button>
                                ) : (
                                    <button
                                        className="agent-btn run"
                                        onClick={(e) => { e.stopPropagation(); runAgent(agent.id); }}
                                    >
                                        <Play size={14} />
                                    </button>
                                )}

                                <button className="agent-btn expand">
                                    {expandedAgent === agent.id ? (
                                        <ChevronUp size={14} />
                                    ) : (
                                        <ChevronDown size={14} />
                                    )}
                                </button>
                            </div>
                        </div>

                        {/* Expanded Logs */}
                        <AnimatePresence>
                            {expandedAgent === agent.id && (
                                <motion.div
                                    className="agent-logs"
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: 'auto', opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                    transition={{ duration: 0.2 }}
                                >
                                    <div className="logs-header">
                                        <Terminal size={14} />
                                        <span>Logs</span>
                                        {agent.lastRun && (
                                            <span className="last-run">Last run: {agent.lastRun}</span>
                                        )}
                                    </div>
                                    <div className="logs-content">
                                        {agent.logs.length > 0 ? (
                                            agent.logs.map((log, i) => (
                                                <div key={i} className="log-line">{log}</div>
                                            ))
                                        ) : (
                                            <div className="log-line muted">No logs yet. Click Run to start.</div>
                                        )}
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </motion.div>
                ))}
            </div>

            {/* Pipeline Progress */}
            <div className="pipeline-progress">
                <div className="pipeline-label">Pipeline Progress</div>
                <div className="pipeline-bar">
                    <motion.div
                        className="pipeline-fill"
                        initial={{ width: 0 }}
                        animate={{ width: `${(stats.success / stats.total) * 100}%` }}
                        transition={{ duration: 0.5 }}
                    />
                </div>
                <div className="pipeline-text">
                    {stats.success}/{stats.total} agents completed
                </div>
            </div>
        </div>
    );
}
