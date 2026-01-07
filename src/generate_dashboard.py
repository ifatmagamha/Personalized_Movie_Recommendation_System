import json
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from tests.eval_llm import evaluate_llm

def get_mlops_data():
    """Collects ML model metadata from the latest run."""
    try:
        latest_file = Path("models/LATEST")
        if not latest_file.exists():
            return {"status": "No models trained"}
        
        run_path = Path(latest_file.read_text().strip())
        config_path = run_path / "config.json"
        cf_info_path = run_path / "cf_info.json"
        
        data = {
            "run_id": run_path.name,
            "trained_at": datetime.fromtimestamp(run_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "config": {},
            "cf_metrics": {}
        }
        
        if config_path.exists():
            data["config"] = json.loads(config_path.read_text())
        if cf_info_path.exists():
            data["cf_metrics"] = json.loads(cf_info_path.read_text())
            
        return data
    except Exception as e:
        return {"status": "Error collecting ML data", "error": str(e)}

def generate_dashboard():
    print("Generating MLOps & LLMOps Dashboard...")
    
    # 1. Collect LLM Data
    llm_stats = evaluate_llm()
    
    # 2. Collect ML Data
    ml_stats = get_mlops_data()
    
    # 3. Build HTML
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MLOps & LLMOps Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #0f172a; color: #f8fafc; }}
        .glass {{ background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); }}
        .card-gradient {{ background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); }}
        .accent-blue {{ color: #38bdf8; }}
        .accent-green {{ color: #4ade80; }}
        .accent-purple {{ color: #c084fc; }}
    </style>
</head>
<body class="p-8">
    <div class="max-w-6xl mx-auto">
        <header class="mb-12 flex justify-between items-end">
            <div>
                <h1 class="text-4xl font-bold mb-2">System <span class="accent-blue">Observability</span></h1>
                <p class="text-slate-400">Real-time performance metrics for Recommendation Engine</p>
            </div>
            <div class="text-right">
                <p class="text-sm text-slate-500">Last Updated</p>
                <p class="font-mono">{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <!-- LLM Stats Card -->
            <div class="glass p-6 rounded-2xl">
                <h2 class="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">LLM Intent Accuracy</h2>
                <div class="text-5xl font-bold accent-green mb-2">{llm_stats['mood_accuracy']:.1f}%</div>
                <div class="w-full bg-slate-700 h-2 rounded-full overflow-hidden">
                    <div class="bg-green-500 h-full" style="width: {llm_stats['mood_accuracy']}%"></div>
                </div>
                <p class="mt-4 text-sm text-slate-400">Based on {llm_stats['total']} gold-standard test cases.</p>
            </div>

            <!-- Genre Recall Card -->
            <div class="glass p-6 rounded-2xl">
                <h2 class="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Genre Mapping Recall</h2>
                <div class="text-5xl font-bold accent-blue mb-2">{llm_stats['genre_recall']:.1f}%</div>
                <div class="w-full bg-slate-700 h-2 rounded-full overflow-hidden">
                    <div class="bg-blue-500 h-full" style="width: {llm_stats['genre_recall']}%"></div>
                </div>
                <p class="mt-4 text-sm text-slate-400">Accuracy of mapping natural language to DB categories.</p>
            </div>

            <!-- ML Training Card -->
            <div class="glass p-6 rounded-2xl">
                <h2 class="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">ML Model Status</h2>
                <div class="text-2xl font-bold accent-purple mb-1">{ml_stats.get('run_id', 'N/A')}</div>
                <p class="text-xs text-slate-500 mb-4">Model: {ml_stats.get('cf_metrics', {}).get('model_type', 'SVD')}</p>
                <div class="flex justify-between items-center text-sm">
                    <span class="text-slate-400">Users: {ml_stats.get('cf_metrics', {}).get('num_users', 0)}</span>
                    <span class="text-slate-400">Movies: {ml_stats.get('cf_metrics', {}).get('num_movies', 0)}</span>
                </div>
            </div>
        </div>

        <!-- Detailed Evaluation Table -->
        <section class="mb-12">
            <h2 class="text-2xl font-bold mb-6">LLM Evaluation <span class="accent-blue">Deep Dive</span></h2>
            <div class="glass rounded-2xl overflow-hidden">
                <table class="w-full text-left border-collapse">
                    <thead class="bg-slate-800/50">
                        <tr>
                            <th class="p-4 text-sm font-semibold text-slate-400">User Query</th>
                            <th class="p-4 text-sm font-semibold text-slate-400">Status</th>
                            <th class="p-4 text-sm font-semibold text-slate-400">Predicted Mood</th>
                            <th class="p-4 text-sm font-semibold text-slate-400">Extracted Genres</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-700/50">
                        {''.join([f'''
                        <tr class="hover:bg-slate-800/30 transition-colors">
                            <td class="p-4 italic text-slate-300">"{res['query']}"</td>
                            <td class="p-4">
                                <span class="px-2 py-1 rounded text-xs font-bold {'bg-green-500/10 text-green-400' if res['success'] else 'bg-red-500/10 text-red-400'}">
                                    {'PASSED' if res['success'] else 'FAILED'}
                                </span>
                            </td>
                            <td class="p-4 text-sm">{res['mood']}</td>
                            <td class="p-4 text-sm text-slate-400">{res['genres']}</td>
                        </tr>
                        ''' for res in llm_stats['results']])}
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Config & Next Steps -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <section class="glass p-6 rounded-2xl">
                <h2 class="text-xl font-bold mb-4">Current <span class="accent-purple">ML Config</span></h2>
                <div class="bg-black/30 p-4 rounded-xl font-mono text-xs text-purple-300 overflow-x-auto">
                    {json.dumps(ml_stats.get('config', {}), indent=2)}
                </div>
            </section>
            
            <section class="glass p-6 rounded-2xl">
                <h2 class="text-xl font-bold mb-4">Future <span class="accent-blue">Roadmap</span></h2>
                <ul class="space-y-4">
                    <li class="flex items-start">
                        <div class="bg-blue-500/20 text-blue-400 p-2 rounded-lg mr-3 mt-1">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                        </div>
                        <div>
                            <p class="font-semibold text-sm">LangSmith Integration</p>
                            <p class="text-xs text-slate-500">Trace conversational reasoning and optimize prompt chains.</p>
                        </div>
                    </li>
                    <li class="flex items-start">
                        <div class="bg-purple-500/20 text-purple-400 p-2 rounded-lg mr-3 mt-1">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
                        </div>
                        <div>
                            <p class="font-semibold text-sm">Weights & Biases (W&B)</p>
                            <p class="text-xs text-slate-500">Track drift in user feedback and model performance over time.</p>
                        </div>
                    </li>
                    <li class="flex items-start">
                        <div class="bg-green-500/20 text-green-400 p-2 rounded-lg mr-3 mt-1">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                        </div>
                        <div>
                            <p class="font-semibold text-sm">Automated Feedback Harvester</p>
                            <p class="text-xs text-slate-500">Convert real 'Not Helpful' swipes into new guardrail test cases.</p>
                        </div>
                    </li>
                </ul>
            </section>
        </div>
    </div>
</body>
</html>
    """
    
    with open("dashboard.html", "w", encoding="utf-8") as f:
        f.write(html_template)
    
    print("Dashboard generated: dashboard.html")

if __name__ == "__main__":
    generate_dashboard()
