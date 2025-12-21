import MessageBubble from './MessageBubble'
import LoadingIndicator from './LoadingIndicator'

export default function ChatHistory({ messages, isLoading }) {
    return (
        <div className="flex-1 overflow-y-auto p-6">
            <div className="max-w-4xl mx-auto space-y-4">
                {messages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full py-20 text-center">
                        <div className="w-24 h-24 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-3xl flex items-center justify-center mb-6 shadow-lg">
                            <svg className="w-12 h-12 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                            </svg>
                        </div>

                        <h2 className="text-xl font-bold text-gray-800 mb-2">
                            Start a Conversation
                        </h2>
                        <p className="text-gray-500 max-w-md mb-8">
                            Ask questions about your Shopify store data. I can help you analyze products, orders, customers, and more.
                        </p>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg">
                            {[
                                'List my top 5 products',
                                'How many orders this month?',
                                'Show customer overview',
                                'What is my total revenue?'
                            ].map((query, idx) => (
                                <div
                                    key={idx}
                                    className="px-4 py-3 bg-white border border-gray-200 rounded-xl text-sm text-gray-600 hover:border-blue-300 hover:bg-blue-50 transition-all cursor-pointer shadow-sm"
                                >
                                    "{query}"
                                </div>
                            ))}
                        </div>
                    </div>
                ) : (
                    <>
                        {messages.map((msg, index) => (
                            <MessageBubble key={index} message={msg} />
                        ))}
                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="bg-white rounded-2xl rounded-bl-md px-5 py-4 shadow-md border border-gray-100">
                                    <LoadingIndicator />
                                </div>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    )
}
