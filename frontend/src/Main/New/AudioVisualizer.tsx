import {useRef, useEffect} from 'react';

type AudioVisualizerProps = {
    width?: number;
    height?: number;
    backgroundColor?: string;
    waveformColor?: string;
    nonlinearExponent?: number;
};

export default function AudioVisualizer({
                                            width = 600,
                                            height = 200,
                                            backgroundColor = 'rgb(240,240,240)',
                                            waveformColor = 'rgb(30,30,30)',
                                            nonlinearExponent = 0.5,
                                        }: AudioVisualizerProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const audioCtxRef = useRef<AudioContext | undefined>(undefined);
    const analyserRef = useRef<AnalyserNode | undefined>(undefined);
    const dataArrRef = useRef<Uint8Array | undefined>(undefined);
    
    const updateIntervalMs = 16;
    const barWidth = 6;
    const barGap = 6;
    const histLen = Math.floor(width! / (barWidth + barGap));
    const historyRef = useRef<Float32Array>(new Float32Array(histLen));
    const writeIdxRef = useRef(0);
    
    const sampleAudioRMS = (): number => {
        if (!analyserRef.current || !dataArrRef.current) return 0;
        analyserRef.current.getByteTimeDomainData(dataArrRef.current);
        const arr = dataArrRef.current;
        let sum = 0;
        for (let i = 0; i < arr.length; i++) {
            sum += Math.abs((arr[i] - 128) / 128);
        }
        return (sum / arr.length) * (height / 2);
    };
    
    function drawPill(
        ctx: CanvasRenderingContext2D,
        x: number,
        y: number,
        w: number,
        h: number,
        r: number
    ) {
        r = Math.max(0, r); // Ensure radius is not negative
        ctx.beginPath();
        ctx.moveTo(x + r, y);
        ctx.lineTo(x + w - r, y);
        ctx.arcTo(x + w, y, x + w, y + r, r);
        ctx.lineTo(x + w, y + h - r);
        ctx.arcTo(x + w, y + h, x + w - r, y + h, r);
        ctx.lineTo(x + r, y + h);
        ctx.arcTo(x, y + h, x, y + h - r, r);
        ctx.lineTo(x, y + r);
        ctx.arcTo(x, y, x + r, y, r);
        ctx.closePath();
        ctx.fill();
    }
    
    useEffect(() => {
        let intervalId: number;
        let stream: MediaStream;
        
        (async () => {
            stream = await navigator.mediaDevices.getUserMedia({audio: true});
            const C = window.AudioContext || (window as any).webkitAudioContext;
            audioCtxRef.current = new C();
            analyserRef.current = audioCtxRef.current.createAnalyser();
            analyserRef.current.fftSize = 2048;
            dataArrRef.current = new Uint8Array(analyserRef.current.fftSize);
            
            const src = audioCtxRef.current.createMediaStreamSource(stream);
            src.connect(analyserRef.current);
            
            const ctx = canvasRef.current!.getContext('2d')!;
            const centerY = height / 2;
            const hist = historyRef.current;
            const radius = Math.max(0, barWidth / 2);
            
            intervalId = window.setInterval(() => {
                // write into ring buffer
                hist[writeIdxRef.current] = sampleAudioRMS();
                writeIdxRef.current = (writeIdxRef.current + 1) % histLen;
                
                // clear canvas
                ctx.fillStyle = backgroundColor!;
                ctx.fillRect(0, 0, width!, height);
                
                // draw visual
                ctx.fillStyle = waveformColor!;
                for (let i = 0; i < histLen; i++) {
                    const idx = (writeIdxRef.current + i) % histLen;
                    const scaled = Math.pow(hist[idx] / centerY, nonlinearExponent!) * centerY;
                    const barH = scaled * 2;
                    const x = i * (barWidth + barGap);
                    const y = centerY - scaled;
                    drawPill(ctx, x, y, barWidth, barH, radius);
                }
            }, updateIntervalMs);
        })();
        
        return () => {
            clearInterval(intervalId);
            audioCtxRef.current?.close();
            stream?.getTracks().forEach((t) => t.stop());
        };
    }, [width, height, backgroundColor, waveformColor, nonlinearExponent]);
    
    return (
        <div className="p-4">
            <canvas ref={canvasRef} width={width} height={height}/>
        </div>
    );
}
