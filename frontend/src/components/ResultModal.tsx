import React, { useState } from 'react';

interface ResultModalProps {
  isVisible?: boolean;
  title?: string;
  content?: string;
  onClose?: () => void;
}

const ResultModal: React.FC<ResultModalProps> = ({
  isVisible = false,
  title = '',
  content = '',
  onClose
}) => {
  const [modalVisible, setModalVisible] = useState(isVisible);

  const handleClose = () => {
    setModalVisible(false);
    if (onClose) {
      onClose();
    }
  };

  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      handleClose();
    }
  };

  return (
    <div 
      id="resultModal" 
      className={`result-modal-overlay ${modalVisible ? 'visible' : ''}`}
      onClick={handleOverlayClick}
    >
      <div className="result-modal-content">
        <button 
          className="close-button"
          onClick={handleClose}
          aria-label="Fechar modal"
        >
          ×
        </button>
        {title && <div className="result-title">{title}</div>}
        {content && (
          <div 
            className="result-text"
            dangerouslySetInnerHTML={{ __html: content }}
          />
        )}
      </div>
    </div>
  );
};

export default ResultModal; 