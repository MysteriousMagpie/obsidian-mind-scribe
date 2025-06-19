import React, { useState } from 'react';

const dateOptions = [
  { label: 'Last 7 days', value: 7 },
  { label: 'Last 30 days', value: 30 },
  { label: 'Last 90 days', value: 90 },
  { label: 'All time', value: 'all' },
];

// Update this page (the content is just a fallback if you fail to update the page)

const Index = () => {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [preview, setPreview] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dateRange, setDateRange] = useState(dateOptions[0].value);

  const send = async () => {
    if (!message) return;
    setLoading(true);
    setError('');
    setResponse('');
    setPreview('');
    try {
      const res = await fetch('/api/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, dateRange }),
      });
      let data;
      if (res.headers.get('content-type')?.includes('application/json')) {
        data = await res.json();
      } else {
        const text = await res.text();
        setError(`Server error (${res.status}): ${text || 'No response body.'}`);
        return;
      }
      if (data.error) setError(data.error);
      setResponse(data.response || '');
      setPreview(data.preview || '');
    } catch (e: any) {
      setError('Network error: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center p-4 bg-gray-100">
      <h1 className="text-3xl font-bold mb-4">Obsidian Agent Chat</h1>
      <div className="flex flex-col md:flex-row gap-2 mb-2 w-full max-w-2xl">
        <textarea
          className="flex-1 h-32 p-2 border rounded shadow"
          placeholder="Enter your message..."
          value={message}
          onChange={e => setMessage(e.target.value)}
        />
        <div className="flex flex-col gap-2 min-w-[160px]">
          <label className="font-semibold">Date Range</label>
          <select
            className="p-2 border rounded"
            value={dateRange}
            onChange={e => setDateRange(e.target.value === 'all' ? 'all' : Number(e.target.value))}
          >
            {dateOptions.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
          <button
            className="px-4 py-2 bg-blue-600 text-white rounded shadow disabled:opacity-50"
            onClick={send}
            disabled={!message || loading}
          >
            {loading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
      {error && <div className="mt-4 text-red-600 whitespace-pre-wrap">{error}</div>}
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
