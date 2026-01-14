import { motion } from 'framer-motion';
import { Sidebar } from '../dashboard/Sidebar';
import { StatsCards } from '../dashboard/StatsCards';
import { QuestList } from '../quests/QuestList';
import { PainCard } from '../ui/PainCard';
import { DiscoverLog } from '../ui/DiscoverLog';
import { AgentControlPanel } from '../agents/AgentControlPanel';
import { PerplexityInsights } from './PerplexityInsights';
import { useAppStore } from '../../stores/useAppStore';
import './Layout.css';

// Mock данные болей
const MOCK_PAINS = [
    {
        category: 'Работа и заработок',
        frequency: 156,
        potential: 'высокий' as const,
        priceHint: '30000-50000 сум',
        businessIdea: 'Телеграм-бот для поиска удалённой работы в Узбекистане с фильтрами по зарплате и опыту',
        sources: ['Telegram', 'Facebook', 'YouTube'],
        examples: ['Ищу работу! SMM-менеджер, опыт 2 года', 'Где найти работу на дому для мамы?', 'Подскажите вакансии в IT'],
    },
    {
        category: 'Образование',
        frequency: 134,
        potential: 'высокий' as const,
        priceHint: '40000-50000 сум',
        businessIdea: 'Платформа подготовки к DTM с AI-репетитором на узбекском языке',
        sources: ['Google Trends', 'YouTube', 'Telegram'],
        examples: ['Подготовка к DTM-2026, помогите!', 'Ищу репетитора по математике', 'Какие книги нужны для поступления?'],
    },
    {
        category: 'Финансы',
        frequency: 98,
        potential: 'средний-высокий' as const,
        priceHint: '20000-40000 сум',
        businessIdea: 'Агрегатор микрокредитов с рейтингом и отзывами пользователей',
        sources: ['Facebook', 'RSS News'],
        examples: ['Где оформить кредит без отказа?', 'Проблема с оплатой, банк отклоняет', 'Как оплатить из Узбекистана?'],
    },
    {
        category: 'Технологии',
        frequency: 87,
        potential: 'высокий' as const,
        priceHint: '30000-50000 сум',
        businessIdea: 'Сервис техподдержки для популярных приложений на узбекском',
        sources: ['Telegram', 'YouTube'],
        examples: ['Не работает приложение, что делать?', 'Подскажите хорошие курсы Python', 'Как вывести деньги из Upwork?'],
    },
];

export function Layout() {
    const { sidebarOpen, currentView } = useAppStore();

    const renderContent = () => {
        switch (currentView) {
            case 'dashboard':
                return (
                    <>
                        <div className="page-header">
                            <h1>🇺🇿 UZ AI Factory</h1>
                            <p>Конвейер ИИ-бизнесов Узбекистана</p>
                        </div>
                        <StatsCards />
                        <div className="dashboard-grid">
                            <div className="main-content-area">
                                <QuestList />
                            </div>
                            <div className="sidebar-area">
                                <DiscoverLog />
                            </div>
                        </div>
                    </>
                );
            case 'quests':
                return (
                    <>
                        <div className="page-header">
                            <h1>🗺️ Квесты</h1>
                            <p>Твои активные бизнес-проекты</p>
                        </div>
                        <QuestList />
                    </>
                );
            case 'trends':
                return (
                    <>
                        <div className="page-header">
                            <h1>🔥 Боли Пользователей</h1>
                            <p>Найденные проблемы узбекского рынка (за которые готовы платить)</p>
                        </div>
                        <div className="pains-grid">
                            {MOCK_PAINS.map((pain, index) => (
                                <PainCard key={pain.category} {...pain} index={index} />
                            ))}
                        </div>
                        <PerplexityInsights />
                    </>
                );
            case 'agents':
                return (
                    <>
                        <div className="page-header">
                            <h1>🤖 Agent Control Panel</h1>
                            <p>Управление Python агентами в реальном времени</p>
                        </div>
                        <AgentControlPanel />
                    </>
                );
            case 'settings':
                return (
                    <>
                        <div className="page-header">
                            <h1>⚙️ Настройки</h1>
                            <p>Конфигурация системы</p>
                        </div>
                        <div className="settings-info">
                            <h3>📁 Структура данных</h3>
                            <pre>{`data/
├── fresh/           ← Свежие данные (< 7 дней)
│   ├── trends/      Google Trends
│   ├── youtube/     Комменты YouTube
│   ├── telegram/    Посты Telegram
│   ├── facebook/    Посты Facebook
│   └── rss/         Новости RSS
└── archive/         Старые данные`}</pre>

                            <h3>🔑 API Ключи (бесплатный уровень)</h3>
                            <ul>
                                <li>✅ Google Trends — без ключа</li>
                                <li>✅ YouTube Data API — 10,000 единиц/день</li>
                                <li>✅ Gemini 1.5 Flash — бесплатно</li>
                                <li>✅ Yandex.uz — без ключа</li>
                                <li>✅ Facebook/Telegram — парсинг публичных данных</li>
                            </ul>
                        </div>
                    </>
                );
            default:
                return null;
        }
    };

    return (
        <div className="app-layout">
            <Sidebar />
            <motion.main
                className="main-content"
                animate={{
                    marginLeft: sidebarOpen ? 260 : 72,
                }}
                transition={{ duration: 0.3, ease: 'easeInOut' }}
            >
                <div className="content-container">
                    {renderContent()}
                </div>
            </motion.main>
        </div>
    );
}
