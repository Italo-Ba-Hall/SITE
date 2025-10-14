import React from 'react';
import YouTube, { YouTubeProps } from 'react-youtube';
import './YouTubePlayer.css';

interface YouTubePlayerProps {
  videoId: string;
}

const YouTubePlayer: React.FC<YouTubePlayerProps> = ({ videoId }) => {
  const opts: YouTubeProps['opts'] = {
    height: '100%',
    width: '100%',
    playerVars: {
      autoplay: 0,
      modestbranding: 1,
      rel: 0,
    },
  };

  return (
    <div className="youtube-player-container">
      <div className="youtube-player-wrapper">
        <YouTube videoId={videoId} opts={opts} className="youtube-player" />
      </div>
    </div>
  );
};

export default YouTubePlayer;
