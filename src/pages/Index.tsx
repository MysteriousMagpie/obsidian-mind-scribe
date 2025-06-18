import React, { useState } from 'react';

// Update this page (the content is just a fallback if you fail to update the page)

const Index = () => {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [preview, setPreview] = useState('');
  const [loading, setLoading] = useState(false);

  const send = async () => {
    if (!message) return;
    setLoading(true);
    setResponse('');
    setPreview('');
    try {
      const res = await fetch('/api/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });
      const data = await res.json();
      setResponse(data.response);
      setPreview(data.preview);
    } catch (e: any) {
      setResponse('Error: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center p-4 bg-gray-100">
      <h1 className="text-3xl font-bold mb-4">Obsidian Agent Chat</h1>
      <textarea
        className="w-full max-w-2xl h-32 p-2 border rounded shadow"
        placeholder="Enter your message..."
        value={message}
        onChange={e => setMessage(e.target.value)}
      />
      <button
        className="mt-2 px-4 py-2 bg-blue-600 text-white rounded shadow disabled:opacity-50"
        onClick={send}
        disabled={!message || loading}
      >
        {loading ? 'Sending...' : 'Send'}
      </button>
      {response && (
        <div className="mt-6 w-full max-w-2xl grid grid-cols-2 gap-4">
          <div className="p-4 bg-white rounded shadow overflow-auto">
            <h2 className="font-semibold mb-2">Markdown</h2>
            <pre className="whitespace-pre-wrap">{response}</pre>
          </div>
          <div className="p-4 bg-white rounded shadow overflow-auto">
            <h2 className="font-semibold mb-2">Preview</h2>
            <div dangerouslySetInnerHTML={{ __html: preview }} />
          </div>
        </div>
      )}
    </div>
  );
};

export default Index;
