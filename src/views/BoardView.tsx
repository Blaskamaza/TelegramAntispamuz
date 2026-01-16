/**
 * BoardView — Kanban Board with Drag-and-Drop
 * 
 * Features:
 * - Drag tasks between columns (backlog → in_progress → review → done)
 * - Real-time status updates via API
 * - Live agent logs via WebSocket
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
    DndContext,
    DragEndEvent,
    DragOverlay,
    DragStartEvent,
    closestCorners,
    PointerSensor,
    useSensor,
    useSensors,
} from '@dnd-kit/core';
import {
    SortableContext,
    verticalListSortingStrategy,
    useSortable,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

// === Types ===
interface Task {
    task_id: string;
    title: string;
    agent: string;
    status: string;
    skill?: string;
    xp_reward: number;
    branch?: string;
    created_at?: string;
}

interface Column {
    id: string;
    title: string;
    color: string;
}

// === API ===
const API_BASE = '/api/board';

async function fetchTasks(): Promise<Task[]> {
    const res = await fetch(`${API_BASE}/tasks`);
    if (!res.ok) throw new Error('Failed to fetch tasks');
    return res.json();
}

async function updateTaskStatus(taskId: string, status: string): Promise<void> {
    const res = await fetch(`${API_BASE}/tasks/${taskId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
    });
    if (!res.ok) throw new Error('Failed to update task');
}

async function createTask(id: string, title: string, agent: string): Promise<Task> {
    const res = await fetch(`${API_BASE}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, title, agent }),
    });
    if (!res.ok) throw new Error('Failed to create task');
    return res.json();
}

// === Constants ===
const COLUMNS: Column[] = [
    { id: 'backlog', title: '📥 Backlog', color: '#6b7280' },
    { id: 'in_progress', title: '🔄 In Progress', color: '#3b82f6' },
    { id: 'review', title: '👀 Review', color: '#f59e0b' },
    { id: 'done', title: '✅ Done', color: '#10b981' },
];

const AGENTS = ['cpo', 'tech_lead', 'cmo', 'sales_head', 'qa_lead'];

// === Components ===

// Task Card (Draggable)
function TaskCard({ task, logs }: { task: Task; logs?: string }) {
    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        transition,
        isDragging,
    } = useSortable({ id: task.task_id });

    const style: React.CSSProperties = {
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.5 : 1,
        background: 'linear-gradient(145deg, #1e1e2e, #2a2a3e)',
        border: '1px solid #3a3a4a',
        borderRadius: '12px',
        padding: '12px',
        marginBottom: '8px',
        cursor: 'grab',
        boxShadow: isDragging ? '0 8px 20px rgba(0,0,0,0.4)' : '0 2px 8px rgba(0,0,0,0.2)',
    };

    return (
        <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h4 style={{ margin: 0, fontSize: '14px', color: '#fff' }}>{task.title}</h4>
                <span style={{
                    fontSize: '10px',
                    background: '#4a4a5a',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    color: '#aaa'
                }}>
                    {task.agent}
                </span>
            </div>

            <div style={{ fontSize: '11px', color: '#888', marginTop: '6px' }}>
                <span>🆔 {task.task_id}</span>
                {task.xp_reward > 0 && <span style={{ marginLeft: '8px' }}>⭐ {task.xp_reward} XP</span>}
            </div>

            {logs && (
                <pre style={{
                    fontSize: '9px',
                    background: '#0a0a0f',
                    padding: '4px',
                    borderRadius: '4px',
                    marginTop: '8px',
                    maxHeight: '60px',
                    overflow: 'hidden',
                    color: '#6a6'
                }}>
                    {logs.slice(-100)}
                </pre>
            )}
        </div>
    );
}

// Column (Droppable)
function KanbanColumn({ column, tasks, logs }: {
    column: Column;
    tasks: Task[];
    logs: Record<string, string>;
}) {
    const taskIds = tasks.map(t => t.task_id);

    return (
        <div style={{
            flex: 1,
            minWidth: '280px',
            maxWidth: '320px',
            background: '#16161e',
            borderRadius: '16px',
            padding: '16px',
            border: `2px solid ${column.color}33`,
        }}>
            <h3 style={{
                margin: '0 0 16px 0',
                color: column.color,
                fontSize: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
            }}>
                {column.title}
                <span style={{
                    fontSize: '12px',
                    background: `${column.color}22`,
                    padding: '2px 8px',
                    borderRadius: '10px'
                }}>
                    {tasks.length}
                </span>
            </h3>

            <SortableContext items={taskIds} strategy={verticalListSortingStrategy}>
                <div style={{ minHeight: '200px' }}>
                    {tasks.map(task => (
                        <TaskCard key={task.task_id} task={task} logs={logs[task.task_id]} />
                    ))}
                </div>
            </SortableContext>
        </div>
    );
}

// New Task Form
function NewTaskForm({ onSubmit }: { onSubmit: (id: string, title: string, agent: string) => void }) {
    const [id, setId] = useState('');
    const [title, setTitle] = useState('');
    const [agent, setAgent] = useState('cpo');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!id || !title) return;

        setLoading(true);
        try {
            await onSubmit(id, title, agent);
            setId('');
            setTitle('');
        } finally {
            setLoading(false);
        }
    };

    const inputStyle: React.CSSProperties = {
        background: '#1e1e2e',
        border: '1px solid #3a3a4a',
        borderRadius: '8px',
        padding: '8px 12px',
        color: '#fff',
        fontSize: '14px',
    };

    return (
        <form onSubmit={handleSubmit} style={{
            display: 'flex',
            gap: '12px',
            marginBottom: '24px',
            flexWrap: 'wrap'
        }}>
            <input
                type="text"
                placeholder="Task ID (e.g., delivery-01)"
                value={id}
                onChange={e => setId(e.target.value)}
                style={{ ...inputStyle, width: '180px' }}
                required
            />
            <input
                type="text"
                placeholder="Task title"
                value={title}
                onChange={e => setTitle(e.target.value)}
                style={{ ...inputStyle, flex: 1, minWidth: '200px' }}
                required
            />
            <select
                value={agent}
                onChange={e => setAgent(e.target.value)}
                style={{ ...inputStyle, width: '120px' }}
            >
                {AGENTS.map(a => (
                    <option key={a} value={a}>{a}</option>
                ))}
            </select>
            <button
                type="submit"
                disabled={loading}
                style={{
                    background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                    border: 'none',
                    borderRadius: '8px',
                    padding: '8px 20px',
                    color: '#fff',
                    fontWeight: 'bold',
                    cursor: loading ? 'wait' : 'pointer',
                    opacity: loading ? 0.7 : 1,
                }}
            >
                {loading ? '⏳' : '➕ Create Task'}
            </button>
        </form>
    );
}

// === Main Board ===
export function BoardView() {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [logs, setLogs] = useState<Record<string, string>>({});
    const [activeId, setActiveId] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    const sensors = useSensors(
        useSensor(PointerSensor, {
            activationConstraint: { distance: 8 },
        })
    );

    // Fetch tasks
    const loadTasks = useCallback(async () => {
        try {
            const data = await fetchTasks();
            setTasks(data);
            setError(null);
        } catch (e) {
            setError('Failed to load tasks');
            console.error(e);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadTasks();
        // Refresh every 10 seconds
        const interval = setInterval(loadTasks, 10000);
        return () => clearInterval(interval);
    }, [loadTasks]);

    // WebSocket for live logs
    useEffect(() => {
        const wsUrl = `ws://${window.location.host}/api/factory/ws`;
        let ws: WebSocket | null = null;

        try {
            ws = new WebSocket(wsUrl);
            ws.onmessage = (e) => {
                const data = JSON.parse(e.data);
                if (data.taskId && data.log) {
                    setLogs(prev => ({ ...prev, [data.taskId]: data.log }));
                }
            };
            ws.onerror = () => console.log('WebSocket not available');
        } catch {
            // WebSocket not available
        }

        return () => ws?.close();
    }, []);

    // Drag handlers
    const handleDragStart = (event: DragStartEvent) => {
        setActiveId(event.active.id as string);
    };

    const handleDragEnd = async (event: DragEndEvent) => {
        const { active, over } = event;
        setActiveId(null);

        if (!over) return;

        const taskId = active.id as string;
        const newStatus = over.id as string;

        // Find task
        const task = tasks.find(t => t.task_id === taskId);
        if (!task || task.status === newStatus) return;

        // Optimistic update
        setTasks(prev => prev.map(t =>
            t.task_id === taskId ? { ...t, status: newStatus } : t
        ));

        // API call
        try {
            await updateTaskStatus(taskId, newStatus);
        } catch (e) {
            // Revert on error
            loadTasks();
            setError('Failed to update task');
        }
    };

    // Create task
    const handleCreateTask = async (id: string, title: string, agent: string) => {
        try {
            const newTask = await createTask(id, title, agent);
            setTasks(prev => [...prev, newTask]);
        } catch (e) {
            setError('Failed to create task');
        }
    };

    // Get active task for overlay
    const activeTask = activeId ? tasks.find(t => t.task_id === activeId) : null;

    if (loading) {
        return (
            <div style={{ padding: '40px', textAlign: 'center', color: '#888' }}>
                ⏳ Loading tasks...
            </div>
        );
    }

    return (
        <div style={{
            padding: '24px',
            minHeight: '100vh',
            background: 'linear-gradient(180deg, #0a0a0f 0%, #12121a 100%)',
        }}>
            <h1 style={{
                color: '#fff',
                marginBottom: '24px',
                fontSize: '28px',
                display: 'flex',
                alignItems: 'center',
                gap: '12px'
            }}>
                🏭 Vibe-Lite Kanban
                <span style={{ fontSize: '14px', color: '#666' }}>
                    Git Worktree Factory
                </span>
            </h1>

            {error && (
                <div style={{
                    background: '#ff000022',
                    border: '1px solid #ff0000',
                    borderRadius: '8px',
                    padding: '12px',
                    marginBottom: '16px',
                    color: '#ff6666'
                }}>
                    ⚠️ {error}
                </div>
            )}

            <NewTaskForm onSubmit={handleCreateTask} />

            <DndContext
                sensors={sensors}
                collisionDetection={closestCorners}
                onDragStart={handleDragStart}
                onDragEnd={handleDragEnd}
            >
                <div style={{
                    display: 'flex',
                    gap: '16px',
                    overflowX: 'auto',
                    paddingBottom: '16px'
                }}>
                    {COLUMNS.map(column => (
                        <KanbanColumn
                            key={column.id}
                            column={column}
                            tasks={tasks.filter(t => t.status === column.id)}
                            logs={logs}
                        />
                    ))}
                </div>

                <DragOverlay>
                    {activeTask && <TaskCard task={activeTask} />}
                </DragOverlay>
            </DndContext>

            <div style={{
                marginTop: '24px',
                fontSize: '12px',
                color: '#555',
                textAlign: 'center'
            }}>
                💡 Drag tasks between columns to update status • Auto-refresh every 10s
            </div>
        </div>
    );
}

export default BoardView;
