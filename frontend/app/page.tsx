export default function Home() {
  return (
    <main className="min-h-screen bg-[#07111f] text-white">

      {/* ================= NAVBAR ================= */}
      <nav className="sticky top-0 z-50 border-b border-white/10 bg-[#07111f]/90 backdrop-blur-xl">
        <div className="mx-auto flex h-20 max-w-[1500px] items-center justify-between px-8 lg:px-12">

          {/* Logo */}
          <a
            href="/"
            className="text-3xl font-bold tracking-tight"
          >
            <span className="text-sky-400">Inno</span>
            <span>Bridge</span>
            <span className="text-indigo-400">-AI</span>
          </a>

          {/* Navigation */}
          <div className="hidden items-center gap-10 lg:flex">

            <a
              href="#platform"
              className="text-base font-medium text-slate-300 transition hover:text-white"
            >
              Platform
            </a>

            <a
              href="#features"
              className="text-base font-medium text-slate-300 transition hover:text-white"
            >
              Features
            </a>

            <a
              href="#how-it-works"
              className="text-base font-medium text-slate-300 transition hover:text-white"
            >
              How It Works
            </a>

            <a
              href="#about"
              className="text-base font-medium text-slate-300 transition hover:text-white"
            >
              About
            </a>

          </div>

          {/* Auth buttons */}
          <div className="flex items-center gap-4">

            <a
              href="/login"
              className="rounded-xl px-5 py-3 text-base font-medium text-slate-200 transition hover:bg-white/10"
            >
              Login
            </a>

            <a
              href="/register"
              className="rounded-xl bg-sky-500 px-6 py-3 text-base font-semibold shadow-lg shadow-sky-500/20 transition hover:bg-sky-400"
            >
              Get Started
            </a>

          </div>

        </div>
      </nav>


      {/* ================= HERO ================= */}
      <section className="relative overflow-hidden">

        {/* Background glow */}
        <div className="pointer-events-none absolute left-[10%] top-20 h-[500px] w-[500px] rounded-full bg-sky-500/10 blur-[150px]" />

        <div className="pointer-events-none absolute right-[10%] top-32 h-[500px] w-[500px] rounded-full bg-indigo-500/10 blur-[150px]" />

        <div className="relative mx-auto grid min-h-[820px] max-w-[1500px] items-center gap-20 px-8 py-28 lg:grid-cols-2 lg:px-12">

          {/* LEFT SIDE */}
          <div>

            {/* Badge */}
            <div className="mb-8 inline-flex items-center gap-3 rounded-full border border-sky-400/20 bg-sky-400/10 px-5 py-3 text-base font-medium text-sky-300">

              <span className="h-2.5 w-2.5 rounded-full bg-sky-400 shadow-lg shadow-sky-400/50" />

              AI-Powered Innovation Intelligence

            </div>


            {/* Main heading */}
            <h1 className="max-w-3xl text-6xl font-bold leading-[1.05] tracking-tight sm:text-7xl lg:text-8xl">

              From

              <span className="block text-slate-100">
                Research
              </span>

              to

              <span className="block bg-gradient-to-r from-sky-400 via-cyan-300 to-indigo-400 bg-clip-text text-transparent">
                Real-World
              </span>

              <span className="block bg-gradient-to-r from-sky-400 via-cyan-300 to-indigo-400 bg-clip-text text-transparent">
                Innovation
              </span>

            </h1>


            {/* Description */}
            <p className="mt-9 max-w-2xl text-xl leading-9 text-slate-300">

              InnoBridge-AI brings research intelligence, patent intelligence,
              funding opportunities, innovation portfolios and AI-powered
              insights together in one intelligent platform.

            </p>


            {/* Buttons */}
            <div className="mt-11 flex flex-col gap-5 sm:flex-row">

              <a
                href="/register"
                className="rounded-xl bg-sky-500 px-9 py-5 text-center text-lg font-semibold shadow-xl shadow-sky-500/20 transition hover:bg-sky-400 hover:shadow-sky-400/20"
              >
                Start Your Innovation Journey →
              </a>

              <a
                href="#platform"
                className="rounded-xl border border-white/10 bg-white/[0.05] px-9 py-5 text-center text-lg font-semibold text-slate-100 transition hover:bg-white/[0.1]"
              >
                Explore Platform
              </a>

            </div>


            {/* Capability line */}
            <div className="mt-12 flex flex-wrap gap-x-7 gap-y-3 text-base text-slate-500">

              <span>Research Intelligence</span>

              <span>•</span>

              <span>Patent Intelligence</span>

              <span>•</span>

              <span>Funding Intelligence</span>

            </div>

          </div>


          {/* RIGHT SIDE — PRODUCT PREVIEW */}
          <div className="relative">

            <div className="rounded-[30px] border border-white/10 bg-white/[0.04] p-5 shadow-2xl shadow-black/40 backdrop-blur-xl">

              {/* Browser top */}
              <div className="flex items-center gap-3 border-b border-white/10 px-4 pb-5">

                <div className="h-3.5 w-3.5 rounded-full bg-red-400/80" />

                <div className="h-3.5 w-3.5 rounded-full bg-yellow-400/80" />

                <div className="h-3.5 w-3.5 rounded-full bg-green-400/80" />

                <div className="ml-4 flex-1 rounded-lg bg-white/[0.04] px-4 py-2 text-sm text-slate-600">
                  innobridge-ai.com
                </div>

              </div>


              {/* Dashboard */}
              <div className="space-y-5 p-5">

                {/* Header card */}
                <div className="rounded-2xl border border-white/10 bg-slate-900/80 p-6">

                  <div className="flex items-center justify-between">

                    <div>

                      <p className="text-sm text-slate-500">
                        Innovation Intelligence
                      </p>

                      <h3 className="mt-2 text-2xl font-semibold">
                        Welcome to InnoBridge-AI
                      </h3>

                    </div>

                    <div className="rounded-xl bg-sky-400/10 px-4 py-2 text-sm font-medium text-sky-300">
                      AI ACTIVE
                    </div>

                  </div>

                </div>


                {/* Three modules */}
                <div className="grid grid-cols-3 gap-4">

                  <PreviewCard
                    number="01"
                    title="Research"
                    text="Discover"
                  />

                  <PreviewCard
                    number="02"
                    title="Patents"
                    text="Analyze"
                  />

                  <PreviewCard
                    number="03"
                    title="Funding"
                    text="Connect"
                  />

                </div>


                {/* Pipeline */}
                <div className="rounded-2xl border border-white/10 bg-slate-900/80 p-6">

                  <div className="mb-7 flex items-center justify-between">

                    <span className="text-base font-medium text-slate-300">
                      Innovation Pipeline
                    </span>

                    <span className="text-sm font-medium text-sky-400">
                      AI Analysis
                    </span>

                  </div>


                  <div className="space-y-6">

                    <Pipeline
                      label="Research Discovery"
                      width="92%"
                    />

                    <Pipeline
                      label="Patent Intelligence"
                      width="78%"
                    />

                    <Pipeline
                      label="Funding Match"
                      width="86%"
                    />

                    <Pipeline
                      label="Commercialization"
                      width="64%"
                    />

                  </div>

                </div>

              </div>

            </div>


            {/* Floating confidence card */}
            <div className="absolute -bottom-8 -left-8 hidden rounded-2xl border border-white/10 bg-slate-900/95 p-6 shadow-2xl backdrop-blur-xl sm:block">

              <p className="text-sm text-slate-500">
                AI Match Confidence
              </p>

              <p className="mt-2 text-4xl font-bold text-sky-400">
                94%
              </p>

              <p className="mt-2 text-sm text-slate-500">
                Research → Funding
              </p>

            </div>

          </div>

        </div>

      </section>


      {/* ================= PLATFORM ================= */}
      <section
        id="platform"
        className="border-t border-white/10 px-8 py-32 lg:px-12"
      >

        <div className="mx-auto max-w-[1500px]">

          <div className="max-w-3xl">

            <p className="text-base font-semibold uppercase tracking-[0.2em] text-sky-400">
              One Connected Platform
            </p>

            <h2 className="mt-5 text-5xl font-bold leading-tight tracking-tight sm:text-6xl">
              Everything your innovation journey needs.
            </h2>

            <p className="mt-7 text-xl leading-9 text-slate-400">
              Discover knowledge, evaluate technology, find funding and move
              promising ideas toward real-world impact.
            </p>

          </div>


          <div
            id="features"
            className="mt-16 grid gap-7 md:grid-cols-2 lg:grid-cols-4"
          >

            <PlatformCard
              icon="01"
              title="Research Intelligence"
              description="Search papers, authors, institutions, trends and research gaps."
            />

            <PlatformCard
              icon="02"
              title="Patent Intelligence"
              description="Explore patents, similarities, timelines, analytics and AI insights."
            />

            <PlatformCard
              icon="03"
              title="Funding Intelligence"
              description="Discover grants, analyze opportunities, get recommendations and generate proposals."
            />

            <PlatformCard
              icon="04"
              title="Innovation Portfolio"
              description="Organize projects, research papers, patents and prototypes."
            />

          </div>

        </div>

      </section>


      {/* ================= HOW IT WORKS ================= */}
      <section
        id="how-it-works"
        className="border-t border-white/10 px-8 py-32 lg:px-12"
      >

        <div className="mx-auto max-w-[1500px]">

          <div className="text-center">

            <p className="text-base font-semibold uppercase tracking-[0.2em] text-indigo-400">
              How It Works
            </p>

            <h2 className="mt-5 text-5xl font-bold sm:text-6xl">
              From Idea to Impact
            </h2>

            <p className="mx-auto mt-6 max-w-3xl text-xl leading-9 text-slate-400">
              A connected workflow that helps innovators make better
              decisions at every stage.
            </p>

          </div>


          <div className="mt-16 grid gap-7 md:grid-cols-2 lg:grid-cols-4">

            <Workflow
              number="01"
              title="Discover"
              text="Find research, technologies and opportunities relevant to your idea."
            />

            <Workflow
              number="02"
              title="Analyze"
              text="Use AI and intelligence tools to evaluate research and patents."
            />

            <Workflow
              number="03"
              title="Connect"
              text="Find funding, collaborators, investors and industry opportunities."
            />

            <Workflow
              number="04"
              title="Innovate"
              text="Turn promising ideas into projects, products and real-world impact."
            />

          </div>

        </div>

      </section>


      {/* ================= CTA ================= */}
      <section
        id="about"
        className="border-t border-white/10 px-8 py-32 lg:px-12"
      >

        <div className="mx-auto max-w-[1200px] rounded-[35px] border border-sky-400/10 bg-gradient-to-br from-sky-400/10 via-transparent to-indigo-400/10 p-12 text-center sm:p-20">

          <p className="text-base font-semibold uppercase tracking-[0.2em] text-sky-400">
            Build the Future
          </p>

          <h2 className="mt-6 text-5xl font-bold leading-tight sm:text-6xl">
            Ready to build the next innovation?
          </h2>

          <p className="mx-auto mt-7 max-w-3xl text-xl leading-9 text-slate-400">
            Bring your research, ideas and opportunities together with
            InnoBridge-AI.
          </p>

          <a
            href="/register"
            className="mt-10 inline-block rounded-xl bg-sky-500 px-10 py-5 text-lg font-semibold shadow-xl shadow-sky-500/20 transition hover:bg-sky-400"
          >
            Get Started →
          </a>

        </div>

      </section>


      {/* ================= FOOTER ================= */}
      <footer className="border-t border-white/10 px-8 py-12 lg:px-12">

        <div className="mx-auto flex max-w-[1500px] flex-col items-center justify-between gap-6 text-base text-slate-500 sm:flex-row">

          <div className="text-lg">
            © 2026 <span className="text-slate-300">InnoBridge-AI</span>
          </div>

          <div className="flex flex-wrap justify-center gap-8">

            <span>Research</span>

            <span>Innovation</span>

            <span>Funding</span>

            <span>Technology</span>

          </div>

        </div>

      </footer>

    </main>
  );
}


/* =========================================================
   PREVIEW CARD
========================================================= */

function PreviewCard({
  number,
  title,
  text,
}: {
  number: string;
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5 transition hover:bg-white/[0.06]">

      <div className="text-sm font-semibold text-sky-400">
        {number}
      </div>

      <div className="mt-4 text-lg font-semibold">
        {title}
      </div>

      <div className="mt-2 text-sm text-slate-500">
        {text}
      </div>

    </div>
  );
}


/* =========================================================
   PIPELINE
========================================================= */

function Pipeline({
  label,
  width,
}: {
  label: string;
  width: string;
}) {
  return (
    <div>

      <div className="mb-3 flex items-center justify-between">

        <span className="text-sm text-slate-400">
          {label}
        </span>

        <span className="text-sm font-medium text-slate-500">
          {width}
        </span>

      </div>

      <div className="h-2.5 rounded-full bg-white/5">

        <div
          className="h-2.5 rounded-full bg-gradient-to-r from-sky-400 to-indigo-400"
          style={{ width }}
        />

      </div>

    </div>
  );
}


/* =========================================================
   PLATFORM CARD
========================================================= */

function PlatformCard({
  icon,
  title,
  description,
}: {
  icon: string;
  title: string;
  description: string;
}) {
  return (
    <div className="group rounded-3xl border border-white/10 bg-white/[0.03] p-9 transition duration-300 hover:-translate-y-2 hover:border-sky-400/30 hover:bg-white/[0.06]">

      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-sky-400/20 to-indigo-400/20 text-base font-bold text-sky-300">
        {icon}
      </div>

      <h3 className="mt-7 text-2xl font-semibold">
        {title}
      </h3>

      <p className="mt-4 text-base leading-8 text-slate-400">
        {description}
      </p>

    </div>
  );
}


/* =========================================================
   WORKFLOW
========================================================= */

function Workflow({
  number,
  title,
  text,
}: {
  number: string;
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-9 transition hover:border-indigo-400/30 hover:bg-white/[0.05]">

      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-400/10 text-base font-bold text-indigo-300">
        {number}
      </div>

      <h3 className="mt-7 text-2xl font-semibold">
        {title}
      </h3>

      <p className="mt-4 text-base leading-8 text-slate-400">
        {text}
      </p>

    </div>
  );
}