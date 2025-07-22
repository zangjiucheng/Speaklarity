import type {ProcessingState, RecordingAnalysis} from './api.types.ts';

// export const API_BASE_URL = 'http://100.66.178.24:9000';
export const API_BASE_URL = 'http://localhost:9000';

export async function callAPI(
    endpoint: string,
    type: 'GET' | 'POST',
    payload?: Record<string, any>,
): Promise<{ success: boolean; reason?: string; data?: any }> {
    const url = `${API_BASE_URL}${endpoint}`;
    const options: RequestInit = {
        method: type,
        headers: {
            'Content-Type': 'application/json',
        },
    };
    if (type === 'POST' && payload) {
        options.body = JSON.stringify(payload);
    }
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            const errorText = await response.text();
            return {success: false, reason: `API error: ${response.status} ${response.statusText} - ${errorText}`};
        }
        const data = await response.json();
        return {success: true, data};
    } catch (error: any) {
        return {success: false, reason: error?.message || 'Unknown error'};
    }
}

export async function downloadConversationWav(convId: string): Promise<{
    success: boolean;
    reason?: string;
    data?: Blob
}> {
    const url = `${API_BASE_URL}/download-conversation/${convId}`;
    try {
        const response = await fetch(url);
        if (!response.ok) {
            const errorText = await response.text();
            return {success: false, reason: `API error: ${response.status} ${response.statusText} - ${errorText}`};
        }
        const blob = await response.blob();
        if (blob.type !== 'audio/wav' && blob.type !== 'audio/x-wav') {
            return {success: false, reason: `Unexpected MIME type: ${blob.type}`};
        }
        return {success: true, data: blob};
    } catch (error: any) {
        return {success: false, reason: error?.message || 'Unknown error'};
    }
}

// Import the RecordingAnalysis type if it's defined in another file
// import type { RecordingAnalysis } from './recording.types.ts';

export async function fetchRecordingAnalysis(
    conv_id: string
): Promise<{ success: boolean; data?: RecordingAnalysis; reason?: string }> {
    const endpoint = `/conv/${conv_id}`;
    const response = await callAPI(endpoint, 'GET');
    
    if (!response.success) {
        return {success: false, reason: response.reason};
    }
    
    try {
        const data = response.data as RecordingAnalysis;
        return {success: true, data};
    } catch (e: any) {
        return {
            success: false,
            reason: 'Failed to parse response as RecordingAnalysis',
        };
    }
}


export async function uploadConversation(
    rawData: ArrayBuffer,
    fileName: string = 'conversation.wav'
): Promise<{ success: boolean; reason?: string; data?: any }> {
    const url = `${API_BASE_URL}/upload-conversation`;
    
    // Create a Blob from the raw WAV data
    const fileBlob = new Blob([rawData], {type: 'audio/wav'});
    
    // Build form-data
    const formData = new FormData();
    formData.append('file', fileBlob, fileName);
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
            // Note: Do NOT set Content-Type header; browser will set multipart/form-data boundary automatically
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            return {
                success: false,
                reason: `API error: ${response.status} ${response.statusText} - ${errorText}`,
            };
        }
        
        const data = await response.json();
        return {success: true, data};
    } catch (error: any) {
        return {success: false, reason: error?.message || 'Unknown error'};
    }
}


export async function listAudio(): Promise<{ success: boolean; reason?: string; data?: ProcessingState[] }> {
    const url = `${API_BASE_URL}/list-audio`;
    
    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            },
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            return {
                success: false,
                reason: `API error: ${response.status} ${response.statusText} - ${errorText}`,
            };
        }
        
        const data: ProcessingState[] = await response.json();
        return {success: true, data};
    } catch (error: any) {
        return {
            success: false,
            reason: error?.message || 'Unknown error',
        };
    }
}

export async function downloadNativeReference(convId: string, sentenceId: number): Promise<{
    success: boolean;
    reason?: string;
    data?: Blob;
}> {
    const url = `${API_BASE_URL}/native-reference/${convId}/${sentenceId}`;
    try {
        const response = await fetch(url);
        if (!response.ok) {
            const errorText = await response.text();
            return {success: false, reason: `API error: ${response.status} ${response.statusText} - ${errorText}`};
        }
        const blob = await response.blob();
        if (blob.type !== 'audio/wav' && blob.type !== 'audio/x-wav') {
            return {success: false, reason: `Unexpected MIME type: ${blob.type}`};
        }
        return {success: true, data: blob};
    } catch (error: any) {
        return {success: false, reason: error?.message || 'Unknown error'};
    }
}
