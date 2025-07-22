import React, {useState, useMemo, useEffect} from 'react';
import {motion} from 'framer-motion';
import {AnimatedGridPattern} from '../components/magicui/animated-grid-pattern.tsx';
import {Divider, Input, Link, Progress, ScrollShadow, Spinner, Tooltip} from '@heroui/react';
import {IoCheckmarkCircleOutline, IoSearch} from 'react-icons/io5';
import type {ProcessingState, RecordingAnalysis} from '../utils/api.types.ts';
import {IoMdAddCircleOutline} from 'react-icons/io';
import {NewRecordingPage} from './New/NewRecordingPage.tsx';
import {downloadConversationWav, fetchRecordingAnalysis, listAudio, removeAudio} from '../utils/api.tools.ts';
import {ConversationPage} from './ConversationPage.tsx';
import { io } from 'socket.io-client';


const TaskItem = React.memo(function TaskItem({task, onClick, onDelete}: {
    task: { id: string, summary: string, state: ProcessingState },
    onClick: () => void,
    onDelete: () => void
}) {
    // Right-click handler
    const handleContextMenu = (e: React.MouseEvent) => {
        e.preventDefault();
        if (window.confirm('Are you sure you want to delete this recording? This action cannot be undone.')) {
            onDelete();
        }
    };
    return <Tooltip color="foreground" showArrow placement="right" delay={1000} size={'sm'} content={
        <div className="px-1 py-2 max-w-[300px]">
            {task.summary.length > 128 ? task.summary.substring(0, 128) + '...' : task.summary}
        </div>
    }>
        <div
            onClick={onClick}
            onContextMenu={handleContextMenu}
            className="p-3 mb-2 rounded-lg bg-default-100 hover:bg-default-200 transition-colors hover:cursor-pointer">
            <p className="text-sm font-semibold truncate w-full max-w-full flex items-center">
                {/* Show checkmark if finished processing */}
                {
                    task.state.total_actions === task.state.actions_done &&
                    <div>
                        <IoCheckmarkCircleOutline size={18} className="mr-1"/>
                    </div>
                }
                <span className="truncate">
                    {task.summary}
                </span>
            </p>
            {
                task.state.total_actions !== task.state.actions_done && <>
                    <Divider className="my-2"/>
                    <p className="text-xs flex justify-between opacity-50">
                <span className="italic">{task.state.action}
                    <span className="inline-flex -translate-x-1 -translate-y-0.5 h-2 w-2">
                        <Spinner className="scale-35" variant="dots"/>
                    </span>
                </span>
                        <span>{task.state.actions_done}/{task.state.total_actions}</span>
                    </p>
                    <Progress className="opacity-90 mt-1" color={'success'}
                              value={Math.round(task.state.actions_done / task.state.total_actions * 100)} size="sm"/>
                </>
            }
        </div>
    </Tooltip>;
});

export const MainWrapper = () => {
    const [search, setSearch] = useState('');
    const [selected, setSelected] = useState<string | null>(null);
    const [tasks, setTasks] = useState<{
        id: string;
        summary: string;
        state: ProcessingState;
    }[]>([]);
    const [convAnalysis, setConvAnalysis] = useState<RecordingAnalysis | undefined>(undefined);
    const [audioUrl, setAudioUrl] = useState<string | undefined>(undefined);
    
    // Memoize filteredTasks to avoid unnecessary re-renders
    const filteredTasks = useMemo(() =>
        tasks.filter(task =>
            task.summary.toLowerCase().includes(search.toLowerCase())
        ), [tasks, search]
    );
    
    useEffect(() => {
        if (typeof selected === 'string') {
            setConvAnalysis(undefined);
            setAudioUrl(undefined);
            fetchRecordingAnalysis(selected).then(result => {
                if (result.success) {
                    setConvAnalysis(result.data);
                    downloadConversationWav(selected).then(result => {
                        if (result.success && result.data) {
                            const url = URL.createObjectURL(result.data);
                            setAudioUrl(url);
                        } else {
                            console.error('Failed to download conversation WAV:', result.reason);
                        }
                    });
                }
            });
        }
    }, [selected]);
    
    useEffect(() => {
        const socket = io('http://localhost:9000');
        socket.on('status', async () => {
            const response = await listAudio();
            if (response.success && response.data) {
                setTasks(() => {
                    return (response.data as ProcessingState[]).map((task: ProcessingState) => ({
                        id: task.id,
                        summary: task.summary || (task.actions_done === task.total_actions ? 'Untitled Task' : 'Processing...'),
                        state: {
                            id: task.id,
                            summary: task.summary || 'Untitled Task',
                            action: task.action || 'Processing',
                            total_actions: task.total_actions || 1,
                            actions_done: task.actions_done || 0
                        }
                    }));
                });
            } else {
                console.error('Failed to fetch tasks:', response.reason);
            }
        });
        return () => {
            socket.disconnect();
        };
    }, []);
    
    return (
        <motion.div
            initial={{opacity: 0}}
            animate={{opacity: 1}}
            exit={{opacity: 0, scale: 1.1}}
            transition={{delay: 0, duration: 0.35, ease: 'easeInOut'}}
            className="bg-default-400 relative w-screen h-screen flex flex-col items-center justify-center overflow-hidden"
        >
            
            <AnimatedGridPattern
                numSquares={90}
                maxOpacity={0.9}
                duration={2}
                repeatDelay={0.2}
                speed={5000}
                opacity={0.8}
                className={'inset-x-0 inset-y-[-30%] h-[200%] -skew-y-8 overflow-hidden blur-2xl'}
            />
            <motion.div
                initial={{scale: 0.8, opacity: 0}}
                animate={{scale: 1, opacity: 1}}
                transition={{delay: 0.12, duration: 0.3, ease: 'easeInOut'}}
                className="bg-white border-1 border-default-200 rounded-2xl w-[80vw] max-w-[1200px] h-[80vh] max-h-[700px] drop-shadow-md drop-shadow-default-400 overflow-hidden flex"
            >
                {/* Side Panel for Managing In-Progress Tasks */}
                <div
                    className="w-[300px] h-full bg-[#66666605] backdrop-blur-sm border-r-1 pt-6 flex flex-col justify-between">
                    <div className="px-6">
                        <h1 className="text-2xl flex items-center mb-5">
                            <img className="w-8 h-8 inline mr-2 translate-y-0.5"
                                 src="/icon.png" alt="Speaklarity"/>
                            <span className="font-semibold opacity-90">
                                Speaklarity
                            </span>
                        </h1>
                        <Input
                            placeholder="Type here to search..."
                            startContent={<IoSearch opacity={0.5}/>} variant="flat"
                            className="hover:shadow-inner rounded-2xl text-[0x00000033]" isClearable size="sm"
                            radius="sm"
                            value={search}
                            onChange={e => setSearch(e.target.value)}
                        />
                        <p className="mt-3 opacity-60 text-sm flex items-center justify-between">
                            <span> {search.trim() ? 'Search results' : 'All analyses'} ({filteredTasks.length})</span>
                            {
                                selected !== null && <Link
                                    className="text-xs flex items-center text-blue-600 hover:cursor-pointer hover:underline"
                                    onPress={() => {
                                        setSelected(null);
                                    }}
                                >
                                <span className="sm font-semibold"><IoMdAddCircleOutline size={16}
                                                                                         className="inline mr-0.5"/>New Recording</span>
                                </Link>
                            }
                        </p>
                    </div>
                    <ScrollShadow className="flex-1 min-h-0 mt-2 px-4 mx-2">
                        {filteredTasks.map(task => (
                            <TaskItem key={task.id} task={task} onClick={() => {
                                setSelected(task.id);
                            }} onDelete={() => removeAudio(task.id)} />
                        ))}
                        <div className="h-6"></div>
                    </ScrollShadow>
                </div>
                {/* Right panel for nested routes */}
                <div className="flex-1 h-full overflow-auto">
                    {
                        selected === null && (
                            <NewRecordingPage/>
                        )
                    }
                    {
                        typeof selected === 'string' &&
                        <ConversationPage audioUrl={audioUrl} recAnalysis={convAnalysis}/>
                    }
                </div>
            </motion.div>
        </motion.div>
    );
};
