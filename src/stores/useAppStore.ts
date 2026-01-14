import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Quest, QuestStatus, UserStats, Achievement, ACHIEVEMENTS } from '../types';

interface AppState {
    // === Квесты ===
    quests: Quest[];
    activeQuestId: string | null;

    // === Геймификация ===
    userStats: UserStats;

    // === UI ===
    sidebarOpen: boolean;
    currentView: 'dashboard' | 'quests' | 'trends' | 'agents' | 'settings';

    // === Actions: Квесты ===
    addQuest: (quest: Omit<Quest, 'id' | 'createdAt' | 'updatedAt'>) => void;
    updateQuest: (id: string, updates: Partial<Quest>) => void;
    deleteQuest: (id: string) => void;
    setActiveQuest: (id: string | null) => void;
    advanceQuestStatus: (id: string) => void;

    // === Actions: XP ===
    addXp: (amount: number) => void;
    unlockAchievement: (achievementId: string) => void;

    // === Actions: UI ===
    toggleSidebar: () => void;
    setCurrentView: (view: AppState['currentView']) => void;
}

const generateId = () => Math.random().toString(36).substring(2, 9);

const STATUS_ORDER: QuestStatus[] = ['idea', 'research', 'prototype', 'launch', 'monetize'];
const XP_PER_STATUS: Record<QuestStatus, number> = {
    idea: 0,
    research: 50,
    prototype: 150,
    launch: 300,
    monetize: 500,
};

export const useAppStore = create<AppState>()(
    persist(
        (set, get) => ({
            // === Initial State ===
            quests: [],
            activeQuestId: null,
            userStats: {
                totalXp: 0,
                level: 1,
                questsCompleted: 0,
                revenueGenerated: 0,
                achievements: [],
            },
            sidebarOpen: true,
            currentView: 'dashboard',

            // === Квесты ===
            addQuest: (questData) => {
                const quest: Quest = {
                    ...questData,
                    id: generateId(),
                    createdAt: new Date(),
                    updatedAt: new Date(),
                };
                set((state) => ({ quests: [...state.quests, quest] }));
            },

            updateQuest: (id, updates) => {
                set((state) => ({
                    quests: state.quests.map((q) =>
                        q.id === id ? { ...q, ...updates, updatedAt: new Date() } : q
                    ),
                }));
            },

            deleteQuest: (id) => {
                set((state) => ({
                    quests: state.quests.filter((q) => q.id !== id),
                    activeQuestId: state.activeQuestId === id ? null : state.activeQuestId,
                }));
            },

            setActiveQuest: (id) => {
                set({ activeQuestId: id });
            },

            advanceQuestStatus: (id) => {
                const quest = get().quests.find((q) => q.id === id);
                if (!quest) return;

                const currentIndex = STATUS_ORDER.indexOf(quest.status);
                if (currentIndex < STATUS_ORDER.length - 1) {
                    const newStatus = STATUS_ORDER[currentIndex + 1];
                    const xpGain = XP_PER_STATUS[newStatus];

                    get().updateQuest(id, { status: newStatus, progress: 0 });
                    get().addXp(xpGain);

                    // Проверка достижений
                    if (newStatus === 'monetize') {
                        get().unlockAchievement('money-maker');
                        set((state) => ({
                            userStats: {
                                ...state.userStats,
                                questsCompleted: state.userStats.questsCompleted + 1,
                            },
                        }));
                    }
                }
            },

            // === XP ===
            addXp: (amount) => {
                set((state) => {
                    const newXp = state.userStats.totalXp + amount;
                    const newLevel = Math.floor(newXp / 500) + 1;
                    return {
                        userStats: {
                            ...state.userStats,
                            totalXp: newXp,
                            level: newLevel,
                        },
                    };
                });
            },

            unlockAchievement: (achievementId) => {
                set((state) => {
                    const alreadyUnlocked = state.userStats.achievements.some(
                        (a) => a.id === achievementId
                    );
                    if (alreadyUnlocked) return state;

                    const achievement = {
                        id: achievementId,
                        name: achievementId,
                        description: '',
                        icon: '🏆',
                        unlockedAt: new Date(),
                    };

                    return {
                        userStats: {
                            ...state.userStats,
                            achievements: [...state.userStats.achievements, achievement],
                        },
                    };
                });
            },

            // === UI ===
            toggleSidebar: () => {
                set((state) => ({ sidebarOpen: !state.sidebarOpen }));
            },

            setCurrentView: (view) => {
                set({ currentView: view });
            },
        }),
        {
            name: 'ai-business-pipeline',
            partialize: (state) => ({
                quests: state.quests,
                userStats: state.userStats,
            }),
        }
    )
);
