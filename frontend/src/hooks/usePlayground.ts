import { useState, useCallback } from 'react';
import { API_BASE_URL } from '../config/performance';

interface TranscriptSegment {
  text: string;
  start: number;
  duration: number;
  end: number;
}

interface TranscribeResponse {
  video_id: string;
  video_url: string;
  title?: string | null;
  transcript: string;
  language: string;
  duration?: number | null;
  segments: TranscriptSegment[];
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
  was_truncated: boolean;
}

interface UserData {
  name: string;
  email: string;
}

const usePlayground = () => {
  const [videoUrl, setVideoUrl] = useState<string>('');
  const [videoId, setVideoId] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<string | null>(null);
  const [segments, setSegments] = useState<TranscriptSegment[]>([]);
  const [summary, setSummary] = useState<SummarizeResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<UserData | null>(null);
  const [activityId, setActivityId] = useState<number | null>(null);
  const [showRegistrationModal, setShowRegistrationModal] = useState<boolean>(false);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const registerUser = useCallback((userData: UserData) => {
    setUser(userData);
    setShowRegistrationModal(false);
  }, []);

  const registerActivity = useCallback(
    async (videoUrl: string, videoId: string, actionType: 'transcribe' | 'summarize') => {
      if (!user) return null;

      try {
        const response = await fetch(`${API_BASE_URL}/playground/register-lead`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_name: user.name,
            user_email: user.email,
            video_url: videoUrl,
            video_id: videoId,
            action_type: actionType,
          }),
        });

        if (!response.ok) {
          // Silenciar erro de registro (não crítico para UX)
          return null;
        }

        const data = await response.json();
        return data.activity_id;
      } catch (err) {
        // Silenciar erro de registro (não crítico para UX)
        return null;
      }
    },
    [user]
  );

  const updateExport = useCallback(
    async (format: 'txt' | 'pdf') => {
      if (!activityId) return;

      try {
        await fetch(`${API_BASE_URL}/playground/update-export`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            activity_id: activityId,
            export_format: format,
          }),
        });
      } catch (err) {
        // Silenciar erro de export tracking (não crítico para UX)
      }
    },
    [activityId]
  );

  const handleUrlSubmit = useCallback(
    async (url: string) => {
      // Verificar se usuário está registrado
      if (!user) {
        setShowRegistrationModal(true);
        return;
      }

      setLoading(true);
      setError(null);
      setSummary(null);
      setSegments([]);

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
        setSegments(data.segments || []);

        // Registrar atividade
        const actId = await registerActivity(url, data.video_id, 'transcribe');
        if (actId) {
          setActivityId(actId);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro desconhecido');
        setVideoId(null);
        setTranscript(null);
        setSegments([]);
      } finally {
        setLoading(false);
      }
    },
    [user, registerActivity]
  );

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

        // Registrar atividade de resumo (se não registrou transcrição)
        if (!activityId && videoId && videoUrl && user) {
          const actId = await registerActivity(videoUrl, videoId, 'summarize');
          if (actId) {
            setActivityId(actId);
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro desconhecido');
      } finally {
        setLoading(false);
      }
    },
    [transcript, activityId, videoId, videoUrl, user, registerActivity]
  );

  const resetSummary = useCallback(() => {
    setSummary(null);
  }, []);

  return {
    videoUrl,
    videoId,
    transcript,
    segments,
    summary,
    loading,
    error,
    user,
    showRegistrationModal,
    activityId,
    handleUrlSubmit,
    handleSummarize,
    clearError,
    resetSummary,
    registerUser,
    updateExport,
    setShowRegistrationModal,
  };
};

export default usePlayground;
export type { UserData };
