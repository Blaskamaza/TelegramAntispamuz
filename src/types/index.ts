// ========== КВЕСТЫ ==========
export interface Quest {
  id: string;
  title: string;
  description: string;
  status: 'idea' | 'research' | 'prototype' | 'launch' | 'monetize';
  progress: number; // 0-100
  xp: number;
  createdAt: Date;
  updatedAt: Date;
  painPoint?: string;
  businessPlan?: BusinessPlan;
}

export type QuestStatus = Quest['status'];

export const QUEST_LEVELS: Record<QuestStatus, { name: string; xpRequired: number; icon: string }> = {
  idea: { name: 'Идея', xpRequired: 0, icon: '💡' },
  research: { name: 'Исследование', xpRequired: 100, icon: '🔍' },
  prototype: { name: 'Прототип', xpRequired: 500, icon: '🛠️' },
  launch: { name: 'Запуск', xpRequired: 1500, icon: '🚀' },
  monetize: { name: 'Монетизация', xpRequired: 5000, icon: '💰' },
};

// ========== АГЕНТЫ ==========
export interface Agent {
  id: string;
  name: string;
  type: 'search' | 'marketing' | 'developer' | 'sales';
  status: 'idle' | 'working' | 'completed' | 'error';
  currentTask?: string;
  progress: number;
  avatar: string;
}

export const AGENT_TYPES = {
  search: { name: 'Поисковый агент', icon: '🔎', color: '#3b82f6' },
  marketing: { name: 'Маркетолог', icon: '📢', color: '#f59e0b' },
  developer: { name: 'Разработчик', icon: '💻', color: '#10b981' },
  sales: { name: 'Продажник', icon: '🤝', color: '#ef4444' },
} as const;

// ========== ТРЕНДЫ ==========
export interface Trend {
  id: string;
  title: string;
  description: string;
  source: 'google' | 'reddit' | 'youtube' | 'twitter';
  painScore: number; // 1-10 насколько это "боль"
  monetizationPotential: number; // 1-10
  keywords: string[];
  discoveredAt: Date;
}

// ========== БИЗНЕС-ПЛАН ==========
export interface BusinessPlan {
  id: string;
  questId: string;
  problem: string;
  solution: string;
  targetAudience: string;
  monetizationStrategy: string;
  estimatedCost: number;
  estimatedRevenue: number;
  timeToMvp: string; // "2-3 дня"
  techStack: string[];
  createdAt: Date;
}

// ========== ГЕЙМИФИКАЦИЯ ==========
export interface UserStats {
  totalXp: number;
  level: number;
  questsCompleted: number;
  revenueGenerated: number;
  achievements: Achievement[];
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  unlockedAt?: Date;
}

export const ACHIEVEMENTS: Achievement[] = [
  { id: 'first-blood', name: 'First Blood', description: 'Найдена первая боль пользователей', icon: '🔥' },
  { id: 'speed-demon', name: 'Speed Demon', description: 'MVP за 48 часов', icon: '⚡' },
  { id: 'money-maker', name: 'Money Maker', description: 'Первая продажа', icon: '💎' },
  { id: 'empire-builder', name: 'Empire Builder', description: '10 активных бизнесов', icon: '👑' },
];

// ========== UI ==========
export interface NavItem {
  id: string;
  label: string;
  icon: string;
  path: string;
}
