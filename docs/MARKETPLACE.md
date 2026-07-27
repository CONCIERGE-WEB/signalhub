# SignalHub Marketplace (vision)

SignalHub is an **extensible signal-processing infrastructure**.  
Source connectors and outbound sinks are **plugins** (Capabilities Marketplace), not Core scrapers.

Illustrative catalog (community / partner plugins — not bundled as Core):

| Capability plugin | Kind |
|-------------------|------|
| Reddit Signals | Provider |
| Google / Web Signals | Provider |
| Reclame Aqui Signals | Provider |
| LinkedIn Signals | Provider |
| GitHub Signals | Provider |
| RSS Signals | Provider |
| Google Alerts | Provider |
| Telegram Alerts | Adapter |
| Discord / Slack / WhatsApp | Adapter |
| PDF Reports | Consumer |
| CRM / HubSpot / Salesforce | Consumer |
| Notion | Consumer |
| Webhook / Email | Consumer |

Each plugin:

- declares `plugin.yaml`
- respects RFC-0001 Signals
- owns compliance with its platform’s terms
- loads via Plugin Loader — **zero Core edits**

This positioning keeps SignalHub adoptable beyond legal/commercial prospecting: any org that needs **public-signal pipelines** + MCP/REST/CLI can extend the same Core.
