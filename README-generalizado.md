# Estrutura base para aplicação generalizada de avaliações

Esta branch implementa uma aplicação Streamlit com:
- Área de configuração (professor): upload de enunciado (markdown), imagens e parâmetros (json)
- Área do aluno: geração personalizada da avaliação ativa

## Estrutura esperada

- config/
    - avaliacao.md         # Enunciado em markdown
    - parametros.json      # Parâmetros aleatórios
    - images/              # Imagens usadas no markdown

## Como funciona

- O professor acessa a área de configuração (senha simples), faz upload dos arquivos e publica a avaliação.
- Os alunos acessam a área pública e geram sua avaliação personalizada.

## Exemplo de parametros.json

```
{
  "L": {"min": 4, "max": 8, "decimais": 1, "unidade": "m"},
  "d1": {"min": 100, "max": 200, "decimais": 0, "unidade": "mm"},
  "q1": {"min": 10, "max": 20, "decimais": 0, "unidade": "kN/m"}
}
```

---

Para deploy, siga as instruções do README principal.
