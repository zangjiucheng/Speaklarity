import React, {useState, useMemo} from 'react';
import {motion} from 'framer-motion';
import {AnimatedGridPattern} from '../components/magicui/animated-grid-pattern.tsx';
import {Divider, Input, Link, Progress, ScrollShadow, Spinner} from '@heroui/react';
import {IoSearch} from 'react-icons/io5';
import type {ProcessingState} from '../utils/api.types.ts';
import {IoMdAddCircleOutline} from 'react-icons/io';
import {NewRecordingPage} from './New/NewRecordingPage.tsx';

const TaskItem = React.memo(function TaskItem({task}: { task: { id: number, title: string, state: ProcessingState } }) {
    return (
        <div className="p-3 mb-2 rounded-lg bg-default-100 hover:bg-default-200 transition-colors">
            <p className="text-sm font-semibold">{task.title}</p>
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
        </div>
    );
});

// Move tasks outside the component to keep reference stable
const tasks: {
    id: number,
    title: string,
    state: ProcessingState
}[] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(task => {
    return {
        id: task,
        title: `Analysis Task ${task}`,
        state: {
            action: 'Analyzing',
            total_actions: 10,
            actions_done: Math.floor(Math.random() * 5 + 3)
        }
    };
});

export const MainWrapper = () => {
    const [search, setSearch] = useState('');
    const [selected, setSelected] = useState<number | 'new'>('new');
    
    // Memoize filteredTasks to avoid unnecessary re-renders
    const filteredTasks = useMemo(() =>
        tasks.filter(task =>
            task.title.toLowerCase().includes(search.toLowerCase())
        ), [tasks, search]
    );
    
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
                                selected !== 'new' && <Link
                                    className="text-xs flex items-center text-blue-600 hover:cursor-pointer hover:underline"
                                    onPress={() => {
                                        setSelected('new');
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
                            <TaskItem key={task.id} task={task}/>
                        ))}
                        <div className="h-6"></div>
                    </ScrollShadow>
                </div>
                {/* Right panel for nested routes */}
                <div className="flex-1 h-full overflow-auto">
                    {
                        selected === 'new' && (
                            <NewRecordingPage/>
                        )
                    }
                </div>
            </motion.div>
        </motion.div>
    );
};
