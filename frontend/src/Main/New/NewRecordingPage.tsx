import React, {useRef, useState} from 'react';
import AudioVisualizer from './AudioVisualizer.tsx';
import {RecordingButton} from '../RecordButton.tsx';
import {toast} from 'react-hot-toast';

export const NewRecordingPage: React.FC = () => {
    const [isRecording, setIsRecording] = useState(false);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);
    
    const handleValueChange = async (recording: boolean) => {
        if (recording) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({audio: true});
                const mediaRecorder = new MediaRecorder(stream);
                audioChunksRef.current = [];
                mediaRecorder.ondataavailable = (event: BlobEvent) => {
                    if (event.data.size > 0) {
                        audioChunksRef.current.push(event.data);
                    }
                };
                mediaRecorder.onstop = async () => {
                    // Convert recorded chunks to a proper WAV file
                    const rawBlob = new Blob(audioChunksRef.current, {type: mediaRecorder.mimeType});
                    const wavBlob = await blobToWav(rawBlob);
                    // Upload to server instead of saving as file
                    const arrayBuffer = await wavBlob.arrayBuffer();
                    const {uploadConversation} = await import('../../utils/api.tools');
                    const result = await uploadConversation(arrayBuffer, 'recording.wav');
                    if (result.success) {
                        toast.success('Upload successful!');
                    } else {
                        toast.error('Upload failed: ' + result.reason);
                    }
                };
                mediaRecorderRef.current = mediaRecorder;
                mediaRecorder.start();
                setIsRecording(true);
            } catch (err) {
                toast.error('Could not start recording: ' + err);
            }
        } else {
            if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
                mediaRecorderRef.current.stop();
                setIsRecording(false);
            }
        }
    };
    
    function writeString(view: DataView, offset: number, str: string) {
        for (let i = 0; i < str.length; i++) {
            view.setUint8(offset + i, str.charCodeAt(i));
        }
    }
    
    async function blobToWav(blob: Blob): Promise<Blob> {
        const arrayBuffer = await blob.arrayBuffer();
        const audioCtx = new AudioContext();
        const buffer = await audioCtx.decodeAudioData(arrayBuffer);
        const numOfChan = buffer.numberOfChannels;
        const sampleRate = buffer.sampleRate;
        const bitDepth = 16;
        const bytesPerSample = bitDepth / 8;
        const blockAlign = numOfChan * bytesPerSample;
        const dataSize = buffer.length * blockAlign;
        const wavBuffer = new ArrayBuffer(44 + dataSize);
        const view = new DataView(wavBuffer);
        
        // RIFF header
        writeString(view, 0, 'RIFF');
        view.setUint32(4, 36 + dataSize, true);
        writeString(view, 8, 'WAVE');
        
        // fmt chunk
        writeString(view, 12, 'fmt ');
        view.setUint32(16, 16, true); // PCM chunk size
        view.setUint16(20, 1, true);  // audio format (1 = PCM)
        view.setUint16(22, numOfChan, true);
        view.setUint32(24, sampleRate, true);
        view.setUint32(28, sampleRate * blockAlign, true);
        view.setUint16(32, blockAlign, true);
        view.setUint16(34, bitDepth, true);
        
        // data chunk
        writeString(view, 36, 'data');
        view.setUint32(40, dataSize, true);
        
        // write PCM samples
        let offset = 44;
        for (let i = 0; i < buffer.length; i++) {
            for (let ch = 0; ch < numOfChan; ch++) {
                const sample = buffer.getChannelData(ch)[i];
                const s = Math.max(-1, Math.min(1, sample));
                view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
                offset += bytesPerSample;
            }
        }
        
        return new Blob([view], {type: 'audio/wav'});
    }
    
    return (
        <div className="flex flex-col h-full">
            <div className="pt-8 pb-4 px-6 text-2xl font-bold text-center">New Recording</div>
            <div className="flex-1 flex items-center justify-center">
                <AudioVisualizer backgroundColor="white" waveformColor={isRecording ? '#f31260' : '#a3a3a3'}/>
            </div>
            <div className="pb-2 flex justify-center">
                {isRecording && (
                    <span className="text-red-600 text-sm">Recording...</span>
                )}
                {!isRecording && (
                    <span className="text-gray-500 text-sm">Press record to start</span>
                )}
            </div>
            <div className="pb-8 flex justify-center">
                <RecordingButton value={isRecording} onValueChange={handleValueChange}/>
            </div>
        </div>
    );
};
