# calculadora.py
import unicodedata

DEBUG = False  # coloque True para ver prints de debug

def normalize_text(s: str) -> str:
    """Lowercase, remove acentos e espaços extras."""
    s = s.strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s

def escolher_taxa_antecipacao(tipo_pessoa_raw: str):
    t = normalize_text(tipo_pessoa_raw)
    # aceita: fisica, f, pf, pessoa fisica, fisíca, etc.
    if t in ("f", "fisica", "pessoa fisica", "pf"):
        return 0.069  # 6.90% ao mês
    if t in ("j", "juridica", "pessoa juridica", "pj"):
        return 0.038  # 3.80% ao mês
    raise ValueError("Tipo de pessoa inválido. Use F (física) ou J (jurídica).")

def calcular_valor_liquido(venda: float, antecipado: bool, tipo_pessoa_raw: str = None, parcelas: int = 1):
    taxa_maquininha = 0.0249  # 2,49%
    if not antecipado:
        valor_liquido = venda * (1 - taxa_maquininha)
        desconto_maquininha = venda - valor_liquido
        return [{
            "parcela": 1,
            "valor_parcela": venda,
            "valor_com_taxa_maquininha": valor_liquido,
            "desconto_maquininha": desconto_maquininha,
            "desconto_antecipacao_val": 0.0,
            "valor_antecipado": valor_liquido,
            "meses_antecipados": 0
        }]
    # antecipado:
    taxa_antecipacao = escolher_taxa_antecipacao(tipo_pessoa_raw)
    resultados = []
    valor_parcela = venda / parcelas
    for i in range(1, parcelas + 1):
        mes_antecipado = i  # 1 para 1ª parcela (30 dias), 2 para 2ª (60 dias), etc.
        valor_com_taxa = valor_parcela * (1 - taxa_maquininha)
        desconto_maquininha = valor_parcela - valor_com_taxa
        desconto_antecipacao_percent = taxa_antecipacao * mes_antecipado
        if desconto_antecipacao_percent > 1:
            desconto_antecipacao_percent = 1.0  # não pode ultrapassar 100%
        desconto_antecipacao_val = valor_com_taxa * desconto_antecipacao_percent
        valor_antecipado = valor_com_taxa - desconto_antecipacao_val
        resultados.append({
            "parcela": i,
            "valor_parcela": valor_parcela,
            "valor_com_taxa_maquininha": valor_com_taxa,
            "desconto_maquininha": desconto_maquininha,
            "desconto_antecipacao_val": desconto_antecipacao_val,
            "desconto_antecipacao_percent": desconto_antecipacao_percent,
            "valor_antecipado": valor_antecipado,
            "meses_antecipados": mes_antecipado
        })
        if DEBUG:
            print(f"[DEBUG] parcela {i}: vp={valor_parcela:.4f}, depois maquininha={valor_com_taxa:.4f}, "
                  f"desconto_ante%={desconto_antecipacao_percent:.6f}, desconto_ante_val={desconto_antecipacao_val:.4f}, "
                  f"liquido={valor_antecipado:.4f}")
    return resultados

def main():
    import os, sys
    print("Rodando calculadora - arquivo:", os.path.abspath(__file__))
    try:
        venda = float(input("Digite o valor da venda: R$ ").replace(",", "."))
    except Exception:
        print("Valor inválido. Use somente números (ex: 100 ou 100.50).")
        return

    resposta_antecipado = normalize_text(input("O valor será antecipado? (S/N): "))
    if resposta_antecipado in ("n", "nao", "não", "no"):
        resultados = calcular_valor_liquido(venda, antecipado=False)
        r = resultados[0]
        print(f"\nRecebimento em 30 dias (não antecipado):")
        print(f" Valor bruto: R$ {r['valor_parcela']:.2f}")
        print(f" Desconto maquininha (2,49%): R$ {r['desconto_maquininha']:.2f}")
        print(f" Valor líquido a receber: R$ {r['valor_antecipado']:.2f}")
        return

    if resposta_antecipado in ("s", "sim", "yes", "y"):
        tipo_pessoa = input("Cliente é Pessoa Física (F) ou Jurídica (J)? ").strip()
        try:
            parcelas = int(input("Em quantas parcelas foi feita a venda? "))
            if parcelas < 1:
                raise ValueError
        except Exception:
            print("Número de parcelas inválido. Use um inteiro >= 1.")
            return

        try:
            resultados = calcular_valor_liquido(venda, antecipado=True, tipo_pessoa_raw=tipo_pessoa, parcelas=parcelas)
        except ValueError as ve:
            print(str(ve))
            return

        total_liquido = 0.0
        print("\nDetalhes do cálculo por parcela (antecipadas):")
        for r in resultados:
            print(f"Parcela {r['parcela']}:")
            print(f"  Valor bruto parcela: R$ {r['valor_parcela']:.2f}")
            print(f"  Após taxa maquininha (2,49%): R$ {r['valor_com_taxa_maquininha']:.2f} "
                  f"(Desconto maquininha: R$ {r['desconto_maquininha']:.2f})")
            print(f"  Taxa antecipação aplicada: {r.get('desconto_antecipacao_percent',0)*100:.2f}% "
                  f" => Desconto: R$ {r['desconto_antecipacao_val']:.2f}")
            print(f"  Valor líquido antecipado desta parcela: R$ {r['valor_antecipado']:.2f}\n")
            total_liquido += r['valor_antecipado']

        print(f"Total líquido a receber (todas as parcelas antecipadas): R$ {total_liquido:.2f}")
        return

    print("Resposta inválida. Por favor, responda com S (sim) ou N (não).")

if __name__ == "__main__":
    main()
