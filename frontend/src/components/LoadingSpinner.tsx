import React from 'react';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  color?: 'cyan' | 'white' | 'blue';
  text?: string;
  className?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'medium',
  color = 'cyan',
  text,
  className = ''
}) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12'
  };

  const colorClasses = {
    cyan: 'border-cyan-400',
    white: 'border-white',
    blue: 'border-blue-400'
  };

  return (
    <div className={`flex flex-col items-center justify-center ${className}`}>
      <div
        className={`animate-spin rounded-full border-2 border-t-transparent ${sizeClasses[size]} ${colorClasses[color]}`}
      />
      {text && (
        <p className={`mt-2 text-sm ${color === 'cyan' ? 'text-cyan-400' : color === 'white' ? 'text-white' : 'text-blue-400'}`}>
          {text}
        </p>
      )}
    </div>
  );
};

export default LoadingSpinner;
