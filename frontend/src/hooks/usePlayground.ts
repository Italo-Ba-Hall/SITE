import { useState, useCallback } from 'react';
import { API_BASE_URL } from '../config/performance';

interface TranscribeResponse {
  video_id: string;
  video_url: string;
  title?: string | null;
  transcript: string;
  language: string;
  duration?: number | null;
}

interface SummarySection {
  title: string;
  content: string;
}

interface SummarizeResponse {
  summary: string;
  key_points: string[];
  keywords_found?: string[] | null;
  sections?: SummarySection[] | null;
  confidence: number;
}

const usePlayground = () => {
  const [videoUrl, setVideoUrl] = useState<string>('');
  const [videoId, setVideoId] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<string | null>(null);
  const [summary, setSummary] = useState<SummarizeResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const handleUrlSubmit = useCallback(async (url: string) => {
    setLoading(true);
    setError(null);
    setSummary(null);

    try {
      const response = await fetch(`${API_BASE_URL}/playground/transcribe`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ video_url: url }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro ao processar transcrição');
      }

      const data: TranscribeResponse = await response.json();

      setVideoUrl(url);
      setVideoId(data.video_id);
      setTranscript(data.transcript);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
      setVideoId(null);
      setTranscript(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleSummarize = useCallback(
    async (context?: string, keywords?: string[]) => {
      if (!transcript) {
        setError('Nenhuma transcrição disponível para sumarizar');
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const response = await fetch(`${API_BASE_URL}/playground/summarize`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            transcript,
            context: context || null,
            keywords: keywords || null,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Erro ao processar sumarização');
        }

        const data: SummarizeResponse = await response.json();

        setSummary(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro desconhecido');
      } finally {
        setLoading(false);
      }
    },
    [transcript]
  );

  return {
    videoUrl,
    videoId,
    transcript,
    summary,
    loading,
    error,
    handleUrlSubmit,
    handleSummarize,
    clearError,
  };
};

export default usePlayground;
