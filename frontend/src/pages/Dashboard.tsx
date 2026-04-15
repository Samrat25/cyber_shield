import { useEffect, useState } from "react"
import SpotlightCard from "@/components/SpotlightCard"
import { Activity, Shield, AlertTriangle, Network, Cpu, HardDrive, TrendingUp } from "lucide-react"
import { Line } from "react-chartjs-2"
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js"

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

type Stats = {
  total_checks: number
  total_threats: number
  safe_rate: number
  nodes: any[]
}

type Event = {
  id: string
  verdict: string
  created_at: string
  node_id: string
  cpu: number
  memory: number
  ml_score: number
  ipfs_cid?: string
  aptos_tx?: string
}

type MetricPoint = {
  timestamp: string
  cpu_percent: number
  memory_percent: number
  ml_score: number
  verdict: string
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats>({
    total_checks: 0,
    total_threats: 0,
    safe_rate: 100,
    nodes: [],
  })
  const [events, setEvents] = useState<Event[]>([])
  const [metrics, setMetrics] = useState<MetricPoint[]>([])
  const [loading, setLoading] = useState(true)

  // Get session key from URL
  const sessionKey = new URLSearchParams(window.location.search).get("key")

  useEffect(() => {
    if (!sessionKey) {
      return
    }

    const fetchData = async () => {
      try {
        // Fetch stats
        const statsRes = await fetch(`/api/stats?key=${sessionKey}`)
        const statsData = await statsRes.json()
        setStats(statsData)

        // Fetch events
        const eventsRes = await fetch(`/api/threats?key=${sessionKey}`)
        const eventsData = await eventsRes.json()
        setEvents(eventsData.events || [])

        // Fetch metrics
        const metricsRes = await fetch(`/api/metrics?key=${sessionKey}`)
        const metricsData = await metricsRes.json()
        setMetrics(metricsData.history?.slice(-30) || [])

        setLoading(false)
      } catch (err) {
        console.error("Fetch error:", err)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 5000)

    return () => clearInterval(interval)
  }, [sessionKey])

  if (!sessionKey) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <SpotlightCard className="rounded-[2rem] border-white/10 bg-white/10 p-8 text-center">
          <AlertTriangle className="mx-auto mb-4 size-12 text-red-500" />
          <h2 className="text-2xl font-bold text-white">Access Denied</h2>
          <p className="mt-2 text-white/70">
            Missing dashboard key. Please use the link provided by the CLI.
          </p>
        </SpotlightCard>
      </div>
    )
  }

  // Prepare chart data
  const chartData = {
    labels: metrics.map((m) => {
      const t = new Date(m.timestamp)
      return t.toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      })
    }),
    datasets: [
      {
        label: "CPU %",
        data: metrics.map((m) => m.cpu_percent || 0),
        borderColor: "#dc2626",
        backgroundColor: "rgba(220, 38, 38, 0.1)",
        tension: 0.4,
        fill: true,
      },
      {
        label: "Memory %",
        data: metrics.map((m) => m.memory_percent || 0),
        borderColor: "#ef4444",
        backgroundColor: "rgba(239, 68, 68, 0.1)",
        tension: 0.4,
        fill: true,
      },
      {
        label: "Anomaly Risk %",
        data: metrics.map((m) => {
          const score = m.ml_score || 0
          const verdict = m.verdict || "safe"
          if (verdict === "anomaly") {
            return Math.min(100, 60 + Math.abs(score) * 100)
          }
          return Math.max(0, 40 - score * 80)
        }),
        borderColor: "#f59e0b",
        backgroundColor: "rgba(245, 158, 11, 0.1)",
        tension: 0.4,
        fill: true,
        borderWidth: 3,
      },
    ],
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 2.5,
    plugins: {
      legend: {
        labels: {
          color: "#e2e8f0",
          font: { size: 13 },
        },
      },
      tooltip: {
        backgroundColor: "rgba(15, 23, 42, 0.9)",
        titleColor: "#e2e8f0",
        bodyColor: "#94a3b8",
        borderColor: "#dc2626",
        borderWidth: 1,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          color: "#94a3b8",
          callback: (value: any) => value + "%",
        },
        grid: { color: "rgba(148, 163, 184, 0.1)" },
      },
      x: {
        ticks: {
          color: "#94a3b8",
          maxTicksLimit: 10,
        },
        grid: { color: "rgba(148, 163, 184, 0.1)" },
      },
    },
  }

  return (
    <div className="min-h-screen p-6">
      {/* Header */}
      <div className="mb-8">
        <SpotlightCard
          className="rounded-[2rem] border-white/10 bg-white/8 p-8 text-center backdrop-blur-md"
          spotlightColor="rgba(220, 38, 38, 0.12)"
        >
          <h1 className="mb-2 font-heading text-4xl font-bold text-white">
            🛡️ CyberShield Dashboard
          </h1>
          <p className="text-lg text-white/70">
            Real-Time Blockchain-Based Intrusion Detection System
          </p>
          <div className="mt-4 inline-flex items-center gap-2 rounded-full border border-green-500/30 bg-green-500/10 px-4 py-2 text-sm font-semibold text-green-400">
            <span className="relative flex size-2">
              <span className="absolute inline-flex size-full animate-ping rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex size-2 rounded-full bg-green-500"></span>
            </span>
            SYSTEM ONLINE
          </div>
        </SpotlightCard>
      </div>

      {/* Stats Grid */}
      <div className="mb-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <SpotlightCard
          className="rounded-[2rem] border-white/10 bg-white/8 p-6 backdrop-blur-md"
          spotlightColor="rgba(220, 38, 38, 0.12)"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-wider text-white/60">
                Total Checks
              </p>
              <p className="mt-2 text-4xl font-bold text-white">
                {stats.total_checks}
              </p>
            </div>
            <div className="rounded-2xl bg-[#dc2626]/20 p-3">
              <Activity className="size-8 text-[#dc2626]" />
            </div>
          </div>
        </SpotlightCard>

        <SpotlightCard
          className="rounded-[2rem] border-white/10 bg-white/8 p-6 backdrop-blur-md"
          spotlightColor="rgba(239, 68, 68, 0.12)"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-wider text-white/60">
                Threats Detected
              </p>
              <p className="mt-2 text-4xl font-bold text-[#ef4444]">
                {stats.total_threats}
              </p>
            </div>
            <div className="rounded-2xl bg-[#ef4444]/20 p-3">
              <AlertTriangle className="size-8 text-[#ef4444]" />
            </div>
          </div>
        </SpotlightCard>

        <SpotlightCard
          className="rounded-[2rem] border-white/10 bg-white/8 p-6 backdrop-blur-md"
          spotlightColor="rgba(34, 197, 94, 0.12)"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-wider text-white/60">
                Safe Rate
              </p>
              <p className="mt-2 text-4xl font-bold text-[#22c55e]">
                {stats.safe_rate.toFixed(1)}%
              </p>
            </div>
            <div className="rounded-2xl bg-[#22c55e]/20 p-3">
              <Shield className="size-8 text-[#22c55e]" />
            </div>
          </div>
        </SpotlightCard>

        <SpotlightCard
          className="rounded-[2rem] border-white/10 bg-white/8 p-6 backdrop-blur-md"
          spotlightColor="rgba(220, 38, 38, 0.12)"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-wider text-white/60">
                Active Nodes
              </p>
              <p className="mt-2 text-4xl font-bold text-white">
                {stats.nodes.length}
              </p>
            </div>
            <div className="rounded-2xl bg-[#dc2626]/20 p-3">
              <Network className="size-8 text-[#dc2626]" />
            </div>
          </div>
        </SpotlightCard>
      </div>

      {/* Metrics Chart */}
      <div className="mb-8">
        <SpotlightCard
          className="rounded-[2rem] border-white/10 bg-white/8 p-6 backdrop-blur-md"
          spotlightColor="rgba(220, 38, 38, 0.12)"
        >
          <div className="mb-6 flex items-center gap-3">
            <TrendingUp className="size-6 text-[#dc2626]" />
            <h2 className="text-2xl font-bold text-white">
              Real-Time System Metrics
            </h2>
          </div>
          {loading ? (
            <div className="flex h-64 items-center justify-center">
              <div className="size-12 animate-spin rounded-full border-4 border-[#dc2626]/30 border-t-[#dc2626]"></div>
            </div>
          ) : (
            <Line data={chartData} options={chartOptions} />
          )}
        </SpotlightCard>
      </div>

      {/* Events Log */}
      <div>
        <SpotlightCard
          className="rounded-[2rem] border-white/10 bg-white/8 p-6 backdrop-blur-md"
          spotlightColor="rgba(220, 38, 38, 0.12)"
        >
          <div className="mb-6 flex items-center gap-3">
            <Activity className="size-6 text-[#dc2626]" />
            <h2 className="text-2xl font-bold text-white">
              Event Log (Blockchain Verified)
            </h2>
          </div>

          <div className="max-h-[600px] space-y-4 overflow-y-auto">
            {loading ? (
              <div className="flex h-32 items-center justify-center">
                <div className="size-12 animate-spin rounded-full border-4 border-[#dc2626]/30 border-t-[#dc2626]"></div>
              </div>
            ) : events.length === 0 ? (
              <p className="py-8 text-center text-white/60">
                No events yet. Start monitoring to see data.
              </p>
            ) : (
              events.map((event) => {
                const isAnomaly = event.verdict === "anomaly"
                const time = new Date(event.created_at).toLocaleString()

                return (
                  <SpotlightCard
                    key={event.id}
                    className={`rounded-[1.5rem] border-l-4 p-4 ${
                      isAnomaly
                        ? "border-l-[#ef4444] bg-[#ef4444]/10"
                        : "border-l-[#22c55e] bg-[#22c55e]/10"
                    }`}
                    spotlightColor={
                      isAnomaly
                        ? "rgba(239, 68, 68, 0.12)"
                        : "rgba(34, 197, 94, 0.12)"
                    }
                  >
                    <div className="flex items-center justify-between">
                      <span
                        className={`text-lg font-bold ${
                          isAnomaly ? "text-[#ef4444]" : "text-[#22c55e]"
                        }`}
                      >
                        {isAnomaly ? "⚠️ ANOMALY" : "✓ SAFE"}
                      </span>
                      <span className="text-sm text-white/60">{time}</span>
                    </div>

                    <div className="mt-3 grid grid-cols-2 gap-3 text-sm md:grid-cols-4">
                      <div>
                        <span className="text-white/60">Node:</span>{" "}
                        <span className="text-white">
                          {event.node_id || "N/A"}
                        </span>
                      </div>
                      <div>
                        <span className="text-white/60">CPU:</span>{" "}
                        <span className="text-white">
                          {event.cpu.toFixed(1)}%
                        </span>
                      </div>
                      <div>
                        <span className="text-white/60">Memory:</span>{" "}
                        <span className="text-white">
                          {event.memory.toFixed(1)}%
                        </span>
                      </div>
                      <div>
                        <span className="text-white/60">ML Score:</span>{" "}
                        <span className="text-white">
                          {event.ml_score.toFixed(3)}
                        </span>
                      </div>
                    </div>

                    {event.ipfs_cid && (
                      <div className="mt-3 text-sm">
                        <span className="text-white/60">📦 IPFS CID:</span>{" "}
                        <code className="rounded bg-black/30 px-2 py-1 text-xs text-white">
                          {event.ipfs_cid}
                        </code>
                        <a
                          href={`https://gateway.pinata.cloud/ipfs/${event.ipfs_cid}`}
                          target="_blank"
                          rel="noreferrer"
                          className="ml-2 text-[#dc2626] hover:underline"
                        >
                          View on Gateway →
                        </a>
                      </div>
                    )}

                    {event.aptos_tx && (
                      <div className="mt-2 text-sm">
                        <span className="text-white/60">⛓️ Aptos TX:</span>{" "}
                        <code className="rounded bg-black/30 px-2 py-1 text-xs text-white">
                          {event.aptos_tx.substring(0, 30)}...
                        </code>
                        <a
                          href={`https://explorer.aptoslabs.com/txn/${event.aptos_tx}?network=testnet`}
                          target="_blank"
                          rel="noreferrer"
                          className="ml-2 text-[#dc2626] hover:underline"
                        >
                          View on Explorer →
                        </a>
                      </div>
                    )}
                  </SpotlightCard>
                )
              })
            )}
          </div>
        </SpotlightCard>
      </div>

      {/* Footer */}
      <div className="mt-8 text-center">
        <div className="mb-4 flex flex-wrap justify-center gap-2">
          {["Aptos Blockchain", "IPFS Storage", "ML Ensemble", "P2P Network", "Supabase"].map(
            (tech) => (
              <span
                key={tech}
                className="rounded-full border border-[#dc2626]/30 bg-[#dc2626]/10 px-3 py-1 text-sm text-[#dc2626]"
              >
                {tech}
              </span>
            )
          )}
        </div>
        <p className="text-sm text-white/50">
          CyberShield v1.0 - Decentralized IDS for the Modern Era
        </p>
      </div>
    </div>
  )
}
