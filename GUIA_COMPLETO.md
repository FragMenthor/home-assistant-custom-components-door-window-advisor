# Door/Window Advisor - Guia Completo

## 🔧 Instalação

1. Extrair na pasta `custom_components/`:
   ```bash
   unzip door_window_advisor.zip -d ~/.homeassistant/custom_components/
   ```

2. Reiniciar Home Assistant

3. Adicionar integração em Definições → Dispositivos e Serviços

## ✅ Motivos Gramaticalmente Corretos

Os motivos **NÃO repetem o verbo**:

- ✓ "Devo ABRIR porque **para deixar sair o ar quente e húmido**."
- ✓ "Devo MANTER porque **condições confortáveis**."
- ✓ "Devo FECHAR porque **por vento forte**."

## 🎯 Lógica de Decisão

Usa **Enthalpy** (h = T + 0.24*T*(RH/100) + 2.5*(RH/100)) para avaliar conforto combinando temperatura e humidade.

- **Interior confortável** → MANTER
- **Interior pior que exterior** → ABRIR (se fechado)
- **Interior melhor que exterior** → FECHAR ou MANTER
- **Vento > 25 km/h** → FECHAR (se aberto)

## 📊 Exemplo de Template

```jinja2
{% set advisor = states('sensor.door_window_advisor_sala_jantar') %}
{% set reason = state_attr('sensor.door_window_advisor_sala_jantar', 'reason') %}

Devo {{ advisor | lower }} porque {{ reason }}.
```

## 📚 Documentação

Ver `MOTIVOS_REFERENCIA.md` para lista completa de motivos.

## ⚙️ Parâmetros Configuráveis

- `target_temp`: Temperatura alvo (padrão: 22°C)
- `target_hum`: Humidade alvo (padrão: 55%)
- `state_open`: Personalizar texto para ABRIR
- `state_close`: Personalizar texto para FECHAR
- `state_keep`: Personalizar texto para MANTER

Tudo pode ser ajustado nas Opções da integração!
