import { motion } from 'framer-motion';
import { Plus, ArrowRight, Clock, Zap } from 'lucide-react';
import { useAppStore } from '../../stores/useAppStore';
import { QUEST_LEVELS } from '../../types';
import './QuestList.css';

export function QuestList() {
    const { quests, addQuest, setActiveQuest, advanceQuestStatus } = useAppStore();

    const handleAddQuest = () => {
        addQuest({
            title: 'Новый квест',
            description: 'Найди боль пользователей и создай решение',
            status: 'idea',
            progress: 0,
            xp: 0,
        });
    };

    return (
        <div className="quest-list">
            <div className="quest-header">
                <h2>🗺️ Активные квесты</h2>
                <button className="btn btn-primary" onClick={handleAddQuest}>
                    <Plus size={18} />
                    Новый квест
                </button>
            </div>

            {quests.length === 0 ? (
                <motion.div
                    className="empty-state"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                >
                    <div className="empty-icon">🚀</div>
                    <h3>Нет активных квестов</h3>
                    <p>Создайте первый квест, чтобы начать строить свою империю</p>
                    <button className="btn btn-primary" onClick={handleAddQuest}>
                        <Plus size={18} />
                        Создать квест
                    </button>
                </motion.div>
            ) : (
                <div className="quest-grid">
                    {quests.map((quest, index) => {
                        const level = QUEST_LEVELS[quest.status];
                        const nextStatus = getNextStatus(quest.status);
                        const nextLevel = nextStatus ? QUEST_LEVELS[nextStatus] : null;

                        return (
                            <motion.div
                                key={quest.id}
                                className={`quest-card status-${quest.status}`}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.1 }}
                                onClick={() => setActiveQuest(quest.id)}
                            >
                                <div className="quest-status-badge">
                                    <span className="status-icon">{level.icon}</span>
                                    <span className="status-name">{level.name}</span>
                                </div>

                                <h3 className="quest-title">{quest.title}</h3>
                                <p className="quest-description">{quest.description}</p>

                                <div className="quest-progress">
                                    <div className="progress-bar">
                                        <motion.div
                                            className="progress-fill"
                                            initial={{ width: 0 }}
                                            animate={{ width: `${quest.progress}%` }}
                                            transition={{ duration: 0.5 }}
                                        />
                                    </div>
                                    <span className="progress-text">{quest.progress}%</span>
                                </div>

                                <div className="quest-footer">
                                    <div className="quest-xp">
                                        <Zap size={14} />
                                        <span>+{level.xpRequired} XP</span>
                                    </div>

                                    {nextLevel && (
                                        <button
                                            className="advance-btn"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                advanceQuestStatus(quest.id);
                                            }}
                                        >
                                            <span>{nextLevel.icon} {nextLevel.name}</span>
                                            <ArrowRight size={14} />
                                        </button>
                                    )}
                                </div>
                            </motion.div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}

function getNextStatus(current: string) {
    const order = ['idea', 'research', 'prototype', 'launch', 'monetize'];
    const index = order.indexOf(current);
    return index < order.length - 1 ? order[index + 1] : null;
}
