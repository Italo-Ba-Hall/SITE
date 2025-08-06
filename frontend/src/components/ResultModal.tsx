import React, { useState, useEffect, useCallback } from 'react';
import { useContent } from '../hooks/useApi';

interface ContactForm {
  nome: string;
  email: string;
  mensagem: string;
}

interface ResultModalProps {
  isVisible?: boolean;
  suggestionId?: string | null;
  onClose?: () => void;
}

const ResultModal: React.FC<ResultModalProps> = ({
  isVisible = false,
  suggestionId = null,
  onClose
}) => {
  const [modalVisible, setModalVisible] = useState(isVisible);
  const [showContactForm, setShowContactForm] = useState(false);
  const [contactForm, setContactForm] = useState<ContactForm>({
    nome: '',
    email: '',
    mensagem: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Hook para buscar conteúdo da API
  const { content, loading: contentLoading, error: contentError } = useContent(suggestionId);

  useEffect(() => {
    setModalVisible(isVisible);
    if (isVisible) {
      setShowContactForm(false);
      setSubmitSuccess(false);
      setSubmitError(null);
    }
  }, [isVisible]);

  const handleClose = useCallback(() => {
    setModalVisible(false);
    if (onClose) {
      onClose();
    }
  }, [onClose]);

  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      handleClose();
    }
  };

  const handleContactSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const response = await fetch('http://localhost:8000/contact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...contactForm,
          suggestion_id: suggestionId
        }),
      });

      if (!response.ok) {
        throw new Error('Erro ao enviar formulário');
      }

      setSubmitSuccess(true);
      setContactForm({ nome: '', email: '', mensagem: '' });

      // Fechar modal após 3 segundos
      setTimeout(() => {
        handleClose();
      }, 3000);
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : 'Erro desconhecido');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setContactForm(prev => ({
      ...prev,
      [name]: value
    }));
  };

  if (!modalVisible) return null;

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
      onClick={handleOverlayClick}
    >
      <div className="bg-gray-900 border border-gray-700 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-700">
          <h2 className="text-white text-xl font-semibold">
            {contentLoading ? 'Carregando...' : (content?.title || 'Detalhes')}
          </h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-white text-2xl font-bold"
            aria-label="Fechar modal"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {contentLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-400 mx-auto"></div>
              <p className="text-gray-400 mt-4">Carregando conteúdo...</p>
            </div>
          ) : contentError ? (
            <div className="text-center py-8">
              <p className="text-red-400">Erro ao carregar conteúdo: {contentError || 'Erro desconhecido'}</p>
            </div>
          ) : content ? (
            <div className="space-y-6">
              {/* Content Details */}
              <div className="prose prose-invert max-w-none">
                <p className="text-gray-300 leading-relaxed">{content.content || ''}</p>

                {/* Details */}
                {content.details && Object.keys(content.details).length > 0 && (
                  <div className="mt-6 p-4 bg-gray-800 rounded-lg">
                    <h3 className="text-green-400 font-semibold mb-3">Detalhes Técnicos</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {Object.entries(content.details).map(([key, value]) => (
                        <div key={key}>
                          <span className="text-gray-400 text-sm capitalize">{key}:</span>
                          <div className="text-white">
                            {Array.isArray(value) ? value.join(', ') : String(value || '')}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Contact Form Button */}
              {!showContactForm && !submitSuccess && (
                <div className="text-center">
                  <button
                    onClick={() => setShowContactForm(true)}
                    className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-400"
                  >
                    Quero saber mais sobre esta solução
                  </button>
                </div>
              )}

              {/* Contact Form */}
              {showContactForm && !submitSuccess && (
                <form onSubmit={handleContactSubmit} className="space-y-4">
                  <h3 className="text-white font-semibold">Entre em contato</h3>

                  <div>
                    <label htmlFor="nome" className="block text-sm font-medium text-gray-300 mb-1">
                      Nome *
                    </label>
                    <input
                      type="text"
                      id="nome"
                      name="nome"
                      value={contactForm.nome}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-green-400"
                    />
                  </div>

                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-1">
                      Email *
                    </label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={contactForm.email}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-green-400"
                    />
                  </div>

                  <div>
                    <label htmlFor="mensagem" className="block text-sm font-medium text-gray-300 mb-1">
                      Mensagem
                    </label>
                    <textarea
                      id="mensagem"
                      name="mensagem"
                      value={contactForm.mensagem}
                      onChange={handleInputChange}
                      rows={4}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-green-400"
                      placeholder="Conte-nos mais sobre seu projeto..."
                    />
                  </div>

                  {submitError && (
                    <div className="text-red-400 text-sm">{submitError || 'Erro ao enviar formulário'}</div>
                  )}

                  <div className="flex space-x-3">
                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                    >
                      {isSubmitting ? 'Enviando...' : 'Enviar'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowContactForm(false)}
                      className="px-4 py-2 bg-gray-700 text-white rounded-md hover:bg-gray-600 transition-colors duration-200"
                    >
                      Cancelar
                    </button>
                  </div>
                </form>
              )}

              {/* Success Message */}
              {submitSuccess && (
                <div className="text-center py-6">
                  <div className="text-green-400 text-4xl mb-4">✓</div>
                  <h3 className="text-white font-semibold mb-2">Mensagem enviada!</h3>
                  <p className="text-gray-400">Entraremos em contato em breve.</p>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-400">Nenhum conteúdo disponível.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResultModal; 