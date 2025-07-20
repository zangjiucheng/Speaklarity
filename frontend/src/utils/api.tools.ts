export const API_BASE_URL = 'http://100.66.178.24:9000';

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
