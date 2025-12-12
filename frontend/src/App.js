import React from "react";
import { BrowserRouter as Router, Routes, Route, Link, NavLink } from "react-router-dom";
import { Shield, CreditCard, GraduationCap, BadgeCheck, Moon, SunMedium, LayoutDashboard } from "lucide-react";

import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Badge } from "./components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "./components/ui/tabs";
import { Switch } from "./components/ui/switch";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Textarea } from "./components/ui/textarea";
import { Toaster } from "./components/ui/sonner";
import { toast } from "sonner";

// ---- Dark mode hook ----
function useTheme() {
  const [theme, setTheme] = React.useState(() => {
    if (typeof window === "undefined") return "light";
    return localStorage.getItem("secops-theme") || "light";
  });

  React.useEffect(() => {
    const root = window.document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
    localStorage.setItem("secops-theme", theme);
  }, [theme]);

  return { theme, setTheme };
}

// ---- Layout ----
function AppShell({ children }) {
  const { theme, setTheme } = useTheme();

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground">
      <header className="sticky top-0 z-40 border-b bg-background/80 backdrop-blur-md">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between gap-4">
          <Link to="/" className="flex items-center gap-2">
            <div className="h-9 w-9 rounded-xl bg-primary/10 flex items-center justify-center ring-soft">
              <Shield className="h-5 w-5 text-primary" />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-semibold tracking-tight">SecOps Studio</span>
              <span className="text-xs text-muted-foreground">Security tooling playground</span>
            </div>
          </Link>

          <nav className="hidden md:flex items-center gap-6 text-sm font-medium">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `transition-colors ${
                  isActive ? "text-foreground" : "text-muted-foreground hover:text-foreground"
                }`
              }
            >
              Overview
            </NavLink>
            <NavLink
              to="/cards"
              className={({ isActive }) =>
                `flex items-center gap-1 transition-colors ${
                  isActive ? "text-foreground" : "text-muted-foreground hover:text-foreground"
                }`
              }
            >
              <CreditCard className="h-3.5 w-3.5" /> Test Cards
            </NavLink>
            <NavLink
              to="/licenses"
              className={({ isActive }) =>
                `flex items-center gap-1 transition-colors ${
                  isActive ? "text-foreground" : "text-muted-foreground hover:text-foreground"
                }`
              }
            >
              <BadgeCheck className="h-3.5 w-3.5" /> Licenses
            </NavLink>
            <NavLink
              to="/training"
              className={({ isActive }) =>
                `flex items-center gap-1 transition-colors ${
                  isActive ? "text-foreground" : "text-muted-foreground hover:text-foreground"
                }`
              }
            >
              <GraduationCap className="h-3.5 w-3.5" /> Training Hub
            </NavLink>
          </nav>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 rounded-full bg-secondary/80 px-2 py-1 text-xs text-muted-foreground">
              <span className="inline-flex items-center gap-1">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                Mock only
              </span>
              <span className="h-3 w-px bg-border/60" />
              <span>PCI-safe test data</span>
            </div>
            <button
              type="button"
              aria-label="Toggle dark mode"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-border bg-background shadow-sm hover:bg-muted transition-colors"
            >
              {theme === "dark" ? (
                <SunMedium className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1">
        {children}
      </main>

      <footer className="border-t mt-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-muted-foreground">
          <span>
            SecOps Studio · Prototype UI · <span className="font-medium">All data is mocked / TEST ONLY</span>
          </span>
          <span>Built with React, Tailwind, and shadcn/ui</span>
        </div>
      </footer>
    </div>
  );
}

// ---- Landing Page ----
function LandingPage() {
  return (
    <div className="bg-hero-surface">
      <section className="max-w-6xl mx-auto px-4 sm:px-6 pt-10 pb-14 grid gap-10 lg:grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)] items-center">
        <div className="space-y-6">
          <Badge className="bg-primary/10 text-primary border-primary/20 rounded-full px-3 py-1 text-xs font-medium w-fit">
            Ocean-grade security sandbox · Mocked only
          </Badge>
          <div className="space-y-3">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-tight leading-tight">
              One studio for cards, licenses & security training.
            </h1>
            <p className="text-muted-foreground text-sm sm:text-base max-w-xl">
              SecOps Studio is a front-end prototype for security teams to explore test card generation, license tracking,
              and web security training dashboards—without touching real payment or licensing systems.
            </p>
          </div>

          <div className="flex flex-wrap gap-3 items-center">
            <Button asChild size="lg" className="rounded-full px-6">
              <Link to="/cards" className="flex items-center gap-2">
                <CreditCard className="h-4 w-4" />
                Open Test Card Lab
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="rounded-full border-dashed">
              <Link to="/training" className="flex items-center gap-2">
                <GraduationCap className="h-4 w-4" />
                Browse Training Hub
              </Link>
            </Button>
          </div>

          <dl className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs sm:text-sm">
            <div className="rounded-xl border bg-card/60 p-3 card-elevated flex flex-col">
              <dt className="text-muted-foreground">Test card brands</dt>
              <dd className="mt-1 font-semibold flex items-center gap-1">
                4
                <span className="text-[0.7rem] text-muted-foreground">Visa, MC, AmEx, Discover</span>
              </dd>
            </div>
            <div className="rounded-xl border bg-card/60 p-3 card-elevated flex flex-col">
              <dt className="text-muted-foreground">Licenses tracked</dt>
              <dd className="mt-1 font-semibold">15+ tools</dd>
            </div>
            <div className="rounded-xl border bg-card/60 p-3 card-elevated flex flex-col">
              <dt className="text-muted-foreground">Security modules</dt>
              <dd className="mt-1 font-semibold">OWASP-style catalog</dd>
            </div>
          </dl>
        </div>

        <div className="relative h-full">
          <div className="relative rounded-3xl card-glass border border-white/20 dark:border-white/5 overflow-hidden p-5 flex flex-col gap-4">
            <div className="flex items-center justify-between gap-3 mb-1">
              <div className="flex items-center gap-2">
                <span className="inline-flex h-7 w-7 rounded-xl bg-primary/10 items-center justify-center">
                  <LayoutDashboard className="h-4 w-4 text-primary" />
                </span>
                <div>
                  <p className="text-xs text-muted-foreground">Environment</p>
                  <p className="text-sm font-medium">SecOps sand-box</p>
                </div>
              </div>
              <Badge variant="outline" className="text-[0.65rem] uppercase tracking-wide bg-secondary/80">
                Mock only
              </Badge>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="rounded-2xl bg-primary/10 border border-primary/20 p-3 flex flex-col justify-between min-h-[96px]">
                <div className="flex items-center justify-between gap-1">
                  <span className="text-[0.7rem] text-primary font-medium">Test cards</span>
                  <CreditCard className="h-3.5 w-3.5 text-primary" />
                </div>
                <div className="mt-4">
                  <p className="text-[0.7rem] text-muted-foreground">Generated today</p>
                  <p className="text-lg font-semibold">128</p>
                </div>
              </div>
              <div className="rounded-2xl bg-accent/10 border border-accent/20 p-3 flex flex-col justify-between min-h-[96px]">
                <div className="flex items-center justify-between gap-1">
                  <span className="text-[0.7rem] text-accent-foreground font-medium">Licenses</span>
                  <BadgeCheck className="h-3.5 w-3.5 text-accent" />
                </div>
                <div className="mt-4">
                  <p className="text-[0.7rem] text-muted-foreground">Renewal this quarter</p>
                  <p className="text-lg font-semibold">6</p>
                </div>
              </div>
            </div>

            <div className="mt-1 rounded-2xl bg-secondary p-3 flex flex-col gap-2">
              <div className="flex items-center justify-between text-[0.7rem] text-muted-foreground">
                <span>Training completion</span>
                <span>Team · QA · Sec</span>
              </div>
              <div className="h-1.5 w-full rounded-full bg-muted overflow-hidden">
                <div className="h-full w-2/3 rounded-full bg-gradient-to-r from-primary to-accent" />
              </div>
              <div className="flex justify-between text-[0.7rem]">
                <span className="font-medium">66% overall</span>
                <span className="text-muted-foreground">OWASP focus</span>
              </div>
            </div>

            <div className="mt-1 rounded-2xl border border-dashed border-primary/30 bg-primary/5 px-3 py-2 text-[0.7rem] text-muted-foreground">
              This entire experience is a <span className="font-semibold text-primary">front-end prototype</span>. No
              real cards, payments, or license APIs are ever called.
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

// ---- Test Card Generator Page ----
function CardGeneratorPage() {
  const [bin, setBin] = React.useState("411111");
  const [length, setLength] = React.useState(16);
  const [brand, setBrand] = React.useState("visa");
  const [count, setCount] = React.useState(5);
  const [cards, setCards] = React.useState([]);

  const generateLuhn = (base) => {
    const digits = base.split("").map((d) => parseInt(d, 10));
    let sum = 0;
    for (let i = 0; i < digits.length; i += 1) {
      let digit = digits[digits.length - 1 - i];
      if (i % 2 === 0) {
        digit *= 2;
        if (digit > 9) digit -= 9;
      }
      sum += digit;
    }
    const check = (10 - (sum % 10)) % 10;
    return `${base}${check}`;
  };

  const handleGenerate = () => {
    const results = [];
    const numericLength = Number(length);
    const numericCount = Number(count);

    if (!bin || bin.length >= numericLength) {
      toast.error("BIN must be shorter than total card length.");
      return;
    }

    for (let i = 0; i < numericCount; i += 1) {
      const randomBodyLength = numericLength - bin.length - 1;
      let body = "";
      for (let j = 0; j < randomBodyLength; j += 1) {
        body += Math.floor(Math.random() * 10).toString();
      }
      const base = `${bin}${body}`;
      const number = generateLuhn(base);
      const expiryMonth = String(Math.floor(Math.random() * 12) + 1).padStart(2, "0");
      const expiryYear = String(new Date().getFullYear() + 2 + (i % 3)).slice(-2);
      const cvvLength = brand === "amex" ? 4 : 3;
      let cvv = "";
      for (let c = 0; c < cvvLength; c += 1) {
        cvv += Math.floor(Math.random() * 10).toString();
      }
      results.push({
        id: `${Date.now()}-${i}`,
        number,
        brand,
        expiry: `${expiryMonth}/${expiryYear}`,
        cvv,
      });
    }
    setCards(results);
    toast.success(`Generated ${results.length} test card${results.length === 1 ? "" : "s"}.`);
  };

  const exportAs = (format) => {
    if (!cards.length) {
      toast("Nothing to export yet. Generate some cards first.");
      return;
    }
    if (format === "json") {
      const blob = new Blob([JSON.stringify(cards, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "secops-test-cards.json";
      a.click();
      URL.revokeObjectURL(url);
      toast.success("Exported JSON file.");
    } else {
      const header = "number,brand,expiry,cvv";
      const rows = cards.map((c) => `${c.number},${c.brand},${c.expiry},${c.cvv}`);
      const csv = [header, ...rows].join("\n");
      const blob = new Blob([csv], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "secops-test-cards.csv";
      a.click();
      URL.revokeObjectURL(url);
      toast.success("Exported CSV file.");
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-10 space-y-8">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-2xl sm:text-3xl font-semibold tracking-tight flex items-center gap-2">
            <CreditCard className="h-6 w-6 text-primary" />
            Test Card Generator
          </h2>
          <p className="text-muted-foreground text-sm max-w-xl mt-2">
            Generate PCI-safe, <span className="font-medium">Luhn-valid</span> test cards with configurable BIN, length, and
            brand. All numbers are clearly marked as <span className="font-semibold">NON-PRODUCTION / TEST ONLY</span>.
          </p>
        </div>
        <Badge variant="outline" className="bg-secondary/70 text-[0.7rem] uppercase tracking-wide">
          Sandbox · No real payments
        </Badge>
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,1.2fr)] items-start">
        <Card className="card-elevated">
          <CardHeader>
            <CardTitle className="text-base">Generation parameters</CardTitle>
            <CardDescription>Configure how your mock test cards should look.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label htmlFor="brand">Brand</Label>
                <select
                  id="brand"
                  value={brand}
                  onChange={(e) => setBrand(e.target.value)}
                  className="inline-flex h-9 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-1 text-sm text-foreground shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
                >
                  <option value="visa">Visa</option>
                  <option value="mc">Mastercard</option>
                  <option value="amex">American Express</option>
                  <option value="discover">Discover</option>
                </select>
                <p className="text-[0.7rem] text-muted-foreground">Used to adjust CVV length only.</p>
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="bin">BIN (Issuer prefix)</Label>
                <Input
                  id="bin"
                  value={bin}
                  maxLength={10}
                  onChange={(e) => setBin(e.target.value.replace(/[^0-9]/g, ""))}
                  placeholder="e.g. 411111"
                />
                <p className="text-[0.7rem] text-muted-foreground">Digits the card should start with.</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label htmlFor="length">Card length</Label>
                <Input
                  id="length"
                  type="number"
                  min={12}
                  max={19}
                  value={length}
                  onChange={(e) => setLength(e.target.value)}
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="count">How many</Label>
                <Input
                  id="count"
                  type="number"
                  min={1}
                  max={50}
                  value={count}
                  onChange={(e) => setCount(e.target.value)}
                />
              </div>
            </div>

            <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t">
              <div className="text-[0.7rem] text-muted-foreground max-w-xs">
                Numbers are generated with the <span className="font-medium">Luhn algorithm</span> for format validity only.
                They are <span className="font-semibold text-destructive">not linked</span> to any real account.
              </div>
              <Button onClick={handleGenerate} size="sm" className="px-4 rounded-full">
                Generate cards
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card className="card-elevated flex flex-col min-h-[260px]">
          <CardHeader className="flex flex-row items-center justify-between gap-4">
            <div>
              <CardTitle className="text-base">Mock output</CardTitle>
              <CardDescription>Preview and export your test set.</CardDescription>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" className="rounded-full" onClick={() => exportAs("csv")}>
                CSV
              </Button>
              <Button variant="outline" size="sm" className="rounded-full" onClick={() => exportAs("json")}>
                JSON
              </Button>
            </div>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col gap-2 max-h-[300px] overflow-y-auto">
            {!cards.length && (
              <div className="flex flex-col items-center justify-center py-10 text-center text-sm text-muted-foreground">
                <CreditCard className="h-8 w-8 mb-2 text-muted-foreground/70" />
                <p>No test cards yet. Configure parameters and generate a batch.</p>
              </div>
            )}
            <div className="space-y-2">
              {cards.map((c) => (
                <div
                  key={c.id}
                  className="flex flex-col sm:flex-row sm:items-center gap-2 rounded-xl border bg-card px-3 py-2 text-xs sm:text-sm"
                >
                  <div className="font-mono flex-1 truncate">{c.number}</div>
                  <div className="flex flex-wrap gap-2 items-center">
                    <Badge variant="outline" className="text-[0.65rem] uppercase">
                      {c.brand}
                    </Badge>
                    <span className="text-[0.7rem] text-muted-foreground">Exp {c.expiry}</span>
                    <span className="text-[0.7rem] text-muted-foreground">CVV {c.cvv}</span>
                    <Badge variant="destructive" className="text-[0.65rem] uppercase tracking-wide">
                      Test only
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// ---- License Manager Page ----
function LicenseManagerPage() {
  const [note, setNote] = React.useState("");
  const [licenses] = React.useState([
    {
      id: 1,
      product: "PortSwigger Burp Suite Pro",
      vendor: "PortSwigger",
      seats: 5,
      costPerYear: 399,
      team: "AppSec",
      renewal: "2025-03-12",
      status: "active",
    },
    {
      id: 2,
      product: "JetBrains All Products Pack",
      vendor: "JetBrains",
      seats: 10,
      costPerYear: 649,
      team: "Engineering",
      renewal: "2025-01-02",
      status: "expiring",
    },
    {
      id: 3,
      product: "Atlassian Jira Cloud Premium",
      vendor: "Atlassian",
      seats: 50,
      costPerYear: 1020,
      team: "Org-wide",
      renewal: "2024-12-01",
      status: "active",
    },
  ]);

  const totalSpend = licenses.reduce((sum, l) => sum + l.costPerYear, 0);

  const saveNote = () => {
    toast.success("Mock note saved in local UI state.");
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-10 space-y-8">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-2xl sm:text-3xl font-semibold tracking-tight flex items-center gap-2">
            <BadgeCheck className="h-6 w-6 text-primary" />
            License & Subscription Manager
          </h2>
          <p className="text-muted-foreground text-sm max-w-xl mt-2">
            Track legitimate tooling like Burp Suite Pro, IDEs, and collaboration platforms. This is a visual prototype only—
            no live billing or vendor APIs.
          </p>
        </div>
        <div className="flex flex-col items-end gap-2 text-xs">
          <div className="rounded-full bg-secondary px-3 py-1 text-muted-foreground">
            Upcoming renewals this quarter: <span className="font-semibold">2</span>
          </div>
          <span className="text-muted-foreground">Annual mock spend: ${totalSpend.toLocaleString()}</span>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.3fr)_minmax(0,1fr)] items-start">
        <Card className="card-elevated">
          <CardHeader>
            <CardTitle className="text-base">Portfolio</CardTitle>
            <CardDescription>Representative sample of tools an AppSec/Eng org might track.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {licenses.map((lic) => (
              <div
                key={lic.id}
                className="flex flex-col md:flex-row md:items-center gap-2 rounded-xl border bg-card px-3 py-2 text-xs sm:text-sm"
              >
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{lic.product}</p>
                  <p className="text-muted-foreground text-[0.7rem]">
                    {lic.vendor} · Team: {lic.team} · Seats: {lic.seats}
                  </p>
                </div>
                <div className="flex flex-wrap items-center gap-2 justify-between md:justify-end">
                  <span className="text-[0.75rem] font-mono text-muted-foreground">
                    ${lic.costPerYear.toLocaleString()}/yr
                  </span>
                  <span className="text-[0.7rem] text-muted-foreground">
                    Renewal {new Date(lic.renewal).toLocaleDateString()}
                  </span>
                  <Badge
                    variant={lic.status === "expiring" ? "destructive" : "outline"}
                    className="text-[0.65rem] uppercase tracking-wide"
                  >
                    {lic.status === "expiring" ? "Renew soon" : "Active"}
                  </Badge>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="card-elevated flex flex-col">
          <CardHeader>
            <CardTitle className="text-base">Renewal notes (mock)</CardTitle>
            <CardDescription>
              Jot down negotiation or budgeting notes. This is stored only in local UI state and disappears on refresh.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col gap-3">
            <Textarea
              rows={6}
              placeholder="e.g. Consolidate Burp licenses under AppSec; review seat usage before renewal; align JetBrains plan with headcount forecast…"
              value={note}
              onChange={(e) => setNote(e.target.value)}
            />
            <div className="flex justify-end">
              <Button size="sm" className="rounded-full px-4" onClick={saveNote}>
                Save note (mock)
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// ---- Training Hub Page ----
function TrainingHubPage() {
  const [activeTrack, setActiveTrack] = React.useState("owasp");

  const modules = [
    { id: 1, title: "XSS fundamentals", difficulty: "Beginner", track: "owasp", progress: 100 },
    { id: 2, title: "SQL injection (PortSwigger lab style)", difficulty: "Intermediate", track: "owasp", progress: 60 },
    { id: 3, title: "SSRF & modern defenses", difficulty: "Advanced", track: "cloud", progress: 20 },
    { id: 4, title: "Authentication pitfalls", difficulty: "Intermediate", track: "owasp", progress: 40 },
    { id: 5, title: "Secure SDLC for feature teams", difficulty: "Beginner", track: "process", progress: 80 },
  ];

  const filtered = modules.filter((m) => (activeTrack === "all" ? true : m.track === activeTrack));

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-10 space-y-8">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-2xl sm:text-3xl font-semibold tracking-tight flex items-center gap-2">
            <GraduationCap className="h-6 w-6 text-primary" />
            Web Security Training Hub
          </h2>
          <p className="text-muted-foreground text-sm max-w-xl mt-2">
            Inspired by OWASP and PortSwigger style labs. Mix and match tracks to design a security curriculum for your
            team—this UI is fully mocked, no external content is pulled in.
          </p>
        </div>
        <div className="text-xs text-muted-foreground">Progress and streaks are local to this browser tab.</div>
      </div>

      <Tabs value={activeTrack} onValueChange={setActiveTrack} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4 max-w-lg">
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="owasp">OWASP Top 10</TabsTrigger>
          <TabsTrigger value="cloud">Cloud & SSRF</TabsTrigger>
          <TabsTrigger value="process">Process & SDLC</TabsTrigger>
        </TabsList>

        <TabsContent value={activeTrack} className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filtered.map((m) => (
              <Card key={m.id} className="flex flex-col card-elevated min-h-[180px]">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between gap-2">
                    <CardTitle className="text-sm line-clamp-2">{m.title}</CardTitle>
                    <Badge variant="outline" className="text-[0.65rem] uppercase tracking-wide">
                      {m.difficulty}
                    </Badge>
                  </div>
                  <CardDescription className="mt-1 text-[0.7rem]">
                    Track: {m.track === "owasp" ? "OWASP" : m.track === "cloud" ? "Cloud/SSRF" : "Process"}
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex flex-col flex-1 pt-0">
                  <div className="mb-3 space-y-1">
                    <div className="flex items-center justify-between text-[0.7rem] text-muted-foreground">
                      <span>Completion</span>
                      <span>{m.progress}%</span>
                    </div>
                    <div className="h-1.5 w-full rounded-full bg-muted overflow-hidden">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-primary to-accent"
                        style={{ width: `${m.progress}%` }}
                      />
                    </div>
                  </div>
                  <div className="mt-auto pt-2 border-t flex items-center justify-between gap-2">
                    <span className="text-[0.7rem] text-muted-foreground">
                      {m.progress === 100 ? "Completed" : m.progress > 0 ? "In progress" : "Not started"}
                    </span>
                    <Button size="sm" variant={m.progress ? "outline" : "default"} className="rounded-full px-3">
                      {m.progress ? "Review module" : "Start module"}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

// ---- Root App with Router ----
function App() {
  return (
    <Router>
      <AppShell>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/cards" element={<CardGeneratorPage />} />
          <Route path="/licenses" element={<LicenseManagerPage />} />
          <Route path="/training" element={<TrainingHubPage />} />
        </Routes>
        <Toaster position="top-center" richColors closeButton />
      </AppShell>
    </Router>
  );
}

export default App;
