export type ProcessingState = {
    id: string;
    summary: string;
    action: string;
    total_actions: number;
    actions_done: number;
}

export interface RecordingAnalysis {
    action: string;
    conversation_id: string;
    filename: string;
    sentences: {
        id: number;
        sentence_text: string;
        sentence_score: number;
        audio_timeline: {
            start: number;
            end: number;
        };
        grammar_analysis: {
            corrected_text: string;
            is_grammatically_correct: boolean;
            overall_feedback: string;
        };
        word_scores: {
            word: string;
            score: number;
        }[];
    }[];
    sha256: string;
    uploaded_at: string; // ISO 8601 timestamp
}
