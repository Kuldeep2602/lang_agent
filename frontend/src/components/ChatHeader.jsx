export default function ChatHeader({ onClearChat }) {
    return (
        <header className="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 text-white py-5 px-6 shadow-xl">
            <div className="max-w-5xl mx-auto flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                    </div>

                    <div>
                        <h1 className="text-xl font-bold tracking-tight flex items-center gap-2">
                            Clevrr
                            <span className="text-blue-200 font-normal">AI Analytics</span>
                        </h1>
                        <p className="text-blue-200 text-sm">
                            Your Shopify data, powered by AI
                        </p>
                    </div>
                </div>

                <button
                    onClick={onClearChat}
                    className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-all duration-200 text-sm font-medium backdrop-blur-sm border border-white/20"
                >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    Clear Chat
                </button>
            </div>
        </header>
    )
}
