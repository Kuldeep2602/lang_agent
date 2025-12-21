import TableRenderer from './TableRenderer'
import ChartRenderer from './ChartRenderer'

function formatText(text) {
    if (!text) return null

    const lines = text.split('\n')

    return lines.map((line, idx) => {
        let formattedLine = line

        formattedLine = formattedLine.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>')
        formattedLine = formattedLine.replace(/__(.*?)__/g, '<strong class="font-semibold text-gray-900">$1</strong>')

        formattedLine = formattedLine.replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
        formattedLine = formattedLine.replace(/_(.*?)_/g, '<em class="italic">$1</em>')

        const numberedMatch = line.match(/^(\d+)\.\s+(.*)/)
        if (numberedMatch) {
            return (
                <div key={idx} className="flex gap-3 py-1.5">
                    <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-semibold">
                        {numberedMatch[1]}
                    </span>
                    <span
                        className="text-gray-700 leading-relaxed"
                        dangerouslySetInnerHTML={{ __html: formattedLine.replace(/^\d+\.\s+/, '') }}
                    />
                </div>
            )
        }

        if (line.trim().startsWith('- ') || line.trim().startsWith('• ') || line.trim().startsWith('* ')) {
            const bulletContent = line.trim().replace(/^[-•*]\s+/, '')
            return (
                <div key={idx} className="flex gap-2 py-1 pl-2">
                    <span className="text-blue-500 mt-1.5">•</span>
                    <span
                        className="text-gray-700 leading-relaxed"
                        dangerouslySetInnerHTML={{ __html: bulletContent }}
                    />
                </div>
            )
        }

        if (line.trim() === '') {
            return <div key={idx} className="h-3" />
        }

        return (
            <p
                key={idx}
                className="text-gray-700 leading-relaxed"
                dangerouslySetInnerHTML={{ __html: formattedLine }}
            />
        )
    })
}

export default function MessageBubble({ message }) {
    const { role, content } = message
    const isUser = role === 'user'

    if (isUser) {
        return (
            <div className="flex justify-end">
                <div className="max-w-[75%] bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-2xl rounded-br-md px-5 py-3 shadow-lg shadow-blue-500/20">
                    <p className="whitespace-pre-wrap leading-relaxed">{content.text}</p>
                </div>
            </div>
        )
    }

    return (
        <div className="flex justify-start">
            <div className="max-w-[85%] bg-white rounded-2xl rounded-bl-md px-5 py-4 shadow-lg border border-gray-100 space-y-4">
                {/* AI Badge */}
                <div className="flex items-center gap-2 pb-3 border-b border-gray-100">
                    <div className="w-7 h-7 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-lg flex items-center justify-center shadow-sm">
                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                    </div>
                    <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Clevrr AI</span>
                </div>

                {/* Text content with formatting */}
                {content.text && (
                    <div className="space-y-1">
                        {formatText(content.text)}
                    </div>
                )}

                {/* Tables */}
                {content.tables && content.tables.length > 0 && (
                    <div className="space-y-3 pt-3 border-t border-gray-100 mt-3">
                        <div className="flex items-center gap-2 text-sm text-blue-600">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                            <span className="font-semibold">Data Tables</span>
                        </div>
                        {content.tables.map((table, index) => (
                            <TableRenderer key={index} data={table} />
                        ))}
                    </div>
                )}

                {/* Charts */}
                {content.chart_data && content.chart_data.length > 0 && (
                    <div className="space-y-4 pt-3 border-t border-gray-100 mt-3">
                        {content.chart_data.map((chartData, index) => (
                            <ChartRenderer key={index} chartData={chartData} />
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}
