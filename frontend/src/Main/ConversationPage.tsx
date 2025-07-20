import {Divider, Spinner} from '@heroui/react';
import type {RecordingAnalysis} from '../utils/api.types.ts';
import {useWavesurfer} from '@wavesurfer/react';
import {useEffect, useRef, useState} from 'react';
import {TiStar} from 'react-icons/ti';

export const ConversationPage = (
    props: {
        recAnalysis?: RecordingAnalysis;
        audioUrl?: string;
    }
) => {
    const containerRef = useRef(null);
    const [currentTimeSecond, setCurrentTimeSecond] = useState(0);
    
    const currentTimeMS = Math.floor(currentTimeSecond * 1000 % 1000);
    const currentTimeMinute = Math.floor(currentTimeSecond / 60);
    const currentTimeSecondRemainder = Math.floor(currentTimeSecond % 60);
    const currentTimeString = `${currentTimeMinute.toString().padStart(2, '0')}:${currentTimeSecondRemainder.toString().padStart(2, '0')}.${currentTimeMS.toString().padStart(3, '0')}`;
    
    const {wavesurfer, isReady, isPlaying, currentTime} = useWavesurfer({
        container: containerRef,
        url: props.audioUrl,
        progressColor: '#3c7ecc',
        waveColor: '#b4c2d1',
        height: 100,
        barWidth: 4,
        barGap: 4,
        barRadius: 4,
        autoScroll: true,
    });
    
    
    useEffect(() => {
        if (wavesurfer) {
            wavesurfer.on('dblclick', () => {
                if (!isPlaying) {
                    wavesurfer.play();
                }
            });
            wavesurfer.on('click', () => {
                wavesurfer.pause();
            });
            wavesurfer.on('timeupdate', (time) => {
                setCurrentTimeSecond(time);
            });
        }
        
        const spacePausePlay = (evt: KeyboardEvent) => {
            if (evt.key === ' ')
                if (wavesurfer) {
                    wavesurfer.playPause();
                }
        };
        window.addEventListener('keydown', spacePausePlay);
        return () => {
            if (wavesurfer) {
                wavesurfer.unAll();
                wavesurfer.destroy();
            }
            window.removeEventListener('keydown', spacePausePlay);
        };
    }, [wavesurfer]);
    
    const [sentenceScore, setSentenceScore] = useState<number | null>(null);
    
    useEffect(() => {
        if (!props.recAnalysis) {
            setSentenceScore(null);
            return;
        }
        // Find all sentences that match the current time (overlap)
        const overlapping = props.recAnalysis.sentences.filter(
            (sentence) =>
                sentence.audio_timeline.start <= currentTimeSecond &&
                sentence.audio_timeline.end >= currentTimeSecond
        );
        // Pick the one with the latest start time if overlaps
        const currentSentence = overlapping.length > 0
            ? overlapping.reduce((latest, s) => s.audio_timeline.start > latest.audio_timeline.start ? s : latest, overlapping[0])
            : null;
        if (currentSentence) {
            setSentenceScore(currentSentence.sentence_score);
        } else {
            setSentenceScore(null);
        }
    }, [currentTimeSecond, props.recAnalysis]);
    
    useEffect(() => {
        if (!props.recAnalysis) return;
        const handleArrow = (evt: KeyboardEvent) => {
            if (!props.recAnalysis) return;
            if (evt.key === 'ArrowLeft' || evt.key === 'ArrowRight') {
                // Sort sentences by start time
                const sentences = [...props.recAnalysis.sentences].sort((a, b) => a.audio_timeline.start - b.audio_timeline.start);
                // Find all overlapping at current time
                const overlapping = sentences.filter(s =>
                    s.audio_timeline.start <= currentTimeSecond &&
                    s.audio_timeline.end >= currentTimeSecond
                );
                // Pick the one with the latest start time
                const current = overlapping.length > 0
                    ? overlapping.reduce((latest, s) => s.audio_timeline.start > latest.audio_timeline.start ? s : latest, overlapping[0])
                    : null;
                // Find index by start time
                const idx = current ? sentences.findIndex(s => s === current) : -1;
                let newIdx = idx;
                if (evt.key === 'ArrowLeft') {
                    newIdx = Math.max(0, idx === -1 ? 0 : idx - 1);
                } else if (evt.key === 'ArrowRight') {
                    newIdx = Math.min(sentences.length - 1, idx === -1 ? 0 : idx + 1);
                }
                if (newIdx !== idx && sentences[newIdx]) {
                    setCurrentTimeSecond(sentences[newIdx].audio_timeline.start);
                    if (wavesurfer) {
                        wavesurfer.setTime(sentences[newIdx].audio_timeline.start);
                    }
                }
            }
        };
        window.addEventListener('keydown', handleArrow);
        return () => window.removeEventListener('keydown', handleArrow);
    }, [currentTimeSecond, props.recAnalysis, wavesurfer]);
    
    return (
        <div className="flex flex-col h-full">
            <h1 className="text-2xl font-bold p-6">Conversation Analysis</h1>
            <div className="flex-1 flex flex-col">
                {
                    !props.recAnalysis ? (
                        <div className="flex items-center justify-center flex-1">
                            <Spinner color="primary" size="lg" label="Fetching analysis..." labelColor="primary"/>
                        </div>
                    ) : (
                        <div className="flex flex-col h-full w-full">
                            <div className="shrink-0 px-8 py-4">
                                <div className={'border px-3 py-1 rounded-xl'} ref={containerRef}/>
                            </div>
                            <div className="px-8 pb-1">
                                <p>
                                    <span className="font-semibold">Current Time:</span> {currentTimeString}
                                    {sentenceScore !== null && <>
                                        <span className="ml-4 font-semibold">Score:</span>
                                        <span
                                            className="inline-flex items-center ml-1">{(sentenceScore * 10).toFixed(1)}
                                            <span className="ml-1"></span>
                                            {
                                                Array(Math.ceil(sentenceScore * 5)).fill(0).map((_, idx) => (
                                                    <TiStar key={idx} size={12} className="scale-110 text-yellow-500"/>
                                                ))
                                            }
                                        </span>
                                    </>}
                                </p>
                            </div>
                            <div className="flex-1 overflow-auto px-8 pb-8 pt-4">
                                <div className="w-full h-full border rounded-xl p-6">
                                    {
                                        props.recAnalysis && props.recAnalysis.sentences.map((sentence) => {
                                            const isCurrent = sentence.audio_timeline.start <= currentTimeSecond && sentence.audio_timeline.end >= currentTimeSecond;
                                            return <span
                                                onContextMenu={e => e.preventDefault()}
                                                className={
                                                    [
                                                        'cursor-pointer transition-colors duration-200 mr-1.5',
                                                        isCurrent
                                                            ? (isPlaying ? 'bg-blue-400/30 bg-opacity-30' : 'bg-blue-400/30 bg-opacity-10')
                                                            : 'bg-transparent hover:bg-cyan-400/50',
                                                        'border-b-2',
                                                        sentence.sentence_score > 0.5
                                                            ? 'border-b-green-600'
                                                            : sentence.sentence_score > 0.25
                                                                ? 'border-b-transparent'
                                                                : sentence.sentence_score < 0.2
                                                                    ? 'border-b-red-500'
                                                                    : 'border-b-amber-400',
                                                    ].filter(Boolean).join(' ')
                                                }
                                                onMouseDown={(evt) => {
                                                    if (evt.button === 0) {
                                                        wavesurfer?.setTime(sentence.audio_timeline.start);
                                                    }
                                                }}
                                            >
                                                {sentence.sentence_text}
                                            </span>;
                                        })
                                    }
                                </div>
                            </div>
                        </div>
                    )
                }
            </div>
        </div>
    );
};
