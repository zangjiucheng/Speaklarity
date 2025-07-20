import React from 'react';
import {motion} from 'framer-motion';

export const RecordingButton = ({value, onValueChange}: { value: boolean, onValueChange: (v: boolean) => void }) => {
    const [hovered, setHovered] = React.useState(false);
    return (
        <motion.button
            className={`hover:cursor-pointer w-16 h-16 rounded-full flex items-center justify-center shadow-lg relative transition-colors duration-200 ${value ? 'bg-red-500' : 'bg-gray-300'}`}
            initial={false}
            animate={{
                scale: value
                    ? [1, 1.05, 1]
                    : hovered
                        ? 1.08
                        : 1,
                boxShadow: value
                    ? [
                        '0 0 0 0 rgba(239,68,68,0.5)',
                        '0 0 0 8px rgba(239,68,68,0)',
                        '0 0 0 0 rgba(239,68,68,0.5)'
                    ]
                    : '0 0 0 0 rgba(0,0,0,0.1)'
            }}
            transition={{
                duration: value ? 1.1 : 0.18,
                repeat: value ? Infinity : 0,
                ease: 'easeInOut',
            }}
            aria-label={value ? 'Recording' : 'Not recording'}
            type="button"
            onClick={() => onValueChange(!value)}
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => setHovered(false)}
        >
            <span
                className={`block w-6 h-6 rounded-full transition-colors duration-200 ${value ? 'bg-white' : 'bg-gray-400'}`}/>
        </motion.button>
    );
};
