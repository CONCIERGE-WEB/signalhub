# scout_kiryano — Source Provider (kiryano/Scout MIT)

Plugin **não-Core**. Atribuição: `third_party/kiryano_scout/`.

## Conectores (v0.1)

| Platform | Fonte |
|----------|--------|
| `github` | API pública GitHub |
| `youtube` | HTML público do canal |
| `linktree` | Linktree / link-in-bio |

**Não** incluído de propósito: Instagram/TikTok (CAPTCHA), enrichment que **inventa** e-mail via SMTP/padrão, UI Rich do Scout original.

## Dry-run (sem gravar no banco)

```bash
pip install -r plugins/scout_kiryano/requirements.txt
python -m signalhub.apps.cli scout-kiryano --dry-run --platform github --target octocat
```

## Provider ao vivo (pipeline)

```bash
set SIGNALHUB_SCOUT_KIRYANO_LIVE=1
# query extras: platform=github ; terms=["usuario"]
```

Sem a env: lista vazia explícita (não inventa hits).
