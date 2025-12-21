import {
    BarChart,
    Bar,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from 'recharts'

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6']

export default function ChartRenderer({ chartData }) {
    if (!chartData || !chartData.data || chartData.data.length === 0) {
        return null
    }

    const { data, type, title } = chartData

    const chartType = type || 'bar'


    const keys = Object.keys(data[0])
    const xAxisKey = keys[0]
    const dataKeys = keys.slice(1).filter(key =>
        typeof data[0][key] === 'number'
    )

    const renderChart = () => {
        if (chartType === 'line') {
            return (
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis
                        dataKey={xAxisKey}
                        tick={{ fontSize: 12 }}
                        stroke="#6b7280"
                    />
                    <YAxis
                        tick={{ fontSize: 12 }}
                        stroke="#6b7280"
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: 'white',
                            border: '1px solid #e5e7eb',
                            borderRadius: '8px',
                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                        }}
                    />
                    <Legend />
                    {dataKeys.map((key, index) => (
                        <Line
                            key={key}
                            type="monotone"
                            dataKey={key}
                            stroke={COLORS[index % COLORS.length]}
                            strokeWidth={2}
                            dot={{ fill: COLORS[index % COLORS.length], strokeWidth: 2 }}
                            activeDot={{ r: 6 }}
                        />
                    ))}
                </LineChart>
            )
        }

        return (
            <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis
                    dataKey={xAxisKey}
                    tick={{ fontSize: 12 }}
                    stroke="#6b7280"
                />
                <YAxis
                    tick={{ fontSize: 12 }}
                    stroke="#6b7280"
                />
                <Tooltip
                    contentStyle={{
                        backgroundColor: 'white',
                        border: '1px solid #e5e7eb',
                        borderRadius: '8px',
                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }}
                />
                <Legend />
                {dataKeys.map((key, index) => (
                    <Bar
                        key={key}
                        dataKey={key}
                        fill={COLORS[index % COLORS.length]}
                        radius={[4, 4, 0, 0]}
                    />
                ))}
            </BarChart>
        )
    }

    return (
        <div className="bg-gray-50 rounded-lg p-4">
            {title && (
                <h4 className="text-sm font-semibold text-gray-700 mb-3">{title}</h4>
            )}
            <ResponsiveContainer width="100%" height={300}>
                {renderChart()}
            </ResponsiveContainer>
        </div>
    )
}
