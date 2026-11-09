# Registro de decisões

Cada entrada traz a decisão, a alternativa rejeitada e o motivo.

## Etapa 0: preparação

### D1. Local do repositório
- **Decisão (confirmada pelo Éric):** a raiz do repositório é a própria pasta do projeto, renomeada de `Projeto 1` para `priorizacao-fraude`.
- **Alternativa rejeitada:** criar a subpasta `priorizacao-fraude/` e iniciar o Git dentro dela.
- **Motivo:** o `.gitignore` que contém `CLAUDE.local.md` foi pedido na raiz desta pasta. Com o repositório numa subpasta, essa regra não teria efeito.
- **Origem:** assumida pelo Claude para não travar a etapa. O Éric a confirmou ao renomear a pasta em 09/11/2026.

### D2. Gerenciador de ambiente
- **Decisão (escolha do Éric):** conda, canal conda-forge, Python 3.12, ambiente dentro do projeto em `.venv/`.
- **Alternativas rejeitadas:**
  - `uv` com Python 3.12: não está instalado, e o LightGBM do PyPI exige `libomp`, ausente nesta máquina, que também não tem Homebrew.
  - `venv` + `pip` com Python 3.9.6: é a única versão disponível no sistema, e as versões atuais de NumPy e pandas não a aceitam.
- **Motivo (aceito pelo Éric):** escolhi conda porque o LightGBM precisa de libomp, que só o conda-forge traz junto nesta máquina sem Homebrew, e assim não preciso de instalação global.
- **Fatos verificados:** a simulação no conda-forge resolveu todos os pacotes e inclui `llvm-openmp`, a biblioteca que o LightGBM precisa. O download previsto é de 242,8 MB compactados. A instalação ocupa 1,2 GB em `.venv/`. As versões fixadas estão em `environment-explicit.txt`.

### D3. Ferramenta de conversão para parquet
- **Decisão (escolha do Éric):** manter o `pyarrow` do conda-forge e corrigir o caminho fixo do Homebrew nos três arquivos `libarrow*.dylib`. Apontei o `liblz4` para `@loader_path/liblz4.1.dylib`, que já está em `.venv/lib/`, e reassinei o binário.
  ```
  install_name_tool -change /opt/homebrew/opt/lz4/lib/liblz4.1.dylib @loader_path/liblz4.1.dylib .venv/lib/libarrow.2600.1.0.dylib
  codesign --force -s - .venv/lib/libarrow.2600.1.0.dylib
  ```
- **Alternativas rejeitadas:**
  - Instalar o `pyarrow` pelo pip dentro do `.venv`: misturaria conda e pip no mesmo ambiente.
  - Recriar o ambiente com outra versão do `pyarrow`: nova resolução de mais de 5 minutos, sem garantia de funcionar.
- **Motivo:** mantém a stack da D2 e a correção é reversível. A desvantagem é que ela se perde se o ambiente for recriado. Nesse caso, repetir os dois comandos acima.
- **Verificado:** `pyarrow` 26.0.1 faz ida e volta de parquet sem perda, e `shap` 0.52.0 importa.

### D4. Tipos na preparação dos dados
- **Decisão (escolha do Claude, aviso ao Éric):** colunas `float64` viram `float32`, `int64` viram o menor inteiro que cabe, e textos com poucos valores viram `category`. Implementado em `src/preparar_dados.py`.
- **Alternativa rejeitada:** manter os tipos originais do pandas.
- **Motivo:** a máquina tem 8 GB de RAM. Com os tipos originais, o uso de memória seria maior, sem medição feita.
- **Custo:** `float32` guarda cerca de 7 dígitos significativos. Valores como `TransactionAmt`, com centavos, podem diferir na última casa decimal do CSV original.
- **Medido:** pico de memória de 3,9 GB (footprint), 2,0 GB de RSS. Saída: `data/processed/treino.parquet`, 590.540 linhas e 434 colunas, 84 MB.
