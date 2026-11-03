import React, { useState, useEffect, useRef } from 'react';
import Sidebar from '../components/Sidebar';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../api/client';

export default function Chat({ onNavigate }) {
  const { user } = useAuth();
  const { t } = useLanguage();

  const [conversations, setConversations] = useState([]);
  const [activeConvId, setActiveConvId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loadingReply, setLoadingReply] = useState(false);
  const [isListening, setIsListening] = useState(false);

  // Rename & Delete modal states
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [deleteConfirmId, setDeleteConfirmId] = useState(null);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const res = await api.getConversations();
      const convList = res.conversations || [];
      setConversations(convList);

      if (convList.length > 0) {
        const firstId = convList[0].id;
        setActiveConvId(firstId);
        loadMessages(firstId);
      } else {
        handleNewChat();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const loadMessages = async (convId) => {
    try {
      const res = await api.getMessages(convId);
      setMessages(res.messages || []);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loadingReply]);

  const handleNewChat = async () => {
    try {
      const res = await api.createConversation('New Chat');
      const newConv = { id: res.id, title: 'New Chat', created_at: new Date().toISOString() };
      setConversations((prev) => [newConv, ...prev]);
      setActiveConvId(res.id);
      setMessages([]);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSelectConv = (convId) => {
    setActiveConvId(convId);
    loadMessages(convId);
  };

  const handleSendMessage = async (e) => {
    if (e) e.preventDefault();
    const cleanMsg = inputMessage.trim();
    if (!cleanMsg || loadingReply || !activeConvId) return;

    const userMsgObj = {
      id: Date.now(),
      role: 'user',
      content: cleanMsg,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsgObj]);
    setInputMessage('');
    setLoadingReply(true);

    try {
      const res = await api.sendMessage(activeConvId, cleanMsg);
      const botMsgObj = {
        id: Date.now() + 1,
        role: 'assistant',
        content: res.reply,
        emotion: res.emotion,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, botMsgObj]);

      // If auto-generated title was returned, update conversations list
      if (res.new_title) {
        setConversations((prev) =>
          prev.map((c) => (c.id === activeConvId ? { ...c, title: res.new_title } : c))
        );
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: "I'm right here with you. Take a slow, calm breath.",
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoadingReply(false);
    }
  };

  const handleSaveTitle = async (convId) => {
    if (!editTitle.trim()) {
      setEditingId(null);
      return;
    }
    try {
      await api.updateConversationTitle(convId, editTitle.trim());
      setConversations((prev) =>
        prev.map((c) => (c.id === convId ? { ...c, title: editTitle.trim() } : c))
      );
    } catch (e) {
      console.error(e);
    }
    setEditingId(null);
  };

  const handleDeleteConversation = async (convId) => {
    try {
      await api.deleteConversation(convId);
      const updated = conversations.filter((c) => c.id !== convId);
      setConversations(updated);
      setDeleteConfirmId(null);

      if (activeConvId === convId) {
        if (updated.length > 0) {
          setActiveConvId(updated[0].id);
          loadMessages(updated[0].id);
        } else {
          handleNewChat();
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  const speakText = (text) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  };

  const toggleVoiceRecording = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech recognition is not supported in this browser.');
      return;
    }

    if (isListening) {
      setIsListening(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInputMessage((prev) => (prev ? prev + ' ' + transcript : transcript));
      setIsListening(false);
    };
    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);

    recognition.start();
  };

  // Group conversations by date
  const groupConversations = () => {
    const now = new Date();
    const todayStr = now.toISOString().slice(0, 10);
    const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
    const sevenDaysAgo = new Date(Date.now() - 7 * 86400000).toISOString().slice(0, 10);

    const groups = {
      Today: [],
      Yesterday: [],
      'Previous 7 Days': [],
      Older: [],
    };

    conversations.forEach((conv) => {
      const d = (conv.updated_at || conv.created_at || '').slice(0, 10);
      if (d === todayStr) groups.Today.push(conv);
      else if (d === yesterday) groups.Yesterday.push(conv);
      else if (d >= sevenDaysAgo) groups['Previous 7 Days'].push(conv);
      else groups.Older.push(conv);
    });

    return groups;
  };

  const grouped = groupConversations();
  const activeConv = conversations.find((c) => c.id === activeConvId);

  return (
    <div className="app-layout">
      <Sidebar currentPage="chat" onNavigate={onNavigate} />

      <main className="main-content" style={{ display: 'flex', gap: '20px', height: 'calc(100vh - 4rem)' }}>
        {/* Chat History Sidebar */}
        <div
          className="aw-card"
          style={{
            width: '280px',
            minWidth: '280px',
            display: 'flex',
            flexDirection: 'column',
            padding: '16px',
          }}
        >
          <button className="btn-primary btn-full" onClick={handleNewChat} style={{ marginBottom: '14px' }}>
            + New Conversation
          </button>

          <div style={{ flex: 1, overflowY: 'auto' }}>
            {Object.entries(grouped).map(([label, items]) => {
              if (items.length === 0) return null;
              return (
                <div key={label}>
                  <div className="chat-date-group-header">{label}</div>
                  {items.map((conv) => {
                    const isActive = conv.id === activeConvId;
                    return (
                      <div
                        key={conv.id}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '8px 12px',
                          borderRadius: '12px',
                          marginBottom: '4px',
                          background: isActive ? 'var(--lavender-light)' : 'transparent',
                          border: isActive ? '1px solid rgba(124,124,235,0.3)' : '1px solid transparent',
                          cursor: 'pointer',
                        }}
                        onClick={() => handleSelectConv(conv.id)}
                      >
                        {editingId === conv.id ? (
                          <input
                            type="text"
                            value={editTitle}
                            autoFocus
                            onChange={(e) => setEditTitle(e.target.value)}
                            onBlur={() => handleSaveTitle(conv.id)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSaveTitle(conv.id)}
                            onClick={(e) => e.stopPropagation()}
                            style={{ padding: '4px 8px', fontSize: '0.85rem' }}
                          />
                        ) : (
                          <div
                            style={{
                              fontSize: '0.88rem',
                              fontWeight: isActive ? 700 : 500,
                              color: 'var(--ink)',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                              flex: 1,
                            }}
                          >
                            💬 {conv.title || 'Conversation'}
                          </div>
                        )}

                        <div style={{ display: 'flex', gap: '4px', marginLeft: '6px' }} onClick={(e) => e.stopPropagation()}>
                          <button
                            style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '0.8rem', opacity: 0.7 }}
                            title="Rename"
                            onClick={() => {
                              setEditingId(conv.id);
                              setEditTitle(conv.title || '');
                            }}
                          >
                            ✏️
                          </button>
                          <button
                            style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '0.8rem', opacity: 0.7 }}
                            title="Delete"
                            onClick={() => setDeleteConfirmId(conv.id)}
                          >
                            🗑️
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              );
            })}
          </div>
        </div>

        {/* Chat Main Area */}
        <div
          className="aw-card"
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            padding: '20px',
            height: '100%',
          }}
        >
          {/* Header */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              paddingBottom: '14px',
              borderBottom: '1px solid rgba(124,124,235,0.15)',
            }}
          >
            <div>
              <h3 style={{ fontSize: '1.25rem', margin: 0 }}>
                {activeConv ? activeConv.title : 'AI Chat Companion 💬'}
              </h3>
              <p className="aw-muted" style={{ margin: 0, fontSize: '0.82rem' }}>
                Safe, supportive, and confidential mental wellness dialogue
              </p>
            </div>

            <button className="btn-secondary" onClick={() => onNavigate('dashboard')}>
              ← Dashboard
            </button>
          </div>

          {/* Delete Confirmation Modal */}
          {deleteConfirmId && (
            <div
              style={{
                background: '#fff5f6',
                border: '1px solid #fecaca',
                padding: '12px 16px',
                borderRadius: '12px',
                margin: '12px 0',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div style={{ fontSize: '0.88rem', color: '#991b1b', fontWeight: 600 }}>
                Delete this conversation? This cannot be undone.
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  className="btn-primary"
                  style={{ background: '#dc2626', padding: '4px 12px', fontSize: '0.82rem' }}
                  onClick={() => handleDeleteConversation(deleteConfirmId)}
                >
                  Confirm Delete
                </button>
                <button
                  className="btn-secondary"
                  style={{ padding: '4px 12px', fontSize: '0.82rem' }}
                  onClick={() => setDeleteConfirmId(null)}
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {/* Messages Stream */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '16px 8px' }}>
            {messages.length === 0 && (
              <div style={{ textAlign: 'center', marginTop: '60px' }} className="aw-muted">
                <div style={{ fontSize: '3rem', marginBottom: '8px' }}>🌿</div>
                <h4>Start a supportive conversation</h4>
                <p style={{ fontSize: '0.9rem', maxWidth: '400px', margin: '8px auto' }}>
                  Share how your day went, talk through difficult emotions, or ask for a grounding exercise.
                </p>
              </div>
            )}

            {messages.map((m, i) => (
              <div key={i}>
                {m.role === 'user' ? (
                  <div className="chat-user-bubble">
                    <div>{m.content}</div>
                    <div style={{ fontSize: '0.72rem', opacity: 0.8, textAlign: 'right', marginTop: '4px' }}>
                      {(m.created_at || '').slice(11, 16)}
                    </div>
                  </div>
                ) : (
                  <div className="chat-bot-bubble">
                    <div style={{ whiteSpace: 'pre-line' }}>{m.content}</div>
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginTop: '8px',
                        fontSize: '0.75rem',
                      }}
                    >
                      {m.emotion ? (
                        <span className="aw-pill" style={{ fontSize: '0.72rem', padding: '3px 8px' }}>
                          Detected: {m.emotion}
                        </span>
                      ) : (
                        <span />
                      )}
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button
                          style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '0.8rem' }}
                          title="Play audio"
                          onClick={() => speakText(m.content)}
                        >
                          🔊 Speak
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}

            {loadingReply && (
              <div className="chat-bot-bubble">
                <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                  <span>Thinking...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Chat Input Bar */}
          <form onSubmit={handleSendMessage} style={{ display: 'flex', gap: '10px', alignItems: 'center', marginTop: '12px' }}>
            <button
              type="button"
              className={isListening ? 'btn-primary' : 'btn-secondary'}
              style={{ borderRadius: '50%', width: '46px', height: '46px', padding: 0, fontSize: '1.2rem', flexShrink: 0 }}
              onClick={toggleVoiceRecording}
              title="Voice Input"
            >
              {isListening ? '⏹️' : '🎙️'}
            </button>

            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder={t('chat_input_placeholder')}
              style={{ flex: 1 }}
            />

            <button type="submit" className="btn-primary" disabled={loadingReply} style={{ height: '46px', flexShrink: 0 }}>
              {t('chat_send')} →
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
