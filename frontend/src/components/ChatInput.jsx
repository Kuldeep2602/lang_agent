export default function ChatInput({
    storeUrl,
    setStoreUrl,
    message,
    setMessage,
    onSend,
    onCancel,
    isLoading
}) {
    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
            e.preventDefault()
            onSend()
        }
    }

    return (
        <div className="bg-white/80 backdrop-blur-lg border-t border-gray-200/50 p-4 shadow-2xl">
            <div className="max-w-4xl mx-auto">
                <div className="mb-4">
                    <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-2">
                        <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                        </svg>
                        Shopify Store URL
                    </label>
                    <input
                        type="text"
                        value={storeUrl}
                        onChange={(e) => setStoreUrl(e.target.value)}
                        placeholder="your-store.myshopify.com"
                        disabled={isLoading}
                        className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:bg-white disabled:bg-gray-100 disabled:cursor-not-allowed transition-all duration-200 text-gray-800 placeholder-gray-400"
                    />
                </div>

                <div className="relative">
                    <div className="flex gap-3 items-end">
                        <div className="flex-1 relative">
                            <input
                                type="text"
                                value={message}
                                onChange={(e) => setMessage(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Ask about your store data... (e.g., 'Show me top 5 products')"
                                disabled={isLoading}
                                className="w-full px-5 py-4 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:bg-white disabled:bg-gray-100 disabled:cursor-not-allowed transition-all duration-200 text-gray-800 placeholder-gray-400 pr-12"
                            />
                            {message && !isLoading && (
                                <button
                                    onClick={() => setMessage('')}
                                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                                >
                                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                                    </svg>
                                </button>
                            )}
                        </div>

                        {isLoading ? (
                            <button
                                onClick={onCancel}
                                className="flex items-center gap-2 px-6 py-4 bg-red-500 hover:bg-red-600 text-white font-semibold rounded-2xl transition-all duration-200 shadow-lg shadow-red-500/25"
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                                Cancel
                            </button>
                        ) : (
                            <button
                                onClick={onSend}
                                disabled={!message.trim() || !storeUrl.trim()}
                                className="flex items-center gap-2 px-6 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold rounded-2xl disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-blue-500/25 disabled:shadow-none"
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                                </svg>
                                Send
                            </button>
                        )}
                    </div>

                    <p className="text-xs text-gray-400 mt-2 text-center">
                        Press <kbd className="px-1.5 py-0.5 bg-gray-100 rounded text-gray-500 font-mono text-xs">Enter</kbd> to send • Analyzing data from your Shopify store
                    </p>
                </div>
            </div>
        </div>
    )
}
