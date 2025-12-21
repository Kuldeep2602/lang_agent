export default function TableRenderer({ data }) {
    const tableTitle = data?.title || null
    const tableData = data?.data || data

    if (!tableData || !Array.isArray(tableData) || tableData.length === 0) {
        return (
            <div className="text-gray-500 text-sm italic p-4 bg-gray-50 rounded-xl border border-gray-200">
                No data available
            </div>
        )
    }

    const headers = Object.keys(tableData[0])

    return (
        <div className="space-y-2">
            {tableTitle && (
                <h3 className="text-sm font-bold text-gray-800 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
                    {tableTitle}
                </h3>
            )}

            <div className="overflow-x-auto rounded-xl border border-gray-200 shadow-sm">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gradient-to-r from-blue-50 to-indigo-50">
                        <tr>
                            {headers.map((header) => (
                                <th
                                    key={header}
                                    className="px-4 py-3 text-left text-xs font-bold text-blue-700 uppercase tracking-wider"
                                >
                                    {formatHeader(header)}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-100">
                        {tableData.map((row, rowIndex) => (
                            <tr
                                key={rowIndex}
                                className={`hover:bg-blue-50/50 transition-colors ${rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50/50'}`}
                            >
                                {headers.map((header, colIndex) => (
                                    <td
                                        key={`${rowIndex}-${header}`}
                                        className={`px-4 py-3 text-sm ${colIndex === 0 ? 'font-medium text-gray-900' : 'text-gray-600'}`}
                                    >
                                        {formatCellValue(row[header])}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <div className="text-xs text-gray-400 text-right pr-1">
                {tableData.length} {tableData.length === 1 ? 'row' : 'rows'}
            </div>
        </div>
    )
}

function formatHeader(header) {
    return header
        .replace(/_/g, ' ')
        .replace(/([a-z])([A-Z])/g, '$1 $2')
        .replace(/\b\w/g, c => c.toUpperCase())
}

function formatCellValue(value) {
    if (value === null || value === undefined || value === '') {
        return <span className="text-gray-400">—</span>
    }
    if (typeof value === 'object') {
        return <code className="text-xs bg-gray-100 px-1.5 py-0.5 rounded text-gray-600">{JSON.stringify(value)}</code>
    }
    if (typeof value === 'string' && value.match(/^\$[\d,.]+$/)) {
        return <span className="text-green-600 font-semibold">{value}</span>
    }
    return String(value)
}
