# Prospecção | Tiago A. Rocha (`scout_kiryano`)

Source Provider MIT (kiryano/Scout) sob Discovery Engine — **B2C only**.

## 9 categorias oficiais

| ID canônico | Label |
|-------------|--------|
| `voo_bagagem` | Voo e Bagagem |
| `negativacao_indevida` | Negativação Indevida |
| `cobranca_indevida` | Cobrança Indevida |
| `fraude_bancaria` | Fraudes Bancárias e Golpes |
| `plano_seguro_negativa` | Plano de Saúde |
| `produto_defeito_atraso` | Produto com Defeito |
| `pensao_alimenticia` | Pensão Alimentícia |
| `guarda_filhos` | Guarda e Convivência |
| `divorcio` | Divórcio e União Estável |

Aliases de copy (`plano_saude`, `produto_defeito`, `divorcio_uniao`) resolvem para o ID canônico.

## Gates

- Anti-B2B: advogado / advocacia / escritório / OAB / github / código / dev / repository
- Família: descarta nomes de menores / CPF exposto
- Sem inventar e-mail (sem SMTP/padrão)

## Dry-run (YouTube)

```bash
pip install -r plugins/scout_kiryano/requirements.txt
python -m signalhub.apps.cli scout-kiryano --dry-run --platform youtube --target HANDLE
```

GitHub é barrado pelo gate B2B (não serve ao funil consumidor).
