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
- **Decisão (proposta do Claude, aceita pelo Éric):** colunas `float64` viram `float32`, `int64` viram o menor inteiro que cabe, e textos com poucos valores viram `category`. Implementado em `src/preparar_dados.py`.
- **Alternativa rejeitada:** manter os tipos originais do pandas.
- **Motivo:** a máquina tem 8 GB de RAM. Com os tipos originais, o uso de memória seria maior, sem medição feita.
- **Custo:** `float32` guarda cerca de 7 dígitos significativos. Valores como `TransactionAmt`, com centavos, podem diferir na última casa decimal do CSV original.
- **Medido:** pico de memória de 3,9 GB (footprint), 2,0 GB de RSS. Saída: `data/processed/treino.parquet`, 590.540 linhas e 434 colunas, 84 MB.

## Etapa 1: exploração

### D5. Dados usados na exploração
- **Decisão (escolha do Éric):** estrutura e ausentes na base inteira. Tudo que envolve `isFraud` ou compara fraudes usa só os primeiros 60% no tempo, com corte provisório por quantil de `TransactionDT`.
- **Alternativas rejeitadas:**
  - Base inteira: exporia padrões de fraude do período de teste.
  - Só os primeiros 60%: não mostraria mudanças nas variáveis ao longo do tempo.
- **Motivo:** protege o teste e ainda mostra mudanças ao longo do tempo. Justificativa proposta pelo Claude. O Éric escolheu a opção sem escrever um motivo próprio.
- **Limite:** o corte provisório não substitui a divisão temporal da Etapa 2.

### D6. Formato da exploração
- **Decisão (escolha do Éric):** notebook em `notebooks/01_exploracao.ipynb`, executado do início ao fim antes de cada entrega.
- **Alternativa rejeitada:** script com figuras em `reports/figures`, que versiona melhor, mas espalha a análise e é menos legível.
- **Motivo:** código, gráficos e interpretação ficam juntos. Justificativa proposta pelo Claude. O Éric escolheu a opção sem escrever um motivo próprio.

## Organização do trabalho

### D7. Divisão do código entre o Éric e o Claude
- **Decisão (escolha do Éric, 09/11/2026):** o Éric escreve só a divisão temporal e a métrica de valor capturado, em passos guiados e com testes. O Claude escreve o limiar e o restante do código. Isso altera a divisão original do `CLAUDE.local.md`, em que o limiar também era do Éric.
- **Alternativas rejeitadas:**
  - O Claude escrever todo o código e o Éric revisar e explicar: menos risco no prazo, mas quase sem prática de código e mais exposição a um pedido de alteração ao vivo.
  - Manter a divisão original e reduzir o escopo do projeto: simplifica o conteúdo, mas não resolve a dificuldade com código.
- **Motivo:** o Éric disse que o projeto está distante do seu nível e que não conseguiria produzir à mão códigos tão complexos. Justificativa da opção proposta pelo Claude: é pouco código e deixa uma parte que o Éric pode defender na entrevista. O Éric escolheu a opção sem escrever um motivo próprio.
- **Plano B:** se o Éric travar nessas peças, o Claude passa a escrever tudo (alternativa acima). O prazo de 10/11 continua valendo.

### D10. Um notebook por etapa
- **Decisão (escolha do Éric, provisória):** manter um notebook separado para cada etapa durante o projeto. Na Etapa 8, o Éric e o Claude reavaliam se a apresentação do portfólio fica assim ou unificada.
- **Alternativa rejeitada por enquanto:** um único notebook com todas as etapas, mais direto de apresentar, mas pesado para 8 GB de RAM e sujeito a misturar variáveis entre etapas.
- **Motivo:** justificativa proposta pelo Claude: cada etapa roda sozinha, economiza memória e reduz o risco de usar uma variável de outra etapa. O Éric aceitou manter e deixou a forma final para a reavaliação na Etapa 8.
- **Origem:** os notebooks 02 a 04 foram criados separados por escolha do Claude, antes de essa decisão ser apresentada.

## Etapa 2: validação temporal

### D8. Forma do corte temporal
- **Decisão (escolha do Éric, 09/11/2026):** dividir por quantidade de transações, com 60% em treino, 20% em validação e 20% em teste, nessa ordem no tempo. Os cortes caem nos dias 101,2 e 141,1. São 354.324 transações no treino, 118.108 na validação e 118.108 no teste.
- **Alternativas rejeitadas:**
  - Dividir por dias do calendário: períodos de duração equivalente, mas não é 60/20/20 em linhas (64,5% no treino), e parte do treino não foi vista na exploração.
  - Dividir por quantidade com um intervalo descartado antes da validação e do teste: mais próxima da operação real, mas perde dados (39.307 transações com 7 dias, 177.843 com 30 dias), e o tamanho do intervalo seria uma premissa.
- **Motivo:** mais simples de escrever e explicar, e o treino fica igual ao trecho usado na exploração (D5). Justificativa proposta pelo Claude. O Éric escolheu a opção sem escrever um motivo próprio.
- **Limites:** o teste vem logo depois do treino, como se o rótulo de fraude saísse na hora, embora ele só seja conhecido depois. As colunas V e D vêm pré-calculadas, e não dá para auditar se usam informação futura.

## Etapa 3: baseline

### D9. Colunas da regressão logística
- **Decisão (escolha do Éric, 09/11/2026):** usar `TransactionAmt`, `ProductCD`, `card4`, `card6`, uma marca de "tem identidade" e as 14 colunas C. O outro baseline é a regra de revisar as compras de maior valor.
- **Alternativas rejeitadas:**
  - Só as colunas básicas, sem as C: mais simples, mas seria uma régua fraca e favoreceria o LightGBM na comparação.
  - Básicas, colunas C e as 15 colunas D: régua mais exigente, mas as colunas D têm muitos vazios e não dá para auditar se usam informação futura.
  - Quase todas as colunas numéricas, incluindo as 339 V: pesada para 8 GB, difícil de explicar e deixa de ser um baseline simples.
- **Motivo:** as colunas C não têm vazios, então deixam a régua mais justa sem exigir tratamento. Justificativa proposta pelo Claude. O Éric seguiu a recomendação sem escrever um motivo próprio.
- **Limite:** a marca de identidade muda entre treino e validação (27,47% e 19,60% das transações com identidade), o que pode reduzir o desempenho fora do treino.
- **Correção:** a recomendação foi inconsistente. As colunas D foram rejeitadas por não dar para auditar se usam informação futura, mas as colunas C também vêm pré-calculadas pela Vesta e têm o mesmo limite. O desempenho da logística pode estar inflado por isso.

## Etapa 4: variáveis

### D11. Colunas C no modelo principal
- **Decisão (escolha do Éric, 10/11/2026):** treinar o LightGBM com e sem as colunas C e apresentar os dois resultados. Fazer também uma checagem de indício de uso do futuro nas colunas C.
- **Alternativas rejeitadas:**
  - Manter as colunas C sem comparação: melhor desempenho, mas, se houver vazamento, o resultado não se repetiria em produção e não teria defesa.
  - Retirar as colunas C: mais defensável, mas com desempenho bem menor.
- **Motivo:** o Éric primeiro escolheu manter as colunas C porque as métricas são melhores. O Claude apontou que um vazamento também melhoraria as métricas, então elas não distinguem sinal real de informação futura. O Éric então escolheu a opção recomendada, sem escrever um motivo próprio.
- **Evidência:** na regressão logística, a PR-AUC na validação é 0,4357 com as colunas C e 0,1351 sem elas.

### D12. Agregações por cartão
- **Decisão (escolha do Éric, 10/11/2026):** testar no LightGBM as agregações com a chave `card1` a `card6` + `addr1` contra a versão sem agregações. Somada à D11, a Etapa 5 treina quatro versões: com e sem colunas C, com e sem agregações.
- **Alternativas rejeitadas:**
  - Não usar agregações: mais simples, mas descartaria sem teste no modelo principal algo previsto no plano.
  - Usar as agregações sem comparar: mais rápido, mas não mostraria se elas ajudam.
- **Motivo:** a chave com `addr1` é a mais próxima de um cartão real (39.087 grupos, maior grupo com 8.081 transações sem o teste), e o teste usa o modelo que será apresentado. Justificativa proposta pelo Claude. O Éric escolheu a opção sem escrever um motivo próprio.
- **Evidência:** na regressão logística com colunas C, as agregações quase não mudaram o resultado. A PR-AUC foi de 0,4357 sem agregações para valores entre 0,4303 e 0,4337 com elas.
- **Limite:** nenhuma chave identifica um cartão real. O maior grupo ainda mistura muitos clientes.
