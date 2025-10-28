import os
import requests
from dotenv import load_dotenv
import gradio as gr

load_dotenv()

SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY") or ""
REST_URL = f"{SUPABASE_URL}/rest/v1"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}


def fetch_articles(limit: int = 20, topic: str | None = None):
    """Fetch latest articles from Supabase REST and return list of dicts.

    If `topic` is provided, filter articles by topic (exact match).
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []
    try:
        # select common fields; adjust order/fields as necessary
        q = f"select=guid,subject,content,image_url,notes,topic&order=created_at.desc&limit={limit}"
        if topic:
            # encode topic for URL and filter by exact match
            t = requests.utils.quote(topic, safe='')
            q = f"select=guid,subject,content,image_url,notes,topic&topic=eq.{t}&order=created_at.desc&limit={limit}"
        url = f"{REST_URL}/articles?{q}"
        r = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return []


def render_html(limit: int = 20, topic: str | None = None):
    articles = fetch_articles(limit, topic=topic)
    if not articles:
        return "<p>No articles found or Supabase not configured.</p>"

    rows = []
    for a in articles:
        title = a.get("subject") or a.get("notes") or "(no title)"
        img = a.get("image_url") or ""
        preview = f"<div style=\"margin-bottom:18px;display:flex;gap:12px;align-items:flex-start\">"
        if img:
            preview += f"<img src=\"{img}\" style=\"width:200px;height:auto;border-radius:6px;object-fit:cover\">"
        preview += f"<div><h3 style=\"margin:0 0 6px 0\">{title}</h3>"
        if a.get("topic"):
            preview += f"<div style=\"font-size:12px;color:#666;margin-bottom:6px\">Topic: {a.get('topic')}</div>"
        if a.get("content"):
            snippet = (a.get("content")[:280] + "...") if len(a.get("content")) > 280 else a.get("content")
            preview += f"<div style=\"font-size:14px;color:#222\">{snippet}</div>"
        preview += "</div></div>"
        rows.append(preview)

    html = "<div style=\"font-family:Arial,Helvetica,sans-serif;max-width:900px;margin:10px auto;padding:12px\">"
    html += "".join(rows)
    html += "</div>"
    return html


def run_gradio(port: int = 7860, host: str = "127.0.0.1"):
    """Start a small Gradio page showing latest articles and images.

    Note: Gradio is launched with prevent_thread_lock=True so it can run in a
    background thread alongside Flask.
    """
    with gr.Blocks() as demo:
        gr.Markdown("# News — Image Preview")
        with gr.Row():
            limit = gr.Slider(minimum=1, maximum=50, step=1, value=12, label="Number of articles")
            refresh = gr.Button("Refresh")
        # single featured button
        featured_btn = gr.Button("Show Featured Topics")

        out = gr.HTML(render_html())

        def on_refresh(n, topic=None):
            return render_html(n, topic=topic)

        # featured topics list (can be overridden with env FEATURE_TOPICS)
        FEATURE_TOPICS = os.environ.get("FEATURE_TOPICS", "Technology,Defense,Sports")
        FEATURE_LIST = [t.strip() for t in FEATURE_TOPICS.split(",") if t.strip()]

        def on_featured(n):
            # If multiple topics, render articles that match any of them by
            # concatenating results for each topic (deduplicate by guid)
            seen = set()
            html_parts = []
            for t in FEATURE_LIST:
                arts = fetch_articles(n, topic=t)
                for a in arts:
                    g = a.get("guid") or a.get("subject")
                    if g in seen:
                        continue
                    seen.add(g)
                    # reuse rendering for a single article (small)
                    title = a.get("subject") or a.get("notes") or "(no title)"
                    img = a.get("image_url") or ""
                    preview = f"<div style=\"margin-bottom:18px;display:flex;gap:12px;align-items:flex-start\">"
                    if img:
                        preview += f"<img src=\"{img}\" style=\"width:200px;height:auto;border-radius:6px;object-fit:cover\">"
                    preview += f"<div><h3 style=\"margin:0 0 6px 0\">{title}</h3>"
                    if a.get("topic"):
                        preview += f"<div style=\"font-size:12px;color:#666;margin-bottom:6px\">Topic: {a.get('topic')}</div>"
                    if a.get("content"):
                        snippet = (a.get("content")[:280] + "...") if len(a.get("content")) > 280 else a.get("content")
                        preview += f"<div style=\"font-size:14px;color:#222\">{snippet}</div>"
                    preview += "</div></div>"
                    html_parts.append(preview)
            if not html_parts:
                return "<p>No articles found for featured topics.</p>"
            return "<div style=\"font-family:Arial,Helvetica,sans-serif;max-width:900px;margin:10px auto;padding:12px\">" + "".join(html_parts) + "</div>"

        # wire the single buttons
        refresh.click(lambda n: on_refresh(n, None), inputs=limit, outputs=out)
        featured_btn.click(on_featured, inputs=limit, outputs=out)

    demo.launch(server_name=host, server_port=port, share=False, prevent_thread_lock=True)


if __name__ == "__main__":
    run_gradio()
