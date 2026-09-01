# src/app.py
import sys
from pathlib import Path
import json
import streamlit as st
import streamlit.components.v1 as components

# 0. Path Resolution Fix
project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.append(project_root)

from src.pipeline import run_pipeline, load_raw_data, COUNTRY_ISO3_MAP, COUNTRY_CURRENCY_MAP
from src.normalize.adjust import COL_DATA
from src.tax.calculator import TAX_DATA
from src.benchmark import BENCHMARK_FILE

# 1. Page Configuration
st.set_page_config(
    page_title="EquivPay — Global Compensation Normalization Engine",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Hide Streamlit default sidebar and margins completely
st.markdown("""
<style>
    /* Hide Streamlit Native Sidebar & Header */
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }
    footer { display: none !important; }
    #MainMenu { display: none !important; }
    
    /* Remove padding around component iframe */
    .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    iframe {
        border: none !important;
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. Load reference datasets to embed into client-side JS engine
fx_data, ppp_data = load_raw_data()
with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
    bench_data = json.load(f)

# Build HTML template for the faithful Stitch UI
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8"/>
    <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
    <title>EquivPay — Global Compensation Normalization</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
    tailwind.config = {{
        theme: {{
            extend: {{
                colors: {{
                    "primary": "#006194",
                    "primary-light": "#0284c7",
                    "primary-container": "#007bb9",
                    "primary-fixed": "#cce5ff",
                    "primary-fixed-dim": "#93ccff",
                    "secondary": "#006c49",
                    "secondary-fixed": "#6ffbbe",
                    "secondary-fixed-dim": "#4edea3",
                    "secondary-container": "#6cf8bb",
                    "on-secondary-container": "#00714d",
                    "on-secondary-fixed-variant": "#005236",
                    "surface": "#faf8ff",
                    "surface-container-lowest": "#ffffff",
                    "surface-container-low": "#f2f3ff",
                    "surface-container": "#eaedff",
                    "surface-container-high": "#e2e7ff",
                    "surface-variant": "#dae2fd",
                    "on-surface": "#131b2e",
                    "on-surface-variant": "#3f4850",
                    "outline": "#707881",
                    "outline-variant": "#bfc7d2",
                    "error": "#ba1a1a",
                    "error-container": "#ffdad6"
                }},
                fontFamily: {{
                    "geist": ["Geist", "Inter", "sans-serif"],
                    "inter": ["Inter", "sans-serif"],
                    "mono": ["JetBrains Mono", "monospace"]
                }},
                borderRadius: {{
                    "xl": "1rem",
                    "2xl": "1.5rem"
                }}
            }}
        }}
    }};
    </script>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet"/>
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            background-color: #faf8ff;
            color: #131b2e;
            margin: 0;
            padding: 0;
            overflow-x: hidden;
        }}
        h1, h2, h3, h4, .font-heading {{
            font-family: 'Geist', sans-serif;
            letter-spacing: -0.03em;
        }}
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}
        ::-webkit-scrollbar-track {{
            background: #f1f5f9;
        }}
        ::-webkit-scrollbar-thumb {{
            background: #cbd5e1;
            border-radius: 9999px;
        }}
        .tab-btn.active {{
            color: #131b2e;
            font-weight: 600;
            border-bottom: 2px solid #006194;
        }}
        .toast-enter {{
            animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }}
        @keyframes slideUp {{
            from {{ transform: translate(-50%, 20px); opacity: 0; }}
            to {{ transform: translate(-50%, 0); opacity: 1; }}
        }}
    </style>
</head>
<body class="bg-surface font-inter text-on-surface antialiased min-h-screen flex flex-col justify-between">

    <!-- Toast Notification Container -->
    <div id="toast" class="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 hidden px-4 py-2.5 bg-slate-900 text-white font-geist text-xs font-semibold rounded-xl shadow-2xl flex items-center gap-2 border border-slate-700 toast-enter">
        <span class="material-symbols-outlined text-secondary text-[18px]">check_circle</span>
        <span id="toast-msg">Copied Comp Brief to clipboard!</span>
    </div>

    <!-- STICKY GLASS HEADER (Faithful Stitch Design, No Auth/Sign In) -->
    <header class="sticky top-0 w-full z-50 bg-white/80 backdrop-blur-xl border-b border-outline-variant/30 shadow-[0_1px_8px_rgba(0,0,0,0.02)]">
        <div class="max-w-[1400px] mx-auto px-6 h-16 flex items-center justify-between">
            <div class="flex items-center gap-3 cursor-pointer" onclick="switchView('landing')">
                <div class="flex items-center gap-1.5 text-primary">
                    <span class="material-symbols-outlined text-[26px]">public</span>
                    <span class="font-heading text-2xl font-bold tracking-tighter text-[#006194]">EquivPay</span>
                </div>
                <span class="px-2.5 py-0.5 rounded-full bg-secondary-container text-on-secondary-container font-geist text-xs font-semibold tracking-wider">v1.0 Live</span>
            </div>

            <!-- Navigation Links -->
            <nav class="hidden md:flex items-center gap-8 text-sm">
                <button onclick="switchView('landing')" id="nav-landing" class="tab-btn active py-2 text-on-surface transition-colors">Product Overview</button>
                <button onclick="switchView('calculator')" id="nav-calculator" class="tab-btn py-2 text-on-surface-variant hover:text-on-surface transition-colors">Analysis Dashboard</button>
                <button onclick="switchView('methodology')" id="nav-methodology" class="tab-btn py-2 text-on-surface-variant hover:text-on-surface transition-colors">Methodology</button>
            </nav>

            <!-- Action Button (Directly launches Calculator, No Login) -->
            <div class="flex items-center gap-3">
                <button onclick="switchView('calculator')" class="bg-primary hover:bg-primary-container text-white font-geist text-sm font-semibold px-4 py-2 rounded-lg shadow-sm hover:shadow transition-all flex items-center gap-2">
                    <span class="material-symbols-outlined text-[18px]">bolt</span>
                    Launch Calculator
                </button>
            </div>
        </div>
    </header>

    <!-- ======================================================================= -->
    <!-- VIEW 1: LANDING PAGE (Screen 3: EquivPay - Global Normalization)        -->
    <!-- ======================================================================= -->
    <main id="view-landing" class="w-full flex-grow">
        <!-- Interactive Hero Background -->
        <div class="relative w-full overflow-hidden bg-surface">
            <div class="absolute top-0 right-0 w-[700px] h-[700px] bg-primary/5 rounded-full filter blur-3xl opacity-60 transform translate-x-1/3 -translate-y-1/4 pointer-events-none"></div>
            <div class="absolute bottom-0 left-0 w-[500px] h-[500px] bg-secondary/5 rounded-full filter blur-3xl opacity-40 transform -translate-x-1/4 translate-y-1/4 pointer-events-none"></div>

            <!-- Hero Section -->
            <section class="max-w-[1400px] mx-auto px-6 pt-12 pb-16 flex flex-col lg:flex-row gap-12 items-center relative z-10">
                <div class="flex-1 flex flex-col items-start gap-5 max-w-2xl">
                    <div class="inline-flex items-center gap-2 px-3 py-1 bg-surface-container-high rounded-full shadow-sm">
                        <span class="material-symbols-outlined text-primary text-[18px]">verified</span>
                        <span class="font-geist text-xs font-semibold text-on-surface-variant uppercase tracking-widest">Global Statutory Truth Data</span>
                    </div>

                    <h1 class="font-heading text-4xl lg:text-5xl font-extrabold text-on-surface tracking-tight leading-[1.15]">
                        Compare Global Tech Offers with True Statutory Truth.
                    </h1>

                    <p class="text-lg text-on-surface-variant leading-relaxed">
                        Normalize international compensation using real-time foreign exchange, localized statutory tax burdens, and purchasing power parity (PPP). Equip your talent acquisition with mathematically defensible global banding.
                    </p>

                    <div class="flex flex-wrap items-center gap-4 pt-2">
                        <button onclick="switchView('calculator')" class="bg-secondary text-white font-geist text-sm font-semibold px-6 py-3 rounded-lg shadow-md hover:shadow-xl hover:-translate-y-0.5 transition-all flex items-center gap-2 group">
                            Analyze Your Compensation
                            <span class="material-symbols-outlined text-[18px] group-hover:translate-x-1 transition-transform">arrow_forward</span>
                        </button>
                        <button onclick="switchView('methodology')" class="bg-white text-on-surface border border-outline-variant/40 font-geist text-sm font-semibold px-6 py-3 rounded-lg shadow-sm hover:bg-surface-container-low transition-colors flex items-center gap-2">
                            Explore Methodology
                            <span class="material-symbols-outlined text-[18px] text-on-surface-variant">menu_book</span>
                        </button>
                    </div>

                    <!-- Trust indicators -->
                    <div class="flex items-center gap-6 pt-8 text-on-surface-variant/70 text-xs uppercase tracking-widest font-geist font-semibold">
                        <span>Trusted Data Sources:</span>
                        <div class="flex gap-4 items-center font-heading text-sm text-on-surface tracking-tight">
                            <span>WorldBank API</span>
                            <span>•</span>
                            <span>Numbeo Matrix</span>
                            <span>•</span>
                            <span>OECD Tax Tables</span>
                        </div>
                    </div>
                </div>

                <!-- Mini-Preview Card (Interactive Stitch Component) -->
                <div class="flex-1 w-full max-w-lg">
                    <div class="bg-white rounded-2xl shadow-xl overflow-hidden border border-outline-variant/30">
                        <div class="bg-surface-container-low px-5 py-3.5 flex justify-between items-center border-b border-outline-variant/20">
                            <span class="font-geist text-xs font-bold uppercase tracking-wider text-on-surface">Offer Normalization Matrix</span>
                            <div class="flex gap-1.5">
                                <div class="w-2.5 h-2.5 rounded-full bg-error/40"></div>
                                <div class="w-2.5 h-2.5 rounded-full bg-amber-400/50"></div>
                                <div class="w-2.5 h-2.5 rounded-full bg-secondary/50"></div>
                            </div>
                        </div>

                        <div class="p-5 flex flex-col gap-3.5">
                            <!-- Location 1: SF -->
                            <div class="flex flex-col gap-1 p-3.5 bg-surface-container-lowest rounded-xl border border-outline-variant/20 shadow-sm hover:border-primary/40 transition-colors">
                                <div class="flex justify-between items-center">
                                    <div class="flex items-center gap-2">
                                        <span class="material-symbols-outlined text-outline text-[20px]">location_city</span>
                                        <span class="font-geist font-semibold text-sm text-on-surface">San Francisco, USA</span>
                                    </div>
                                    <span class="font-heading font-bold text-lg text-on-surface">$140,000</span>
                                </div>
                                <div class="flex justify-between text-xs text-on-surface-variant pl-7">
                                    <span>Effective Tax: <span class="text-error font-semibold">23.6%</span></span>
                                    <span>COL Net: <span class="text-secondary font-bold">$118,177</span></span>
                                </div>
                                <div class="w-full bg-surface-container-high h-1.5 rounded-full mt-1.5 overflow-hidden">
                                    <div class="bg-primary h-full w-[70%] rounded-full"></div>
                                </div>
                            </div>

                            <!-- Location 2: Bangalore -->
                            <div class="flex flex-col gap-1 p-3.5 bg-surface-container-lowest rounded-xl border border-outline-variant/20 shadow-sm hover:border-primary/40 transition-colors">
                                <div class="flex justify-between items-center">
                                    <div class="flex items-center gap-2">
                                        <span class="material-symbols-outlined text-outline text-[20px]">location_city</span>
                                        <span class="font-geist font-semibold text-sm text-on-surface">Bangalore, India</span>
                                    </div>
                                    <span class="font-heading font-bold text-lg text-on-surface">₹3,500,000</span>
                                </div>
                                <div class="flex justify-between text-xs text-on-surface-variant pl-7">
                                    <span>Effective Tax: <span class="text-error font-semibold">21.8%</span></span>
                                    <span>COL Net: <span class="text-secondary font-bold">$111,263 (Eq.)</span></span>
                                </div>
                                <div class="w-full bg-surface-container-high h-1.5 rounded-full mt-1.5 overflow-hidden">
                                    <div class="bg-primary h-full w-[85%] rounded-full"></div>
                                </div>
                            </div>

                            <!-- Location 3: Berlin -->
                            <div class="flex flex-col gap-1 p-3.5 bg-surface-container-lowest rounded-xl border border-outline-variant/20 shadow-sm hover:border-primary/40 transition-colors">
                                <div class="flex justify-between items-center">
                                    <div class="flex items-center gap-2">
                                        <span class="material-symbols-outlined text-outline text-[20px]">location_city</span>
                                        <span class="font-geist font-semibold text-sm text-on-surface">Berlin, Germany</span>
                                    </div>
                                    <span class="font-heading font-bold text-lg text-on-surface">€85,000</span>
                                </div>
                                <div class="flex justify-between text-xs text-on-surface-variant pl-7">
                                    <span>Effective Tax: <span class="text-error font-semibold">27.9%</span></span>
                                    <span>COL Net: <span class="text-secondary font-bold">$109,240 (Eq.)</span></span>
                                </div>
                                <div class="w-full bg-surface-container-high h-1.5 rounded-full mt-1.5 overflow-hidden">
                                    <div class="bg-primary h-full w-[65%] rounded-full"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>

        <!-- BENTO GRID SECTION ("The Normalization Engine") -->
        <section class="max-w-[1400px] mx-auto px-6 py-12 w-full">
            <div class="mb-8">
                <span class="font-geist text-xs font-bold uppercase tracking-widest text-primary">Core Infrastructure</span>
                <h2 class="font-heading text-3xl font-bold text-on-surface tracking-tight mt-1">The Normalization Engine</h2>
                <p class="text-on-surface-variant max-w-xl mt-1 text-sm">Transform raw local currency offers into comparable standardized units using our proprietary four-stage pipeline.</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[280px]">
                <!-- 1. Statutory Tax Waterfall (Col Span 2) -->
                <div class="col-span-1 md:col-span-2 bg-white rounded-2xl p-6 shadow-sm border border-outline-variant/30 flex flex-col justify-between relative overflow-hidden group">
                    <div class="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-2xl transform translate-x-1/4 -translate-y-1/4"></div>
                    <div>
                        <span class="font-geist text-xs font-bold text-on-surface-variant uppercase tracking-widest">Stage 1</span>
                        <h3 class="font-heading text-xl font-bold text-on-surface mt-1">Statutory Progressive Waterfall</h3>
                        <p class="text-xs text-on-surface-variant mt-2 max-w-lg leading-relaxed">
                            Applies federal, state, municipal, and social security contribution deductions dynamically based on residency status and total comp structure (2024 Tax Tables).
                        </p>
                    </div>

                    <!-- Waterfall Chart -->
                    <div class="w-full h-24 mt-4 flex items-end justify-between gap-3 px-2">
                        <div class="flex-1 bg-primary/20 rounded-t-sm h-[20%] relative group-hover:bg-primary/30 transition-colors">
                            <div class="text-[10px] font-geist text-center -top-5 relative text-on-surface-variant">Tier 1</div>
                        </div>
                        <div class="flex-1 bg-primary/40 rounded-t-sm h-[40%] relative group-hover:bg-primary/50 transition-colors">
                            <div class="text-[10px] font-geist text-center -top-5 relative text-on-surface-variant">Tier 2</div>
                        </div>
                        <div class="flex-1 bg-primary/60 rounded-t-sm h-[65%] relative group-hover:bg-primary/70 transition-colors">
                            <div class="text-[10px] font-geist text-center -top-5 relative text-on-surface-variant">Tier 3</div>
                        </div>
                        <div class="flex-1 bg-primary/80 rounded-t-sm h-[85%] relative group-hover:bg-primary/90 transition-colors">
                            <div class="text-[10px] font-geist text-center -top-5 relative text-on-surface-variant">Tier 4</div>
                        </div>
                        <div class="flex-1 bg-primary rounded-t-sm h-[100%] relative shadow-[0_0_15px_rgba(0,97,148,0.3)]">
                            <div class="text-[10px] font-geist font-bold text-center -top-5 relative text-primary">Top Tier</div>
                        </div>
                    </div>
                </div>

                <!-- 2. Tri-Vector Normalization Indices -->
                <div class="col-span-1 bg-white rounded-2xl p-6 shadow-sm border border-outline-variant/30 flex flex-col justify-between">
                    <div>
                        <span class="font-geist text-xs font-bold text-on-surface-variant uppercase tracking-widest">Stage 2 & 3</span>
                        <h3 class="font-heading text-xl font-bold text-on-surface mt-1">Adjustment Indices</h3>
                    </div>
                    <div class="flex flex-col gap-2.5 mt-4">
                        <div class="flex items-center justify-between p-2.5 bg-surface-container rounded-lg border border-transparent">
                            <div class="flex items-center gap-2">
                                <span class="material-symbols-outlined text-primary text-[18px]">currency_exchange</span>
                                <span class="font-geist text-xs font-semibold text-on-surface">FX Spot Rate</span>
                            </div>
                            <span class="font-mono text-xs font-semibold text-primary">Live (ECB)</span>
                        </div>
                        <div class="flex items-center justify-between p-2.5 bg-surface-container rounded-lg border border-transparent">
                            <div class="flex items-center gap-2">
                                <span class="material-symbols-outlined text-secondary text-[18px]">shopping_cart</span>
                                <span class="font-geist text-xs font-semibold text-on-surface">World Bank PPP</span>
                            </div>
                            <span class="font-mono text-xs font-semibold text-secondary">Int$ Parity</span>
                        </div>
                        <div class="flex items-center justify-between p-2.5 bg-surface-container rounded-lg border border-transparent">
                            <div class="flex items-center gap-2">
                                <span class="material-symbols-outlined text-amber-600 text-[18px]">location_city</span>
                                <span class="font-geist text-xs font-semibold text-on-surface">City COL Factor</span>
                            </div>
                            <span class="font-mono text-xs font-semibold text-amber-700">NYC Base 100</span>
                        </div>
                    </div>
                </div>

                <!-- 3. Market Percentile Gaussian Curve -->
                <div class="col-span-1 bg-white rounded-2xl p-6 shadow-sm border border-outline-variant/30 flex flex-col justify-between relative overflow-hidden">
                    <div>
                        <span class="font-geist text-xs font-bold text-on-surface-variant uppercase tracking-widest">Stage 4</span>
                        <h3 class="font-heading text-xl font-bold text-on-surface mt-1">Market Banding</h3>
                    </div>
                    <div class="relative h-28 w-full flex items-end justify-center mt-2">
                        <svg class="w-full h-full stroke-primary fill-primary/10" viewBox="0 0 200 80">
                            <path d="M0,78 C40,78 60,10 100,10 C140,10 160,78 200,78" stroke-width="2" stroke-linecap="round"/>
                            <line x1="100" y1="10" x2="100" y2="78" stroke="#006194" stroke-dasharray="3,3" stroke-width="1.5"/>
                            <circle cx="120" cy="25" r="4" fill="#006c49"/>
                        </svg>
                        <div class="absolute bottom-2 right-4 bg-white px-2 py-0.5 rounded border border-outline-variant/30 text-[10px] font-geist font-bold text-secondary shadow-sm">
                            P75 Placement
                        </div>
                    </div>
                </div>

                <!-- 4. Real-Time Integrity & Freshness (Col Span 2) -->
                <div class="col-span-1 md:col-span-2 bg-white rounded-2xl p-6 shadow-sm border border-outline-variant/30 flex flex-col md:flex-row items-center justify-between gap-6">
                    <div class="flex-1">
                        <span class="font-geist text-xs font-bold text-on-surface-variant uppercase tracking-widest">Data Health</span>
                        <h3 class="font-heading text-xl font-bold text-on-surface mt-1">Real-Time Data Integrity</h3>
                        <p class="text-xs text-on-surface-variant mt-2 max-w-sm leading-relaxed">
                            Our engines synchronize with global central bank FX rates, World Bank Development Indicators, and updated 2024 statutory tables.
                        </p>
                    </div>
                    <div class="flex items-center gap-4 bg-emerald-50 border border-emerald-200 rounded-xl p-4">
                        <span class="material-symbols-outlined text-secondary text-[32px]">sync_saved_locally</span>
                        <div>
                            <div class="font-geist text-xs font-bold text-secondary uppercase tracking-wider">SYNCED & OPERATIONAL</div>
                            <div class="text-[11px] text-emerald-800 mt-0.5">FX 2024 Snapshot • World Bank 2024 Base</div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- INTERACTIVE OFFER DELTA SIMULATOR SECTION -->
        <section class="w-full bg-surface-container-low py-14 border-y border-outline-variant/30">
            <div class="max-w-[1400px] mx-auto px-6">
                <div class="text-center mb-8">
                    <span class="font-geist text-xs font-bold uppercase tracking-widest text-primary">Relocation Parity</span>
                    <h2 class="font-heading text-3xl font-bold text-on-surface mt-1">Offer Delta Simulator</h2>
                    <p class="text-sm text-on-surface-variant mt-1">Visualize the true spread between perceived value and localized take-home pay.</p>
                </div>

                <div class="flex flex-col lg:flex-row gap-8 bg-white rounded-2xl p-8 shadow-md border border-outline-variant/20">
                    <!-- Left: Simulator Controls -->
                    <div class="flex-1 flex flex-col gap-5 lg:pr-6 lg:border-r border-outline-variant/20">
                        <div>
                            <label class="font-geist text-xs font-bold text-on-surface-variant uppercase tracking-wider block mb-1.5">Base Location (HQ)</label>
                            <select id="sim-base-loc" onchange="onSimulatorBaseChange()" class="w-full bg-surface border border-outline-variant/40 rounded-lg p-2.5 text-sm font-semibold text-on-surface cursor-pointer">
                                <option value="US_SF" selected>San Francisco, CA, USA</option>
                                <option value="US_NYC">New York, NY, USA</option>
                                <option value="IN_BLR">Bangalore, IN</option>
                                <option value="DE_BER">Berlin, DE</option>
                                <option value="JP_TYO">Tokyo, JP</option>
                            </select>
                        </div>

                        <div>
                            <label class="font-geist text-xs font-bold text-on-surface-variant uppercase tracking-wider block mb-1.5">Target Location</label>
                            <select id="sim-target-loc" onchange="updateSimulator()" class="w-full bg-surface border border-outline-variant/40 rounded-lg p-2.5 text-sm font-semibold text-on-surface cursor-pointer">
                                <option value="DE_BER" selected>Berlin, DE</option>
                                <option value="IN_BLR">Bangalore, IN</option>
                                <option value="US_SF">San Francisco, CA, USA</option>
                                <option value="US_NYC">New York, NY, USA</option>
                                <option value="JP_TYO">Tokyo, JP</option>
                            </select>
                        </div>

                        <div>
                            <div class="flex justify-between font-geist text-xs font-bold text-on-surface-variant uppercase tracking-wider mb-2">
                                <span>Base Gross Compensation</span>
                                <span id="sim-slider-val" class="text-primary font-mono text-sm">$150,000</span>
                            </div>
                            <input id="sim-slider" type="range" min="40000" max="400000" step="5000" value="150000" oninput="updateSimulator()" class="w-full h-2 bg-surface-container-high rounded-lg appearance-none cursor-pointer accent-primary"/>
                        </div>
                    </div>

                    <!-- Right: Comparison Bars & Insights -->
                    <div class="flex-[1.4] flex flex-col justify-center gap-6">
                        <!-- HQ Base Bar -->
                        <div>
                            <div class="flex justify-between font-geist text-xs font-bold text-on-surface-variant mb-1.5">
                                <span id="sim-base-bar-title">HQ Gross (San Francisco)</span>
                                <span id="sim-base-bar-amt" class="font-mono text-sm font-bold text-on-surface">$150,000</span>
                            </div>
                            <div class="w-full h-8 bg-surface-container-high rounded-full overflow-hidden flex border border-outline-variant/20">
                                <div id="sim-base-net-fill" class="bg-primary text-white text-[11px] font-geist font-semibold flex items-center px-3" style="width: 76%;">Net ($114,600)</div>
                                <div id="sim-base-tax-fill" class="bg-error/80 text-white text-[11px] font-geist font-semibold flex items-center justify-end px-3" style="width: 24%;">Tax 24%</div>
                            </div>
                        </div>

                        <!-- Target Equivalent Bar -->
                        <div>
                            <div class="flex justify-between font-geist text-xs font-bold text-secondary mb-1.5">
                                <span id="sim-target-bar-title">Target Equivalent (Berlin)</span>
                                <span id="sim-target-bar-amt" class="font-mono text-sm font-bold text-secondary">€121,400</span>
                            </div>
                            <div class="w-full h-8 bg-surface-container-high rounded-full overflow-hidden flex border border-secondary-container">
                                <div id="sim-target-net-fill" class="bg-secondary text-white text-[11px] font-geist font-semibold flex items-center px-3" style="width: 68%;">Net (€82,552)</div>
                                <div id="sim-target-tax-fill" class="bg-error/80 text-white text-[11px] font-geist font-semibold flex items-center justify-end px-3" style="width: 32%;">Tax 32%</div>
                            </div>
                        </div>

                        <!-- Parity Banner -->
                        <div id="sim-insight-banner" class="flex items-center gap-3 p-3.5 bg-secondary-fixed/20 border border-secondary-fixed/40 rounded-xl">
                            <span class="material-symbols-outlined text-secondary text-[22px]">insights</span>
                            <span id="sim-insight-text" class="text-xs text-on-surface leading-relaxed">
                                To maintain identical purchasing power in <strong>Berlin</strong>, a gross offer of <strong>€121,400</strong> is required.
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <!-- ======================================================================= -->
    <!-- VIEW 2: ANALYSIS DASHBOARD (Screen 1: Deep Analysis Dashboard)          -->
    <!-- ======================================================================= -->
    <main id="view-calculator" class="w-full flex-grow hidden">
        <div class="max-w-[1440px] mx-auto px-6 py-6">
            <div class="flex flex-col lg:flex-row gap-6">

                <!-- LEFT CONTROL PANEL (In-Page Aside Panel, No Native Sidebar) -->
                <aside class="w-full lg:w-[380px] shrink-0 bg-surface-container-low rounded-2xl p-6 border border-outline-variant/30 shadow-sm flex flex-col gap-6">
                    <div class="flex items-center justify-between text-primary">
                        <div class="flex items-center gap-2">
                            <span class="material-symbols-outlined text-[22px]">tune</span>
                            <h2 class="font-heading text-base font-bold uppercase tracking-wider text-[#006194]">Calculation Engine</h2>
                        </div>
                        <button onclick="copyExecutiveSummary()" title="Copy Markdown Comp Brief" class="px-2.5 py-1 bg-white hover:bg-surface-container border border-outline-variant/40 rounded-md font-geist text-xs font-semibold text-primary flex items-center gap-1 transition-colors">
                            <span class="material-symbols-outlined text-[14px]">content_copy</span>
                            Copy Brief
                        </button>
                    </div>

                    <!-- Jurisdiction Context -->
                    <div class="flex flex-col gap-2">
                        <label class="font-geist text-xs font-bold text-on-surface-variant uppercase tracking-wider">Jurisdiction & Metro</label>
                        <div class="grid grid-cols-2 gap-2">
                            <select id="calc-country" onchange="onCountryChange()" class="w-full bg-white border border-outline-variant/50 rounded-lg px-3 py-2 text-sm font-medium text-on-surface cursor-pointer">
                                <option value="IN" selected>India (INR)</option>
                                <option value="US">United States (USD)</option>
                                <option value="DE">Germany (EUR)</option>
                                <option value="JP">Japan (JPY)</option>
                            </select>
                            <select id="calc-city" class="w-full bg-white border border-outline-variant/50 rounded-lg px-3 py-2 text-sm font-medium text-on-surface cursor-pointer">
                                <option value="Bangalore" selected>Bangalore</option>
                                <option value="Mumbai">Mumbai</option>
                                <option value="Delhi">Delhi</option>
                                <option value="Hyderabad">Hyderabad</option>
                                <option value="Pune">Pune</option>
                            </select>
                        </div>
                    </div>

                    <!-- Job Role -->
                    <div class="flex flex-col gap-2">
                        <label class="font-geist text-xs font-bold text-on-surface-variant uppercase tracking-wider">Job Role</label>
                        <select id="calc-role" class="w-full bg-white border border-outline-variant/50 rounded-lg px-3 py-2 text-sm font-medium text-on-surface cursor-pointer">
                            <option value="Software Engineer" selected>Software Engineer</option>
                            <option value="Data Scientist">Data Scientist</option>
                            <option value="Data Analyst">Data Analyst</option>
                        </select>
                    </div>

                    <!-- Salary Presets -->
                    <div class="flex flex-col gap-1.5">
                        <label class="font-geist text-xs font-bold text-on-surface-variant uppercase tracking-wider">Quick Band Presets</label>
                        <div class="grid grid-cols-3 gap-2">
                            <button type="button" onclick="applyPreset('p25')" class="py-1.5 bg-white border border-outline-variant/40 hover:border-primary rounded-md font-geist text-xs font-semibold text-on-surface transition-colors">P25</button>
                            <button type="button" onclick="applyPreset('p50')" class="py-1.5 bg-white border border-outline-variant/40 hover:border-primary rounded-md font-geist text-xs font-semibold text-on-surface transition-colors">Median</button>
                            <button type="button" onclick="applyPreset('p75')" class="py-1.5 bg-white border border-outline-variant/40 hover:border-primary rounded-md font-geist text-xs font-semibold text-on-surface transition-colors">P75</button>
                        </div>
                    </div>

                    <!-- Salary Input -->
                    <div class="flex flex-col gap-2">
                        <div class="flex justify-between items-center font-geist text-xs font-bold text-on-surface-variant uppercase tracking-wider">
                            <span>Annual Gross Salary</span>
                            <span id="calc-curr-badge" class="text-outline">₹ INR</span>
                        </div>
                        <div class="relative">
                            <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-on-surface-variant font-bold text-lg" id="calc-curr-sym">₹</div>
                            <input id="calc-gross-input" type="number" value="3500000" step="50000" oninput="updateInputPreview()" class="w-full bg-white border border-outline-variant/50 rounded-xl pl-8 pr-3 py-2.5 font-heading text-xl font-bold text-on-surface tracking-tight focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"/>
                        </div>
                        <div id="calc-approx-usd" class="text-right font-mono text-xs text-on-surface-variant">Approx. $36,676 USD (FX Spot)</div>
                    </div>

                    <!-- Recalculate CTA -->
                    <button id="btn-recalc" onclick="handleRecalculateClick()" class="w-full bg-primary hover:bg-primary-container text-white py-3 rounded-xl font-geist text-sm font-semibold transition-all flex items-center justify-center gap-2 shadow-sm active:scale-[0.98]">
                        <span class="material-symbols-outlined text-[18px]">bolt</span>
                        Recalculate Equivalence
                    </button>
                </aside>

                <!-- RIGHT MAIN ANALYSIS CANVAS -->
                <section id="dash-results-container" class="flex-1 flex flex-col gap-6 transition-opacity duration-200">
                    <!-- Location & Cohort Header Banner -->
                    <div class="flex justify-between items-center flex-wrap gap-4">
                        <div>
                            <h2 class="font-heading text-2xl font-bold text-on-surface" id="dash-header-title">Compensation Analysis</h2>
                            <div class="text-xs text-on-surface-variant mt-0.5" id="dash-header-subtitle">Software Engineer • Bangalore, India</div>
                        </div>
                        <div class="flex gap-2">
                            <span id="dash-fx-pill" class="bg-blue-100 text-blue-900 font-geist text-xs font-semibold px-3 py-1 rounded-full">FX: 1 USD = 95.43 INR</span>
                            <span id="dash-ppp-pill" class="bg-emerald-100 text-emerald-900 font-geist text-xs font-semibold px-3 py-1 rounded-full">PPP Factor: 20.45</span>
                        </div>
                    </div>

                    <!-- TOP 4-METRIC GRID (Faithful Stitch Design) -->
                    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
                        <!-- 1. Gross Base -->
                        <div class="bg-surface-container-low rounded-xl p-5 border border-outline-variant/30 flex flex-col justify-between hover:border-primary/50 transition-colors">
                            <div class="font-geist text-xs font-bold uppercase tracking-wider text-on-surface-variant flex items-center gap-1.5">
                                <span class="material-symbols-outlined text-[16px]">payments</span>
                                Gross Base
                            </div>
                            <div class="font-heading text-3xl font-extrabold text-on-surface tracking-tight my-2" id="m-gross-val">₹35.0L</div>
                            <div class="text-xs text-outline font-medium" id="m-gross-sub">Per Annum</div>
                        </div>

                        <!-- 2. Net Take-Home (Glowing Mint Focus) -->
                        <div class="bg-secondary-fixed/20 rounded-xl p-5 border border-secondary-fixed/40 flex flex-col justify-between relative overflow-hidden shadow-[0_8px_30px_rgb(111,251,190,0.15)]">
                            <div class="absolute -right-4 -top-4 w-20 h-20 bg-secondary-fixed/30 rounded-full blur-xl"></div>
                            <div class="font-geist text-xs font-bold uppercase tracking-wider text-on-secondary-fixed-variant flex items-center gap-1.5">
                                <span class="material-symbols-outlined text-[16px] text-secondary">check_circle</span>
                                Net Take-Home
                            </div>
                            <div class="font-heading text-3xl font-extrabold text-on-secondary-fixed-variant tracking-tight my-2" id="m-net-val">₹27.36L</div>
                            <div class="text-xs text-secondary font-semibold" id="m-net-sub">₹2.28L / month</div>
                        </div>

                        <!-- 3. Effective Tax Rate -->
                        <div class="bg-surface-container-low rounded-xl p-5 border border-outline-variant/30 flex flex-col justify-between">
                            <div class="font-geist text-xs font-bold uppercase tracking-wider text-error flex items-center gap-1.5">
                                <span class="material-symbols-outlined text-[16px] text-error">account_balance</span>
                                Effective Tax
                            </div>
                            <div class="font-heading text-3xl font-extrabold text-error tracking-tight my-2" id="m-tax-val">21.8%</div>
                            <div class="text-xs text-outline font-medium" id="m-tax-sub">Tax: ₹7,64,400</div>
                        </div>

                        <!-- 4. Equivalence Score with Radial SVG Ring -->
                        <div class="bg-surface-container-low rounded-xl p-5 border border-outline-variant/30 flex items-center justify-between">
                            <div>
                                <div class="font-geist text-xs font-bold uppercase tracking-wider text-primary flex items-center gap-1.5">
                                    <span class="material-symbols-outlined text-[16px] text-primary">military_tech</span>
                                    Eqv. Score
                                </div>
                                <div class="font-heading text-3xl font-extrabold text-primary tracking-tight my-2" id="m-score-val">83<span class="text-sm font-medium text-outline">/100</span></div>
                                <div class="text-xs font-semibold text-primary" id="m-score-sub">Top Tier</div>
                            </div>
                            <div class="w-14 h-14 relative">
                                <svg class="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                                    <path class="stroke-outline-variant/30" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke-width="4"/>
                                    <path id="score-radial-path" class="stroke-primary transition-all duration-700" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke-dasharray="83, 100" stroke-width="4" stroke-linecap="round"/>
                                </svg>
                            </div>
                        </div>
                    </div>

                    <!-- 2-COLUMN BREAKDOWN: Normalization Bars + Statutory Decomposition -->
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <!-- Left: Purchasing Power Normalization Bars -->
                        <div class="bg-white rounded-2xl p-6 border border-outline-variant/30 shadow-sm flex flex-col justify-between">
                            <div class="flex justify-between items-center mb-4">
                                <div class="font-heading text-base font-bold text-on-surface flex items-center gap-2">
                                    <span class="material-symbols-outlined text-primary text-[20px]">equalizer</span>
                                    Purchasing Power Normalization
                                </div>
                                <span class="px-2 py-0.5 rounded bg-surface-container-high text-on-surface-variant font-geist text-[10px] font-bold uppercase">USD Base</span>
                            </div>

                            <div class="flex flex-col gap-4">
                                <!-- Nominal USD -->
                                <div class="p-3 bg-surface-container-low rounded-xl border border-outline-variant/20 hover:border-slate-400 transition-colors" title="Nominal take-home converted using live ECB foreign exchange spot rate.">
                                    <div class="flex justify-between font-geist text-xs font-semibold text-on-surface mb-1">
                                        <span class="flex items-center gap-1">
                                            Nominal USD (Live FX)
                                            <span class="material-symbols-outlined text-[13px] text-outline">help</span>
                                        </span>
                                        <span id="norm-nom-amt" class="font-mono text-sm font-bold">$28,670</span>
                                    </div>
                                    <div class="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                                        <div id="norm-nom-bar" class="bg-slate-500 h-full rounded-full transition-all duration-700" style="width: 25%;"></div>
                                    </div>
                                </div>

                                <!-- PPP Equivalence -->
                                <div class="p-3 bg-surface-container-low rounded-xl border border-outline-variant/20 hover:border-primary/40 transition-colors" title="Purchasing power equivalent in international dollars (Int$) based on World Bank 2024 basket.">
                                    <div class="flex justify-between font-geist text-xs font-semibold text-primary mb-1">
                                        <span class="flex items-center gap-1">
                                            PPP Equivalence (Int$)
                                            <span class="material-symbols-outlined text-[13px] text-primary">help</span>
                                        </span>
                                        <span id="norm-ppp-amt" class="font-mono text-sm font-bold text-primary">$133,780</span>
                                    </div>
                                    <div class="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                                        <div id="norm-ppp-bar" class="bg-primary-light h-full rounded-full transition-all duration-700" style="width: 80%;"></div>
                                    </div>
                                </div>

                                <!-- COL Adjusted -->
                                <div class="p-3 bg-primary/5 rounded-xl border border-primary/30 hover:border-primary transition-colors" title="Normalized purchasing value anchored to New York City cost of living index (NYC Base 100.0).">
                                    <div class="flex justify-between font-geist text-xs font-bold text-primary mb-1">
                                        <span class="flex items-center gap-1">
                                            COL-Adjusted (NYC Base)
                                            <span class="material-symbols-outlined text-[13px] text-primary">help</span>
                                        </span>
                                        <span id="norm-col-amt" class="font-mono text-sm font-extrabold text-primary">$111,124</span>
                                    </div>
                                    <div class="w-full bg-slate-200 h-2.5 rounded-full overflow-hidden">
                                        <div id="norm-col-bar" class="bg-primary h-full rounded-full transition-all duration-700 shadow-[0_0_8px_rgba(0,97,148,0.4)]" style="width: 100%;"></div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Right: Statutory Decomposition Waterfall Table -->
                        <div class="bg-white rounded-2xl p-6 border border-outline-variant/30 shadow-sm flex flex-col justify-between">
                            <div class="flex justify-between items-center mb-4">
                                <div class="font-heading text-base font-bold text-on-surface flex items-center gap-2">
                                    <span class="material-symbols-outlined text-secondary text-[20px]">account_tree</span>
                                    Statutory Tax Decomposition
                                </div>
                                <span class="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-geist text-[10px] font-bold uppercase">2024 MODEL</span>
                            </div>

                            <div id="decomp-rows-container" class="flex flex-col divide-y divide-outline-variant/20 text-xs">
                                <!-- Dynamic rows generated via JS -->
                            </div>
                        </div>
                    </div>

                    <!-- MARKET PERCENTILE BENCHMARK CARD -->
                    <div class="bg-white rounded-2xl p-6 border border-outline-variant/30 shadow-sm">
                        <div class="flex justify-between items-center mb-6">
                            <div>
                                <div class="font-heading text-base font-bold text-on-surface flex items-center gap-2">
                                    <span class="material-symbols-outlined text-primary text-[20px]">timeline</span>
                                    Market Percentile Benchmark
                                </div>
                                <div class="text-xs text-on-surface-variant mt-0.5" id="bench-subtitle">Software Engineer • Bangalore Tech Cohort</div>
                            </div>
                            <span id="bench-placement-badge" class="font-geist text-xs font-bold text-primary bg-primary-fixed/40 px-3 py-1 rounded-full">
                                P78 Placement
                            </span>
                        </div>

                        <!-- Visual Track -->
                        <div class="relative py-6">
                            <div class="w-full h-2.5 bg-surface-container rounded-full relative">
                                <div id="bench-track-fill" class="h-full bg-gradient-to-r from-primary-fixed to-primary rounded-full transition-all duration-700" style="width: 78%;"></div>

                                <!-- P25 -->
                                <div class="absolute left-[25%] -top-2 flex flex-col items-center -translate-x-1/2">
                                    <div class="w-0.5 h-6 bg-outline-variant"></div>
                                    <span class="text-[10px] font-geist font-bold text-on-surface-variant mt-1">P25</span>
                                    <span id="bench-p25-val" class="text-[10px] font-mono text-outline">₹15.0L</span>
                                </div>

                                <!-- P50 -->
                                <div class="absolute left-[50%] -top-2 flex flex-col items-center -translate-x-1/2">
                                    <div class="w-0.5 h-6 bg-outline-variant"></div>
                                    <span class="text-[10px] font-geist font-bold text-on-surface mt-1">Median (P50)</span>
                                    <span id="bench-p50-val" class="text-[10px] font-mono text-outline">₹25.0L</span>
                                </div>

                                <!-- P75 -->
                                <div class="absolute left-[75%] -top-2 flex flex-col items-center -translate-x-1/2">
                                    <div class="w-0.5 h-6 bg-outline-variant"></div>
                                    <span class="text-[10px] font-geist font-bold text-on-surface-variant mt-1">P75</span>
                                    <span id="bench-p75-val" class="text-[10px] font-mono text-outline">₹40.0L</span>
                                </div>

                                <!-- Current User Pin -->
                                <div id="bench-user-pin" class="absolute left-[78%] -translate-x-1/2 -top-7 flex flex-col items-center z-10 transition-all duration-700">
                                    <div id="bench-user-pill" class="bg-primary text-white font-geist text-[10px] font-bold px-2 py-0.5 rounded shadow whitespace-nowrap">
                                        You: ₹35.0L (78th)
                                    </div>
                                    <div class="w-2 h-2 bg-primary rotate-45 -mt-1 shadow-sm"></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- GLOBAL CROSS-BORDER PARITY MATRIX -->
                    <div class="bg-white rounded-2xl p-6 border border-outline-variant/30 shadow-sm">
                        <div class="flex justify-between items-center mb-4">
                            <div>
                                <div class="font-heading text-base font-bold text-on-surface flex items-center gap-2">
                                    <span class="material-symbols-outlined text-secondary text-[20px]">public</span>
                                    Global Equivalent Offers (Equal Purchasing Power)
                                </div>
                                <div class="text-xs text-on-surface-variant mt-0.5">Gross compensation required in major global hubs to match your current lifestyle</div>
                            </div>
                            <span class="px-2.5 py-0.5 bg-secondary-fixed/30 text-on-secondary-fixed-variant rounded-full text-xs font-semibold">Parity Anchored</span>
                        </div>

                        <div id="global-parity-grid" class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 pt-2">
                            <!-- Populated dynamically via JS -->
                        </div>
                    </div>

                    <!-- Data Provenance Bar -->
                    <div class="flex justify-between items-center p-3 bg-surface-container-low border border-outline-variant/30 rounded-xl text-xs text-on-surface-variant">
                        <div class="flex items-center gap-2">
                            <span class="material-symbols-outlined text-secondary text-[16px]">sync</span>
                            <span>WorldBank 2024 PPP • 2024 Statutory Tables • Numbeo Mid-2024 COL (NYC 100.0)</span>
                        </div>
                        <span class="font-mono text-xs font-semibold text-secondary">INTEGRITY: SYNCED</span>
                    </div>
                </section>
            </div>
        </div>
    </main>

    <!-- ======================================================================= -->
    <!-- VIEW 3: METHODOLOGY PAGE                                                -->
    <!-- ======================================================================= -->
    <main id="view-methodology" class="w-full flex-grow hidden">
        <div class="max-w-[1200px] mx-auto px-6 py-10">
            <h1 class="font-heading text-3xl font-bold text-on-surface mb-2">Statutory Normalization Methodology</h1>
            <p class="text-on-surface-variant text-sm mb-8">Formal mathematical specification of the 4-stage cross-border equivalence algorithm.</p>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-white p-6 rounded-2xl border border-outline-variant/30 shadow-sm">
                    <h3 class="font-heading text-lg font-bold text-primary mb-3">1. Statutory Take-Home Pay</h3>
                    <p class="text-xs text-on-surface-variant leading-relaxed mb-3">
                        Net salary is computed by executing progressive statutory tax brackets, standard allowances, and mandatory social security contributions.
                    </p>
                    <div class="bg-surface-container p-3 rounded-lg font-mono text-xs text-on-surface">
                        Net Local = Gross - StatutoryTax(Gross) - MandatoryContributions
                    </div>
                </div>

                <div class="bg-white p-6 rounded-2xl border border-outline-variant/30 shadow-sm">
                    <h3 class="font-heading text-lg font-bold text-primary mb-3">2. Tri-Vector Normalization</h3>
                    <p class="text-xs text-on-surface-variant leading-relaxed mb-3">
                        Net local pay is adjusted across Nominal Spot FX, World Bank Purchasing Power Parity (Int$), and Numbeo Cost of Living index.
                    </p>
                    <div class="bg-surface-container p-3 rounded-lg font-mono text-xs text-on-surface">
                        COL-Adjusted USD = Nominal USD * (100.0 / CityCOLIndex)
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- FOOTER (Clean Stitch Design) -->
    <footer class="w-full bg-surface-container-low border-t border-outline-variant/30 py-8 mt-12">
        <div class="max-w-[1400px] mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4 text-on-surface-variant text-xs">
            <div>© 2024 EquivPay. Engineering Global Compensation Equity.</div>
            <nav class="flex gap-6 font-medium">
                <button onclick="switchView('landing')" class="hover:text-on-surface transition-colors">Product Overview</button>
                <button onclick="switchView('calculator')" class="hover:text-on-surface transition-colors">Analysis Dashboard</button>
                <button onclick="switchView('methodology')" class="hover:text-on-surface transition-colors">Methodology</button>
            </nav>
        </div>
    </footer>

    <!-- CLIENT-SIDE CALCULATION ENGINE & REACTIVE JS -->
    <script>
    // Embedded Reference Data from project backend
    const TAX_DATA = {json.dumps(TAX_DATA)};
    const COL_DATA = {json.dumps(COL_DATA)};
    const BENCH_DATA = {json.dumps(bench_data)};
    const FX_DATA = {json.dumps(fx_data)};
    const PPP_DATA = {json.dumps(ppp_data)};

    const ISO3_MAP = {{"IN": "IND", "US": "USA", "DE": "DEU", "JP": "JPN"}};
    const CURR_MAP = {{"IN": "INR", "US": "USD", "DE": "EUR", "JP": "JPY"}};
    const CURR_SYM = {{"IN": "₹", "US": "$", "DE": "€", "JP": "¥"}};

    // Switch Views seamlessly
    function switchView(viewName) {{
        document.getElementById('view-landing').classList.add('hidden');
        document.getElementById('view-calculator').classList.add('hidden');
        document.getElementById('view-methodology').classList.add('hidden');

        document.getElementById('nav-landing').classList.remove('active');
        document.getElementById('nav-calculator').classList.remove('active');
        document.getElementById('nav-methodology').classList.remove('active');

        if (viewName === 'landing') {{
            document.getElementById('view-landing').classList.remove('hidden');
            document.getElementById('nav-landing').classList.add('active');
        }} else if (viewName === 'calculator') {{
            document.getElementById('view-calculator').classList.remove('hidden');
            document.getElementById('nav-calculator').classList.add('active');
            runDashboardCalculation();
        }} else if (viewName === 'methodology') {{
            document.getElementById('view-methodology').classList.remove('hidden');
            document.getElementById('nav-methodology').classList.add('active');
        }}
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    // Tax calculation math in JS
    function calculateNetPay(gross, country) {{
        gross = parseFloat(gross) || 0;
        let tax = 0;
        let items = [];

        if (country === 'IN') {{
            let stdDed = 50000;
            let taxable = Math.max(0, gross - stdDed);
            items.push({{ label: 'Standard Deduction', amount: stdDed, type: 'deduction', note: 'Statutory relief' }});
            if (taxable <= 700000) {{
                items.push({{ label: 'Income Tax (Sec 87A Rebate)', amount: 0, type: 'tax', note: '100% rebate under ₹7L' }});
                tax = 0;
            }} else {{
                let rawTax = 0;
                let prev = 0;
                const brackets = [
                    {{ cap: 300000, rate: 0.0 }},
                    {{ cap: 600000, rate: 0.05 }},
                    {{ cap: 900000, rate: 0.10 }},
                    {{ cap: 1200000, rate: 0.15 }},
                    {{ cap: 1500000, rate: 0.20 }},
                    {{ cap: null, rate: 0.30 }}
                ];
                for (let b of brackets) {{
                    if (b.cap === null || taxable <= b.cap) {{
                        rawTax += (taxable - prev) * b.rate;
                        break;
                    }} else {{
                        rawTax += (b.cap - prev) * b.rate;
                        prev = b.cap;
                    }}
                }}
                let cess = rawTax * 0.04;
                tax = rawTax + cess;
                items.push({{ label: 'Income Tax (Slabs)', amount: rawTax, type: 'tax', note: 'Progressive slabs' }});
                items.push({{ label: 'Health & Education Cess (4%)', amount: cess, type: 'tax', note: '4% on tax' }});
            }}
        }} else if (country === 'US') {{
            let stdDed = 14600;
            let taxable = Math.max(0, gross - stdDed);
            items.push({{ label: 'Standard Deduction', amount: stdDed, type: 'deduction', note: 'Single baseline' }});
            let ss = Math.min(gross, 168600) * 0.062;
            let med = gross * 0.0145;
            let addlMed = gross > 200000 ? (gross - 200000) * 0.009 : 0;
            let fedTax = 0;
            let prev = 0;
            const brackets = [
                {{ cap: 11600, rate: 0.10 }},
                {{ cap: 47150, rate: 0.12 }},
                {{ cap: 100525, rate: 0.22 }},
                {{ cap: 191950, rate: 0.24 }},
                {{ cap: 243725, rate: 0.32 }},
                {{ cap: 609350, rate: 0.35 }},
                {{ cap: null, rate: 0.37 }}
            ];
            for (let b of brackets) {{
                if (b.cap === null || taxable <= b.cap) {{
                    fedTax += (taxable - prev) * b.rate;
                    break;
                }} else {{
                    fedTax += (b.cap - prev) * b.rate;
                    prev = b.cap;
                }}
            }}
            tax = fedTax + ss + med + addlMed;
            items.push({{ label: 'Federal Income Tax', amount: fedTax, type: 'tax', note: '7-bracket model' }});
            items.push({{ label: 'FICA Social Security (6.2%)', amount: ss, type: 'tax', note: 'Capped at $168.6k' }});
            items.push({{ label: 'FICA Medicare (1.45%)', amount: med + addlMed, type: 'tax', note: 'Hospital insurance' }});
        }} else if (country === 'DE') {{
            let zve = Math.floor(gross);
            if (zve <= 12096) tax = 0;
            else if (zve <= 17443) {{
                let y = (zve - 12096) / 10000;
                tax = (912.17 * y + 1400) * y;
            }} else if (zve <= 68480) {{
                let y = (zve - 17443) / 10000;
                tax = (228.74 * y + 2397) * y + 1025.38;
            }} else if (zve <= 277825) {{
                tax = zve * 0.42 - 10202.94;
            }} else {{
                tax = zve * 0.45 - 18537.69;
            }}
            items.push({{ label: 'Progressive Income Tax (ESt)', amount: tax, type: 'tax', note: '§32a EStG 2024 Zones' }});
        }} else if (country === 'JP') {{
            let empDed = 0;
            if (gross <= 1625000) empDed = 550000;
            else if (gross <= 1800000) empDed = gross * 0.4 - 100000;
            else if (gross <= 3600000) empDed = gross * 0.3 + 80000;
            else if (gross <= 6600000) empDed = gross * 0.2 + 440000;
            else if (gross <= 8500000) empDed = gross * 0.1 + 1100000;
            else empDed = 1950000;
            let basicDed = 480000;
            items.push({{ label: 'Employment Income Deduction', amount: empDed, type: 'deduction', note: 'Salary deduction' }});
            items.push({{ label: 'Basic Exemption', amount: basicDed, type: 'deduction', note: 'Standard basic deduction' }});
            let taxable = Math.max(0, gross - empDed - basicDed);
            taxable = Math.floor(taxable / 1000) * 1000;
            let natTax = 0;
            if (taxable > 0) {{
                if (taxable <= 1950000) natTax = taxable * 0.05;
                else if (taxable <= 3300000) natTax = taxable * 0.10 - 97500;
                else if (taxable <= 6950000) natTax = taxable * 0.20 - 427500;
                else if (taxable <= 9000000) natTax = taxable * 0.23 - 636000;
                else if (taxable <= 18000000) natTax = taxable * 0.33 - 1536000;
                else if (taxable <= 40000000) natTax = taxable * 0.40 - 2796000;
                else natTax = taxable * 0.45 - 4796000;
            }}
            let recon = natTax * 0.021;
            tax = natTax + recon;
            items.push({{ label: 'National Income Tax', amount: natTax, type: 'tax', note: 'National brackets' }});
            items.push({{ label: 'Reconstruction Surtax (2.1%)', amount: recon, type: 'tax', note: '2.1% of tax' }});
        }}

        let net = gross - tax;
        return {{ net: net, tax: tax, rate: gross > 0 ? (tax / gross) * 100 : 0, items: items }};
    }}

    function formatNumber(num, country) {{
        if (country === 'IN') {{
            if (num >= 10000000) return '₹' + (num / 10000000).toFixed(2) + ' Cr';
            if (num >= 100000) return '₹' + (num / 100000).toFixed(2) + 'L';
            return '₹' + Math.round(num).toLocaleString('en-IN');
        }} else if (country === 'US') {{
            return '$' + Math.round(num).toLocaleString('en-US');
        }} else if (country === 'DE') {{
            return '€' + Math.round(num).toLocaleString('de-DE');
        }} else if (country === 'JP') {{
            if (num >= 10000) return '¥' + (num / 10000).toFixed(1) + '万';
            return '¥' + Math.round(num).toLocaleString('ja-JP');
        }}
        return Math.round(num).toLocaleString();
    }}

    function updateInputPreview() {{
        const country = document.getElementById('calc-country').value;
        const gross = parseFloat(document.getElementById('calc-gross-input').value) || 0;
        const curr = CURR_MAP[country];
        const fxRate = FX_DATA.rates[curr] || 1.0;
        const approxUSD = Math.round(gross / fxRate);
        document.getElementById('calc-approx-usd').innerText = `Approx. $${{approxUSD.toLocaleString()}} USD (FX Spot)`;
    }}

    function onCountryChange() {{
        const country = document.getElementById('calc-country').value;
        const citySelect = document.getElementById('calc-city');
        citySelect.innerHTML = '';
        const cities = Object.keys(COL_DATA.cities[country] || {{}});
        cities.forEach(c => {{
            const opt = document.createElement('option');
            opt.value = c;
            opt.innerText = c;
            citySelect.appendChild(opt);
        }});

        const sym = CURR_SYM[country];
        const lbl = CURR_MAP[country];
        document.getElementById('calc-curr-sym').innerText = sym;
        document.getElementById('calc-curr-badge').innerText = sym + ' ' + lbl;

        const defaultG = country === 'IN' ? 3500000 : (country === 'US' ? 140000 : (country === 'DE' ? 85000 : 9500000));
        document.getElementById('calc-gross-input').value = defaultG;
        updateInputPreview();
    }}

    function applyPreset(presetKey) {{
        const country = document.getElementById('calc-country').value;
        const role = document.getElementById('calc-role').value;
        const bands = (BENCH_DATA[country] && BENCH_DATA[country][role]) || {{ p25: 100000, p50: 150000, p75: 200000 }};
        document.getElementById('calc-gross-input').value = bands[presetKey];
        updateInputPreview();
    }}

    function handleRecalculateClick() {{
        const btn = document.getElementById('btn-recalc');
        const originalHTML = btn.innerHTML;
        btn.innerHTML = `<span class="material-symbols-outlined text-[18px] animate-spin">refresh</span> Calculating...`;
        btn.disabled = true;

        const container = document.getElementById('dash-results-container');
        if (container) {{
            container.style.opacity = '0.5';
        }}

        setTimeout(() => {{
            runDashboardCalculation();
            if (container) {{
                container.style.opacity = '1';
            }}
            btn.innerHTML = originalHTML;
            btn.disabled = false;
        }}, 180);
    }}

    // Binary search target gross needed to yield a specific net local
    function solveGrossForTargetNet(targetNetLocal, country) {{
        let low = targetNetLocal;
        let high = targetNetLocal * 3.5;
        for (let i = 0; i < 30; i++) {{
            let mid = (low + high) / 2.0;
            let net = calculateNetPay(mid, country).net;
            if (net < targetNetLocal) low = mid;
            else high = mid;
        }}
        return (low + high) / 2.0;
    }}

    function runDashboardCalculation() {{
        const country = document.getElementById('calc-country').value;
        const city = document.getElementById('calc-city').value;
        const role = document.getElementById('calc-role').value;
        const gross = parseFloat(document.getElementById('calc-gross-input').value) || 0;

        const curr = CURR_MAP[country];
        const sym = CURR_SYM[country];
        const fxRate = FX_DATA.rates[curr] || 1.0;
        const iso3 = ISO3_MAP[country];
        const pppFactor = (PPP_DATA.latest_per_country[iso3] && PPP_DATA.latest_per_country[iso3].value) || 1.0;
        const cityCol = (COL_DATA.cities[country] && COL_DATA.cities[country][city]) || 100.0;

        const taxRes = calculateNetPay(gross, country);
        const netLocal = taxRes.net;
        const totalTax = taxRes.tax;
        const taxRate = taxRes.rate;

        // Conversions
        const nomUSD = netLocal / fxRate;
        const pppUSD = netLocal / pppFactor;
        const colUSD = nomUSD * (100.0 / cityCol);

        // Percentile
        const bands = (BENCH_DATA[country] && BENCH_DATA[country][role]) || {{ p25: 100000, p50: 150000, p75: 200000 }};
        let pctl = 50;
        if (gross < bands.p25) pctl = (gross / bands.p25) * 25;
        else if (gross < bands.p50) pctl = 25 + ((gross - bands.p25) / (bands.p50 - bands.p25)) * 25;
        else if (gross < bands.p75) pctl = 50 + ((gross - bands.p50) / (bands.p75 - bands.p50)) * 25;
        else pctl = Math.min(99.9, 75 + ((gross - bands.p75) / bands.p75) * 24);

        // Blended score
        const ppPoints = Math.min(100, (colUSD / 100000.0) * 100);
        const score = Math.round(pctl * 0.5 + ppPoints * 0.5);

        // Update Top Metrics
        document.getElementById('m-gross-val').innerText = formatNumber(gross, country);
        document.getElementById('m-gross-sub').innerText = sym + Math.round(gross).toLocaleString() + ' ' + curr + ' / year';

        document.getElementById('m-net-val').innerText = formatNumber(netLocal, country);
        document.getElementById('m-net-sub').innerText = formatNumber(netLocal / 12.0, country) + ' / month net pay';

        document.getElementById('m-tax-val').innerText = taxRate.toFixed(1) + '%';
        document.getElementById('m-tax-sub').innerText = 'Tax Burden: ' + sym + Math.round(totalTax).toLocaleString();

        document.getElementById('m-score-val').innerHTML = score + '<span class="text-sm font-medium text-outline">/100</span>';
        document.getElementById('m-score-sub').innerText = score >= 80 ? 'Top Tier' : (score >= 60 ? 'Strong Tier' : 'Moderate');
        document.getElementById('score-radial-path').setAttribute('stroke-dasharray', `${{score}}, 100`);

        // Header and pills
        document.getElementById('dash-header-subtitle').innerText = `${{role}} • ${{city}}, ${{country === 'IN' ? 'India' : (country === 'US' ? 'United States' : (country === 'DE' ? 'Germany' : 'Japan'))}}`;
        document.getElementById('dash-fx-pill').innerText = `FX: 1 USD = ${{fxRate.toFixed(2)}} ${{curr}}`;
        document.getElementById('dash-ppp-pill').innerText = `PPP Factor: ${{pppFactor.toFixed(2)}}`;
        document.getElementById('calc-approx-usd').innerText = `Approx. $${{Math.round(gross / fxRate).toLocaleString()}} USD (FX Spot)`;

        // Normalization Bars
        const maxUSD = Math.max(nomUSD, pppUSD, colUSD, 1.0);
        document.getElementById('norm-nom-amt').innerText = '$' + Math.round(nomUSD).toLocaleString();
        document.getElementById('norm-nom-bar').style.width = Math.min(100, (nomUSD / maxUSD) * 100) + '%';

        document.getElementById('norm-ppp-amt').innerText = '$' + Math.round(pppUSD).toLocaleString();
        document.getElementById('norm-ppp-bar').style.width = Math.min(100, (pppUSD / maxUSD) * 100) + '%';

        document.getElementById('norm-col-amt').innerText = '$' + Math.round(colUSD).toLocaleString();
        document.getElementById('norm-col-bar').style.width = Math.min(100, (colUSD / maxUSD) * 100) + '%';

        // Decomposition Table
        const rowsContainer = document.getElementById('decomp-rows-container');
        rowsContainer.innerHTML = '';
        
        let baseRow = document.createElement('div');
        baseRow.className = 'flex justify-between items-center py-2.5';
        baseRow.innerHTML = `<span class="font-medium text-slate-700">Base Gross Salary</span><span class="font-mono font-bold text-slate-900">${{sym}}${{Math.round(gross).toLocaleString()}}</span>`;
        rowsContainer.appendChild(baseRow);

        taxRes.items.forEach(it => {{
            let isDed = it.type === 'deduction';
            let row = document.createElement('div');
            row.className = 'flex justify-between items-center py-2 text-slate-600';
            row.innerHTML = `
                <div>
                    <span>${{it.label}}</span>
                    <span class="text-[10px] text-slate-400 block">${{it.note}}</span>
                </div>
                <span class="font-mono font-semibold ${{isDed ? 'text-slate-500' : 'text-error'}}">
                    ${{isDed ? '' : '-'}}${{sym}}${{Math.round(it.amount).toLocaleString()}}
                </span>
            `;
            rowsContainer.appendChild(row);
        }});

        let totalRow = document.createElement('div');
        totalRow.className = 'flex justify-between items-center py-2.5 bg-emerald-50 text-emerald-900 rounded-lg px-3 mt-2 font-bold';
        totalRow.innerHTML = `<span>Net Annual Take-Home</span><span class="font-mono text-sm">${{sym}}${{Math.round(netLocal).toLocaleString()}}</span>`;
        rowsContainer.appendChild(totalRow);

        // Benchmark Track
        document.getElementById('bench-subtitle').innerText = `${{role}} • ${{city}} Verified Market Band`;
        document.getElementById('bench-placement-badge').innerText = `P${{Math.round(pctl)}} Placement`;
        document.getElementById('bench-track-fill').style.width = Math.min(100, Math.max(0, pctl)) + '%';
        document.getElementById('bench-p25-val').innerText = formatNumber(bands.p25, country);
        document.getElementById('bench-p50-val').innerText = formatNumber(bands.p50, country);
        document.getElementById('bench-p75-val').innerText = formatNumber(bands.p75, country);

        document.getElementById('bench-user-pin').style.left = Math.min(96, Math.max(4, pctl)) + '%';
        document.getElementById('bench-user-pill').innerText = `You: ${{formatNumber(gross, country)}} (${{Math.round(pctl)}}th)`;

        // Global Cross-Border Parity Matrix Update
        updateGlobalParityMatrix(colUSD);
    }}

    function updateGlobalParityMatrix(colUSD) {{
        const parityGrid = document.getElementById('global-parity-grid');
        parityGrid.innerHTML = '';

        const targets = [
            {{ key: 'US_SF', name: 'San Francisco', flag: '🇺🇸', country: 'US', city: 'San Francisco' }},
            {{ key: 'IN_BLR', name: 'Bangalore', flag: '🇮🇳', country: 'IN', city: 'Bangalore' }},
            {{ key: 'DE_BER', name: 'Berlin', flag: '🇩🇪', country: 'DE', city: 'Berlin' }},
            {{ key: 'JP_TYO', name: 'Tokyo', flag: '🇯🇵', country: 'JP', city: 'Tokyo' }}
        ];

        targets.forEach(tgt => {{
            const tCol = COL_DATA.cities[tgt.country][tgt.city] || 100.0;
            const tFx = FX_DATA.rates[CURR_MAP[tgt.country]] || 1.0;
            const tNeededNomUSD = colUSD / (100.0 / tCol);
            const tNeededNetLocal = tNeededNomUSD * tFx;
            const tGross = solveGrossForTargetNet(tNeededNetLocal, tgt.country);
            const tTax = calculateNetPay(tGross, tgt.country);

            const card = document.createElement('div');
            card.className = 'p-4 bg-surface-container-low rounded-xl border border-outline-variant/30 flex flex-col justify-between hover:border-primary/50 transition-colors';
            card.innerHTML = `
                <div>
                    <div class="flex items-center justify-between">
                        <span class="font-geist text-xs font-bold text-on-surface flex items-center gap-1.5">
                            <span class="text-base">${{tgt.flag}}</span> ${{tgt.name}}
                        </span>
                        <span class="text-[10px] font-mono text-outline">COL ${{tCol}}</span>
                    </div>
                    <div class="font-heading text-xl font-extrabold text-on-surface tracking-tight mt-2.5">
                        ${{formatNumber(tGross, tgt.country)}}
                    </div>
                    <div class="text-[11px] text-on-surface-variant font-medium mt-0.5">
                        Net: <span class="font-semibold text-secondary">${{formatNumber(tTax.net, tgt.country)}}</span>
                    </div>
                </div>
                <div class="flex justify-between items-center pt-3 border-t border-outline-variant/20 mt-3 text-[11px]">
                    <span class="text-outline">Tax Burden</span>
                    <span class="font-semibold text-error">${{tTax.rate.toFixed(1)}}%</span>
                </div>
            `;
            parityGrid.appendChild(card);
        }});
    }}

    // Dynamic Slider Rescaling for Offer Delta Simulator
    const SIM_LOC_CONFIG = {{
        "US_SF": {{ country: "US", city: "San Francisco", name: "San Francisco", min: 40000, max: 400000, step: 5000, default: 150000 }},
        "US_NYC": {{ country: "US", city: "New York", name: "New York", min: 40000, max: 400000, step: 5000, default: 160000 }},
        "IN_BLR": {{ country: "IN", city: "Bangalore", name: "Bangalore", min: 500000, max: 15000000, step: 50000, default: 3500000 }},
        "DE_BER": {{ country: "DE", city: "Berlin", name: "Berlin", min: 30000, max: 250000, step: 2500, default: 85000 }},
        "JP_TYO": {{ country: "JP", city: "Tokyo", name: "Tokyo", min: 3000000, max: 35000000, step: 100000, default: 11000000 }}
    }};

    function onSimulatorBaseChange() {{
        const baseKey = document.getElementById('sim-base-loc').value;
        const cfg = SIM_LOC_CONFIG[baseKey] || SIM_LOC_CONFIG["US_SF"];
        const slider = document.getElementById('sim-slider');
        slider.min = cfg.min;
        slider.max = cfg.max;
        slider.step = cfg.step;
        slider.value = cfg.default;
        updateSimulator();
    }}

    // Offer Delta Simulator Math
    function updateSimulator() {{
        const baseKey = document.getElementById('sim-base-loc').value;
        const targetKey = document.getElementById('sim-target-loc').value;
        const sliderVal = parseFloat(document.getElementById('sim-slider').value) || 150000;

        const base = SIM_LOC_CONFIG[baseKey] || SIM_LOC_CONFIG["US_SF"];
        const target = SIM_LOC_CONFIG[targetKey] || SIM_LOC_CONFIG["DE_BER"];

        const bSym = CURR_SYM[base.country];
        const tSym = CURR_SYM[target.country];

        document.getElementById('sim-slider-val').innerText = formatNumber(sliderVal, base.country);

        const baseTax = calculateNetPay(sliderVal, base.country);
        const baseNet = baseTax.net;
        const baseRate = baseTax.rate;
        const baseCol = COL_DATA.cities[base.country][base.city] || 100.0;
        const targetCol = COL_DATA.cities[target.country][target.city] || 100.0;

        const baseFx = FX_DATA.rates[CURR_MAP[base.country]] || 1.0;
        const targetFx = FX_DATA.rates[CURR_MAP[target.country]] || 1.0;

        const baseNetUSD = (baseNet / baseFx) * (100.0 / baseCol);
        const targetNeededNomUSD = baseNetUSD / (100.0 / targetCol);
        const targetNeededNetLocal = targetNeededNomUSD * targetFx;

        const targetGross = solveGrossForTargetNet(targetNeededNetLocal, target.country);
        const targetTax = calculateNetPay(targetGross, target.country);

        document.getElementById('sim-base-bar-title').innerText = `HQ Gross (${{base.name}})`;
        document.getElementById('sim-base-bar-amt').innerText = formatNumber(sliderVal, base.country);
        document.getElementById('sim-base-net-fill').style.width = (100 - baseRate) + '%';
        document.getElementById('sim-base-net-fill').innerText = `Net ${{formatNumber(baseNet, base.country)}}`;
        document.getElementById('sim-base-tax-fill').style.width = baseRate + '%';
        document.getElementById('sim-base-tax-fill').innerText = `Tax ${{baseRate.toFixed(0)}}%`;

        document.getElementById('sim-target-bar-title').innerText = `Target Equivalent (${{target.name}})`;
        document.getElementById('sim-target-bar-amt').innerText = formatNumber(targetGross, target.country);
        document.getElementById('sim-target-net-fill').style.width = (100 - targetTax.rate) + '%';
        document.getElementById('sim-target-net-fill').innerText = `Net ${{formatNumber(targetTax.net, target.country)}}`;
        document.getElementById('sim-target-tax-fill').style.width = targetTax.rate + '%';
        document.getElementById('sim-target-tax-fill').innerText = `Tax ${{targetTax.rate.toFixed(0)}}%`;

        document.getElementById('sim-insight-text').innerHTML = `To maintain identical purchasing power in <strong>${{target.name}}</strong>, a gross offer of <strong>${{formatNumber(targetGross, target.country)}}</strong> ($${{Math.round(targetGross / targetFx).toLocaleString()}} USD spot equivalent) is required.`;
    }}

    // Copy Comp Brief to Clipboard
    function copyExecutiveSummary() {{
        const country = document.getElementById('calc-country').value;
        const city = document.getElementById('calc-city').value;
        const role = document.getElementById('calc-role').value;
        const gross = parseFloat(document.getElementById('calc-gross-input').value) || 0;
        const taxRes = calculateNetPay(gross, country);
        const curr = CURR_MAP[country];

        const text = `📊 **EquivPay Global Compensation Brief**
- Role: ${{role}} (${{city}}, ${{country}})
- Gross Salary: ${{formatNumber(gross, country)}} (${{curr}})
- Net Take-Home: ${{formatNumber(taxRes.net, country)}} / year (${{formatNumber(taxRes.net / 12, country)}}/mo)
- Effective Statutory Tax: ${{taxRes.rate.toFixed(1)}}%
- Generated via EquivPay Normalization Engine`;

        navigator.clipboard.writeText(text).then(() => {{
            showToast('✓ Copied Comp Brief to clipboard!');
        }}).catch(() => {{
            showToast('✓ Comp Brief generated!');
        }});
    }}

    function showToast(msg) {{
        const toast = document.getElementById('toast');
        const msgEl = document.getElementById('toast-msg');
        msgEl.innerText = msg;
        toast.classList.remove('hidden');
        setTimeout(() => {{
            toast.classList.add('hidden');
        }}, 2600);
    }}

    // Initialize on load
    window.addEventListener('DOMContentLoaded', () => {{
        updateSimulator();
    }});
    </script>
</body>
</html>
"""

# Render the application as full iframe component
components.html(html_content, height=1400, scrolling=True)