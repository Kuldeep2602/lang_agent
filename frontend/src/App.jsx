import { useState, useRef, useEffect } from 'react'

// API URL - uses environment variable in production, empty for local dev (proxy)
const API_URL = import.meta.env.VITE_API_URL || ''

function App() {
  const [storeUrl, setStoreUrl] = useState('clevrr-test.myshopify.com')
  const [message, setMessage] = useState('')
  const [chatHistory, setChatHistory] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [showSettings, setShowSettings] = useState(false)

  const abortControllerRef = useRef(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [chatHistory])

  const handleCancel = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
      setIsLoading(false)
      setChatHistory((prev) => [...prev, {
        role: 'agent',
        content: { text: '⚠️ Request cancelled.', tables: [], chart_data: [] }
      }])
    }
  }

  const handleSend = async () => {
    if (!message.trim() || !storeUrl.trim() || isLoading) return

    setChatHistory((prev) => [...prev, { role: 'user', content: { text: message } }])
    const currentMessage = message
    setMessage('')
    setIsLoading(true)
    abortControllerRef.current = new AbortController()

    try {
      const response = await fetch(`${API_URL}/api/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ store_url: storeUrl, query: currentMessage }),
        signal: abortControllerRef.current.signal,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || `Request failed`)
      }

      const data = await response.json()
      setChatHistory((prev) => [...prev, {
        role: 'agent',
        content: { text: data.text || '', tables: data.tables || [], chart_data: data.chart_data || [] }
      }])
    } catch (err) {
      if (err.name === 'AbortError') return
      setChatHistory((prev) => [...prev, {
        role: 'agent',
        content: { text: `❌ ${err.message}`, tables: [], chart_data: [] }
      }])
    } finally {
      setIsLoading(false)
      abortControllerRef.current = null
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', background: '#fff' }}>
      <header style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '12px 24px',
        borderBottom: '1px solid #e5e7eb',
        background: '#fff',
        flexShrink: 0
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            background: 'linear-gradient(135deg, #3b82f6, #6366f1)',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
              <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <span style={{ fontSize: '18px', fontWeight: '600', color: '#1f2937' }}>Clevrr AI</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            onClick={() => setShowSettings(!showSettings)}
            style={{
              padding: '8px',
              background: showSettings ? '#f3f4f6' : 'transparent',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              color: '#6b7280'
            }}
          >
            ⚙️
          </button>
          <button
            onClick={() => setChatHistory([])}
            style={{
              padding: '8px 16px',
              background: '#f3f4f6',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              color: '#374151'
            }}
          >
            New Chat
          </button>
        </div>
      </header>

      {showSettings && (
        <div style={{ padding: '12px 24px', background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
          <label style={{ fontSize: '12px', fontWeight: '500', color: '#6b7280', textTransform: 'uppercase' }}>Store URL</label>
          <input
            type="text"
            value={storeUrl}
            onChange={(e) => setStoreUrl(e.target.value)}
            style={{
              marginTop: '4px',
              width: '100%',
              maxWidth: '400px',
              padding: '8px 12px',
              border: '1px solid #d1d5db',
              borderRadius: '8px',
              fontSize: '14px',
              display: 'block'
            }}
            placeholder="your-store.myshopify.com"
          />
        </div>
      )}

      <div style={{ flex: 1, overflow: 'auto', padding: '20px' }}>
        {chatHistory.length === 0 ? (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            textAlign: 'center'
          }}>
            <div style={{
              width: '64px',
              height: '64px',
              background: 'linear-gradient(135deg, #dbeafe, #e0e7ff)',
              borderRadius: '16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '16px'
            }}>
              <span style={{ fontSize: '28px' }}>💬</span>
            </div>
            <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#1f2937', marginBottom: '8px' }}>
              How can I help you?
            </h2>
            <p style={{ color: '#6b7280', maxWidth: '320px', marginBottom: '24px' }}>
              Ask questions about your Shopify store data
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', justifyContent: 'center', maxWidth: '500px' }}>
              {['List 2 products', 'What is the price of...'].map((q) => (
                <button
                  key={q}
                  onClick={() => setMessage(q)}
                  style={{
                    padding: '10px 16px',
                    background: '#f3f4f6',
                    border: 'none',
                    borderRadius: '20px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    color: '#4b5563'
                  }}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div style={{ maxWidth: '800px', margin: '0 auto' }}>
            {chatHistory.map((msg, index) => (
              <MessageBubble key={index} message={msg} />
            ))}
            {isLoading && (
              <div style={{ display: 'flex', justifyContent: 'flex-start', marginTop: '16px' }}>
                <div style={{
                  background: '#f3f4f6',
                  borderRadius: '16px',
                  borderBottomLeftRadius: '4px',
                  padding: '12px 16px'
                }}>
                  <span style={{ color: '#6b7280' }}>Thinking...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <div style={{
        borderTop: '1px solid #e5e7eb',
        padding: '16px 24px',
        background: '#fff',
        flexShrink: 0
      }}>
        <div style={{ maxWidth: '800px', margin: '0 auto' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            background: '#f3f4f6',
            borderRadius: '24px',
            padding: '8px 16px',
            border: '1px solid #e5e7eb'
          }}>
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message..."
              disabled={isLoading}
              style={{
                flex: 1,
                background: 'transparent',
                border: 'none',
                outline: 'none',
                padding: '8px 0',
                fontSize: '15px',
                color: '#1f2937'
              }}
            />
            {isLoading ? (
              <button
                onClick={handleCancel}
                style={{
                  padding: '10px 20px',
                  background: '#ef4444',
                  color: 'white',
                  border: 'none',
                  borderRadius: '16px',
                  cursor: 'pointer',
                  fontWeight: '500',
                  fontSize: '14px'
                }}
              >
                Cancel
              </button>
            ) : (
              <button
                onClick={handleSend}
                disabled={!message.trim() || !storeUrl.trim()}
                style={{
                  padding: '10px 20px',
                  background: message.trim() && storeUrl.trim()
                    ? 'linear-gradient(135deg, #3b82f6, #6366f1)'
                    : '#d1d5db',
                  color: 'white',
                  border: 'none',
                  borderRadius: '16px',
                  cursor: message.trim() && storeUrl.trim() ? 'pointer' : 'not-allowed',
                  fontWeight: '500',
                  fontSize: '14px'
                }}
              >
                Send
              </button>
            )}
          </div>
          <p style={{ textAlign: 'center', fontSize: '12px', color: '#9ca3af', marginTop: '8px' }}>
            Press Enter to send, Shift + Enter for new line
          </p>
        </div>
      </div>
    </div>
  )
}

function MessageBubble({ message }) {
  const { role, content } = message
  const isUser = role === 'user'

  if (isUser) {
    return (
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '16px' }}>
        <div style={{
          maxWidth: '70%',
          background: 'linear-gradient(135deg, #3b82f6, #6366f1)',
          color: 'white',
          borderRadius: '16px',
          borderBottomRightRadius: '4px',
          padding: '12px 16px'
        }}>
          <p style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{content.text}</p>
        </div>
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: '16px' }}>
      <div style={{
        maxWidth: '80%',
        background: '#f3f4f6',
        borderRadius: '16px',
        borderBottomLeftRadius: '4px',
        padding: '12px 16px'
      }}>
        <div style={{ color: '#1f2937', whiteSpace: 'pre-wrap', lineHeight: '1.5' }}>
          {content.text}
        </div>

        {content.tables && content.tables.length > 0 && (
          <div style={{ marginTop: '12px' }}>
            {content.tables.map((table, idx) => (
              <TableView key={idx} data={table} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function TableView({ data }) {
  const tableData = data?.data || data
  if (!tableData || !Array.isArray(tableData) || tableData.length === 0) return null

  const headers = Object.keys(tableData[0])

  return (
    <div style={{
      overflow: 'auto',
      borderRadius: '8px',
      border: '1px solid #e5e7eb',
      background: 'white',
      marginTop: '8px'
    }}>
      {data?.title && (
        <div style={{
          padding: '8px 12px',
          background: '#f9fafb',
          borderBottom: '1px solid #e5e7eb',
          fontSize: '12px',
          fontWeight: '600',
          color: '#4b5563',
          textTransform: 'uppercase'
        }}>
          {data.title}
        </div>
      )}
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
        <thead>
          <tr style={{ background: '#f9fafb' }}>
            {headers.map((h) => (
              <th key={h} style={{
                padding: '8px 12px',
                textAlign: 'left',
                fontWeight: '600',
                color: '#374151',
                fontSize: '12px',
                textTransform: 'uppercase'
              }}>
                {h.replace(/_/g, ' ')}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {tableData.map((row, i) => (
            <tr key={i} style={{ borderTop: '1px solid #f3f4f6' }}>
              {headers.map((h) => (
                <td key={h} style={{ padding: '8px 12px', color: '#4b5563' }}>
                  {row[h] === null || row[h] === undefined || row[h] === '' ? '—' : String(row[h])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default App
