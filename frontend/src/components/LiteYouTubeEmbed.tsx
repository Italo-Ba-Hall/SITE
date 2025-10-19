import React, { useEffect, useRef } from 'react';
import '@justinribeiro/lite-youtube';

interface LiteYouTubeEmbedProps {
  videoId: string;
  title?: string;
  autoload?: boolean;
  params?: string;
  posterQuality?: 'default' | 'mqdefault' | 'hqdefault' | 'sddefault' | 'maxresdefault';
  noCookie?: boolean;
}

/**
 * Wrapper React para o lite-youtube web component
 * Elimina warnings do console e melhora performance drasticamente
 */
const LiteYouTubeEmbed: React.FC<LiteYouTubeEmbedProps> = ({
  videoId,
  title = 'YouTube video',
  autoload = false,
  params = '',
  posterQuality = 'hqdefault',
  noCookie = false
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Garantir que o web component está registrado
    // O import já registra automaticamente
  }, []);

  return (
    <div 
      ref={containerRef} 
      style={{ width: '100%', height: '100%' }}
      dangerouslySetInnerHTML={{
        __html: `
          <lite-youtube
            videoid="${videoId}"
            ${title ? `videotitle="${title}"` : ''}
            ${autoload ? 'autoload' : ''}
            ${params ? `params="${params}"` : ''}
            ${posterQuality ? `posterquality="${posterQuality}"` : ''}
            ${noCookie ? 'nocookie' : ''}
            style="width: 100%; height: 100%; aspect-ratio: 16 / 9;"
          ></lite-youtube>
        `
      }}
    />
  );
};

export default LiteYouTubeEmbed;

