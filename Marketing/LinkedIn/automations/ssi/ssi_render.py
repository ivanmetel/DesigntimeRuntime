from .model import SSIData

def render_obsidian_markdown(data: SSIData) -> str:
    """
    Render SSIData → Obsidian markdown with frontmatter.
    """
    
    # YAML Frontmatter (для dataview запросов)
    frontmatter = f"""---
date: {data.date.strftime('%Y-%m-%d')}
ssi: {data.ssi}
brand: {data.brand}
right_people: {data.right_people}
engagement: {data.engagement}
relationships: {data.relationships}
industry_rank: {data.industry_rank}
network_rank: {data.network_rank}
industry_avg: {data.industry_avg}
network_avg: {data.network_avg}
---

"""
    
    # Markdown body (читаемое для человека)
    markdown_body = f"""# SSI — {data.date.strftime('%B %Y')}

## Current snapshot
- **Current SSI:** {data.ssi} / 100
- **Industry SSI rank:** Top {data.industry_rank}%
- **Network SSI rank:** Top {data.network_rank}%

### Averages
- **People in my Network avg:** {data.network_avg} / 100
- **People in my Industry avg:** {data.industry_avg} / 100

## Components
- **Establish professional brand** — {data.brand}
- **Find the right people** — {data.right_people}
- **Engage with insights** — {data.engagement}
- **Build relationships** — {data.relationships}

---
*Generated: {data.date.strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    return frontmatter + markdown_body


def get_filename(data: SSIData) -> str:
    """Generate filename: 2026-01.md"""
    return data.date.strftime('%Y-%m.md')