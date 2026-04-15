import { buttonVariants } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import ShinyText from "@/components/ShinyText"
import SpotlightCard from "@/components/SpotlightCard"
import {
  ArrowDown,
  ArrowRight,
  BookOpen,
  Chrome,
  Coins,
  Github,
  ShieldCheck,
  Sparkles,
  TerminalSquare,
  WalletCards,
  Workflow,
  type LucideIcon,
} from "lucide-react"
import { lazy, Suspense } from "react"

const Silk = lazy(() => import("@/components/Silk"))

type Feature = {
  icon: LucideIcon
  title: string
  description: string
}

type GuideStep = {
  step: string
  title: string
  description: string
  note: string
}

type CodePanelProps = {
  label: string
  title: string
  code: string
  className?: string
}

type IconLinkProps = {
  href: string
  icon: LucideIcon
  label: string
  className?: string
}

const heroBullets = [
  "P2P blockchain-based threat detection",
  "ML-powered anomaly detection",
  "Real-time phishing detection",
  "Decentralized security network",
]

const helperRoutes = [
  "GET /api/health",
  "GET /api/stats",
  "POST /api/detect",
  "GET /api/threats",
  "POST /api/report",
]

const features: Feature[] = [
  {
    icon: ShieldCheck,
    title: "Blockchain-based detection",
    description:
      "Decentralized P2P network shares threat intelligence across nodes for real-time protection.",
  },
  {
    icon: Coins,
    title: "ML anomaly detection",
    description:
      "Machine learning models identify suspicious patterns and zero-day threats automatically.",
  },
  {
    icon: WalletCards,
    title: "Distributed architecture",
    description:
      "Scalable P2P network architecture enables seamless node communication and threat sharing.",
  },
  {
    icon: Workflow,
    title: "Real-time monitoring",
    description:
      "Live dashboard with threat visualization, network statistics, and node health monitoring.",
  },
]

const guideSteps: GuideStep[] = [
  {
    step: "01",
    title: "Install CyberShield",
    description:
      "Install the package using pip and set up your virtual environment for the security platform.",
    note: "Start with the package command below, then configure your node.",
  },
  {
    step: "02",
    title: "Start a security node",
    description:
      "Launch a P2P node that connects to the decentralized network and shares threat intelligence.",
    note: "Each node contributes to the collective security of the network.",
  },
  {
    step: "03",
    title: "Enable ML detection",
    description:
      "Train or load ML models to detect anomalies, malware, and suspicious network activity.",
    note: "The system learns from patterns and adapts to new threats automatically.",
  },
  {
    step: "04",
    title: "Configure blockchain",
    description:
      "Set up blockchain integration for immutable threat logging and verification.",
    note: "All detected threats are recorded on the blockchain for transparency.",
  },
  {
    step: "05",
    title: "Access the dashboard",
    description:
      "Monitor network activity, view threat statistics, and manage your security node through the web interface.",
    note: "Real-time visualization of threats and network health.",
  },
  {
    step: "06",
    title: "Deploy with Docker",
    description:
      "Use Docker Compose to deploy multiple nodes, dashboard, and indexer for a complete security infrastructure.",
    note: "Scalable containerized deployment with automatic health checks.",
  },
]

const paymentFlow = [
  "A threat is detected by any node in the network.",
  "The detection is verified and logged to the blockchain.",
  "All connected nodes receive the threat intelligence update.",
  "ML models are updated with new patterns for future detection.",
]

const installCode = `pip install -r requirements.txt

# Activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\\Scripts\\activate     # Windows

# Install CyberShield
pip install -e .`

const quickStartCode = `# Start a security node
python -m cybershield.cli node start --port 8000

# Run ML detection
python -m cybershield.cli ml detect \\
  --data network_traffic.csv

# Train custom model
python -m cybershield.cli ml train \\
  --data training_data.csv

# View node status
python -m cybershield.cli node status`

const extensionCode = `# Access the dashboard
http://localhost:8080

# View network stats
# Monitor threats
# Check node health
# Review detection logs`

const overrideCode = `# Docker deployment
docker-compose up -d

# Services:
# - Node 1: localhost:8001
# - Node 2: localhost:8002
# - Dashboard: localhost:8080
# - Indexer: localhost:5432`

const resourceLinks: IconLinkProps[] = [
  {
    href: "https://github.com/yourusername/cyber_shield",
    icon: BookOpen,
    label: "Documentation",
    className:
      "border-[#dc2626]/35 text-[#fca5a5] hover:bg-[#dc2626]/16 hover:text-white",
  },
  {
    href: "https://github.com/yourusername/cyber_shield",
    icon: Github,
    label: "GitHub",
    className:
      "border-[#dc2626]/35 text-[#fca5a5] hover:bg-[#dc2626]/16 hover:text-white",
  },
]

function IconLink({ href, icon: Icon, label, className }: IconLinkProps) {
  return (
    <a
      aria-label={label}
      className={cn(
        "flex size-11 items-center justify-center rounded-full border bg-white/8 text-white/72 transition",
        className,
      )}
      href={href}
      rel="noreferrer"
      target="_blank"
      title={label}
    >
      <Icon className="size-4.5" />
    </a>
  )
}

function SectionHeading({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string
  title: string
  description: string
}) {
  return (
    <div className="max-w-3xl">
      <p className="text-sm font-semibold uppercase tracking-[0.28em] text-[#fca5a5]">
        {eyebrow}
      </p>
      <h2 className="mt-4 font-heading text-4xl leading-tight text-white sm:text-5xl">
        {title}
      </h2>
      <p className="mt-5 text-lg leading-8 text-white/72">{description}</p>
    </div>
  )
}

function CodePanel({ label, title, code, className }: CodePanelProps) {
  return (
    <SpotlightCard
      spotlightColor="rgba(220, 38, 38, 0.12)"
      className={cn(
        "overflow-hidden rounded-[2rem] border-white/12 bg-[#450a0a]/92 text-white",
        className,
      )}
    >
      <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-white/45">
            {label}
          </p>
          <h3 className="mt-2 text-lg font-semibold text-white">{title}</h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="size-2.5 rounded-full bg-[#dc2626]" />
          <span className="size-2.5 rounded-full bg-[#ef4444]" />
          <span className="size-2.5 rounded-full bg-[#f87171]" />
        </div>
      </div>
      <pre className="overflow-x-auto px-5 py-5 text-sm leading-7 text-white/86">
        <code>{code}</code>
      </pre>
    </SpotlightCard>
  )
}

function App() {
  return (
    <main id="top" className="relative min-h-screen overflow-x-hidden text-white">
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute inset-0">
          <Suspense
            fallback={
              <div className="h-full w-full bg-[#7f1d1d]" />
            }
          >
            <Silk
              speed={5}
              scale={1}
              color="#dc2626"
              noiseIntensity={1.4}
              rotation={0}
            />
          </Suspense>
        </div>
      </div>

      <div className="relative z-10">
        <header className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-6 sm:flex-row sm:items-center sm:justify-between lg:px-10">
          <div className="flex items-center gap-3">
            <div className="rounded-full border border-white/15 bg-white/8 px-4 py-2 text-xs font-semibold uppercase tracking-[0.28em] text-white/75 backdrop-blur-md">
              CyberShield
            </div>
            <span className="hidden text-sm text-white/55 sm:inline">
              Decentralized blockchain-based threat detection
            </span>
          </div>

          <div className="flex items-center gap-4">
            <nav className="flex flex-wrap items-center gap-3 text-sm text-white/70">
              <a className="transition hover:text-white" href="#modules">
                Modules
              </a>
              <a className="transition hover:text-white" href="#build">
                Build
              </a>
              <a className="transition hover:text-white" href="#flow">
                Flow
              </a>
            </nav>
            <div className="flex items-center gap-2">
              {resourceLinks.map((link) => (
                <IconLink key={link.label} {...link} />
              ))}
            </div>
          </div>
        </header>

        <section className="mx-auto max-w-7xl px-6 pb-24 pt-14 lg:px-10">
          <div className="grid gap-12 lg:grid-cols-[1.1fr_0.9fr] lg:items-end">
            <div className="max-w-3xl">
              <div className="inline-flex flex-wrap items-center gap-2 rounded-full border border-white/12 bg-white/8 px-4 py-2 text-sm text-white/72 backdrop-blur-md">
                <Sparkles className="size-4 text-[#fca5a5]" />
                <ShinyText
                  className="font-medium tracking-[0.02em]"
                  color="#fca5a5"
                  delay={0}
                  direction="left"
                  shineColor="#ffffff"
                  speed={2}
                  spread={120}
                  text="P2P blockchain-based threat detection"
                />
              </div>

              <h1 className="mt-7 font-heading text-5xl leading-[0.95] text-white sm:text-6xl lg:text-7xl">
                Decentralized cybersecurity powered by blockchain and AI.
              </h1>

              <p className="mt-6 max-w-2xl text-lg leading-8 text-white/76 sm:text-xl">
                CyberShield combines P2P networking, machine learning, and blockchain technology to create a distributed threat detection system. Share intelligence, detect anomalies, and protect against emerging threats in real-time.
              </p>

              <div className="mt-8 flex flex-wrap gap-4">
                <a
                  className={cn(
                    buttonVariants({ size: "lg" }),
                    "h-11 rounded-full px-5 text-sm font-semibold shadow-[0_20px_60px_rgba(220,38,38,0.28)]",
                  )}
                  href="#build"
                >
                  Scroll to build
                  <ArrowDown className="size-4" />
                </a>
                <a
                  className={cn(
                    buttonVariants({ variant: "outline", size: "lg" }),
                    "h-11 rounded-full border-white/15 bg-white/8 px-5 text-sm text-white hover:bg-white/14 hover:text-white",
                  )}
                  href="#modules"
                >
                  Explore modules
                  <ArrowRight className="size-4" />
                </a>
              </div>

              <div className="mt-10 grid gap-3 sm:grid-cols-2">
                {heroBullets.map((bullet) => (
                  <SpotlightCard
                    key={bullet}
                    className="rounded-[1.5rem] border-white/10 bg-white/8 px-4 py-4 text-sm text-white/80"
                    spotlightColor="rgba(220, 38, 38, 0.12)"
                  >
                    {bullet}
                  </SpotlightCard>
                ))}
              </div>
            </div>

            <div className="grid gap-5">
              <SpotlightCard
                className="rounded-[2rem] border-white/12 bg-white/10 p-6"
                spotlightColor="rgba(220, 38, 38, 0.14)"
              >
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.28em] text-white/45">
                      Security Platform
                    </p>
                    <h2 className="mt-2 text-2xl font-semibold text-white">
                      Multiple layers of protection working together.
                    </h2>
                  </div>
                  <div className="rounded-2xl border border-white/12 bg-white/8 p-3">
                    <TerminalSquare className="size-6 text-[#fca5a5]" />
                  </div>
                </div>

                <div className="mt-5 space-y-3">
                  {features.slice(0, 3).map((feature) => (
                    <SpotlightCard
                      key={feature.title}
                      className="rounded-[1.35rem] border-white/10 bg-black/18 px-4 py-4"
                      spotlightColor="rgba(220, 38, 38, 0.1)"
                    >
                      <div className="flex items-center gap-3">
                        <div className="flex size-10 items-center justify-center rounded-2xl bg-[#dc2626]/18 text-[#fca5a5]">
                          <feature.icon className="size-5" />
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-white">
                            {feature.title}
                          </p>
                          <p className="mt-1 text-sm leading-6 text-white/66">
                            {feature.description}
                          </p>
                        </div>
                      </div>
                    </SpotlightCard>
                  ))}
                </div>
              </SpotlightCard>

              <SpotlightCard
                className="rounded-[2rem] border-white/12 bg-black/20 p-6"
                spotlightColor="rgba(220, 38, 38, 0.12)"
              >
                <p className="text-xs font-semibold uppercase tracking-[0.28em] text-white/45">
                  Getting Started
                </p>
                <h2 className="mt-2 text-2xl font-semibold text-white">
                  Installation and setup guide below.
                </h2>
                <p className="mt-4 text-[15px] leading-7 text-white/72">
                  The homepage stays security-first. Scroll down for installation commands, CLI usage, Docker deployment, and the complete guide to running your own security node.
                </p>
              </SpotlightCard>
            </div>
          </div>
        </section>

        <section
          id="modules"
          className="mx-auto max-w-7xl px-6 py-20 lg:px-10"
        >
          <div className="rounded-[2.5rem] border border-white/10 bg-white/5 p-6 backdrop-blur-xl sm:p-8">
            <SectionHeading
              eyebrow="Modules"
              title="A comprehensive security platform with multiple protection layers."
              description="Each component serves a specific purpose: P2P threat sharing, ML-based detection, blockchain verification, and real-time monitoring through an intuitive dashboard."
            />

            <div className="mt-12 grid gap-6 md:grid-cols-2 xl:grid-cols-4">
              {features.map((feature) => (
                <SpotlightCard
                  key={feature.title}
                  className="rounded-[2rem] border-white/10 bg-white/86 p-6 text-[#450a0a]"
                  spotlightColor="rgba(220, 38, 38, 0.14)"
                >
                  <div className="flex size-12 items-center justify-center rounded-2xl bg-[#fee2e2] text-[#dc2626]">
                    <feature.icon className="size-5" />
                  </div>
                  <h3 className="mt-6 text-xl font-semibold">{feature.title}</h3>
                  <p className="mt-4 text-[15px] leading-7 text-[#7f1d1d]">
                    {feature.description}
                  </p>
                </SpotlightCard>
              ))}
            </div>

            <div className="mt-6 grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
              <SpotlightCard
                className="rounded-[2.25rem] border-white/10 bg-white/86 p-6 text-[#450a0a]"
                spotlightColor="rgba(220, 38, 38, 0.18)"
              >
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.28em] text-[#dc2626]">
                      Detection and Response
                    </p>
                    <h3 className="mt-3 text-2xl font-semibold">
                      Client and server components work seamlessly together.
                    </h3>
                  </div>
                  <div className="rounded-2xl bg-[#fee2e2] p-3 text-[#dc2626]">
                    <WalletCards className="size-6" />
                  </div>
                </div>

                <div className="mt-6 grid gap-4 md:grid-cols-2">
                  <div className="rounded-[1.5rem] border border-[#fecaca] bg-[#fef2f2] p-4">
                    <p className="text-sm font-semibold">CLI Interface</p>
                    <p className="mt-2 text-sm leading-6 text-[#7f1d1d]">
                      Command-line tools for node management, threat detection, and ML model training.
                    </p>
                  </div>
                  <div className="rounded-[1.5rem] border border-[#fecaca] bg-[#fef2f2] p-4">
                    <p className="text-sm font-semibold">Web Dashboard</p>
                    <p className="mt-2 text-sm leading-6 text-[#7f1d1d]">
                      Real-time monitoring, statistics visualization, threat logs, and network health metrics.
                    </p>
                  </div>
                </div>

                <div className="mt-6 flex flex-wrap gap-3">
                  {helperRoutes.map((route) => (
                    <span
                      key={route}
                      className="rounded-full border border-[#fecaca] bg-[#fef2f2] px-3 py-2 text-sm text-[#991b1b]"
                    >
                      {route}
                    </span>
                  ))}
                </div>
              </SpotlightCard>

              <SpotlightCard
                id="flow"
                className="rounded-[2.25rem] border-white/10 bg-white/86 p-6 text-[#450a0a]"
                spotlightColor="rgba(220, 38, 38, 0.16)"
              >
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.28em] text-[#dc2626]">
                      Threat Intelligence Flow
                    </p>
                    <h3 className="mt-3 text-2xl font-semibold">
                      Distributed detection with blockchain verification.
                    </h3>
                  </div>
                  <div className="rounded-2xl bg-[#fee2e2] p-3 text-[#dc2626]">
                    <Chrome className="size-6" />
                  </div>
                </div>

                <div className="mt-6 space-y-3">
                  {paymentFlow.map((item, index) => (
                    <SpotlightCard
                      key={item}
                      className="flex gap-4 rounded-[1.35rem] border border-[#fecaca] bg-[#fef2f2] px-4 py-4"
                      spotlightColor="rgba(220, 38, 38, 0.12)"
                    >
                      <div className="flex size-9 shrink-0 items-center justify-center rounded-full bg-[#dc2626] text-sm font-semibold text-white">
                        {index + 1}
                      </div>
                      <p className="text-sm leading-7 text-[#7f1d1d]">{item}</p>
                    </SpotlightCard>
                  ))}
                </div>
              </SpotlightCard>
            </div>
          </div>
        </section>

        <section id="build" className="mx-auto max-w-7xl px-6 py-20 lg:px-10">
          <div className="rounded-[2.5rem] border border-white/10 bg-white/5 p-6 backdrop-blur-xl sm:p-8">
            <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
              <SectionHeading
                eyebrow="Build"
                title="Install CyberShield and deploy your security node step by step."
                description="Everything you need: installation, node setup, ML detection, blockchain integration, dashboard access, and Docker deployment."
              />
              <div className="flex items-center gap-2">
                {resourceLinks.map((link) => (
                  <IconLink key={`${link.label}-build`} {...link} />
                ))}
              </div>
            </div>

            <div className="mt-12 grid gap-12 lg:grid-cols-[0.9fr_1.1fr]">
              <div className="space-y-4">
                {guideSteps.map((item) => (
                  <SpotlightCard
                    key={item.step}
                    className="rounded-[1.75rem] border-white/10 bg-white/86 p-5 text-[#450a0a]"
                    spotlightColor="rgba(220, 38, 38, 0.16)"
                  >
                    <div className="flex gap-4">
                      <div className="flex size-11 shrink-0 items-center justify-center rounded-full bg-[#dc2626] text-sm font-semibold text-white">
                        {item.step}
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold">{item.title}</h3>
                        <p className="mt-2 text-[15px] leading-7 text-[#7f1d1d]">
                          {item.description}
                        </p>
                        <p className="mt-3 text-sm leading-6 text-[#dc2626]">
                          {item.note}
                        </p>
                      </div>
                    </div>
                  </SpotlightCard>
                ))}
              </div>

              <div className="space-y-6">
                <CodePanel
                  label="Install"
                  title="Package installation"
                  code={installCode}
                />
                <CodePanel
                  label="CLI Commands"
                  title="Quick start guide"
                  code={quickStartCode}
                />
                <div className="grid gap-6 xl:grid-cols-2">
                  <CodePanel
                    label="Dashboard"
                    title="Web interface"
                    code={extensionCode}
                  />
                  <CodePanel
                    label="Docker"
                    title="Container deployment"
                    code={overrideCode}
                  />
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  )
}

export default App
