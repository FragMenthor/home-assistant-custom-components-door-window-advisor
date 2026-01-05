# 📦 Door/Window Advisor v1.2.0 - INTEGRAÇÃO COMPLETA

## ✨ NOVIDADES v1.2.0

✅ **Entity ID Personalizado** - `sensor.advice_[slug_do_nome]`
   - "Porta Cozinha" → `sensor.advice_porta_cozinha`
   - "Janela Sala" → `sensor.advice_janela_sala`

✅ **Nome Obrigatório** - Utilizador preenche de raiz
   - Sem valor default na configuração
   - Nome fica como "friendly name" no Home Assistant

✅ **Seletor de Tipo** - Porta ou Janela
   - Ícones dinâmicos conforme tipo
   - Reconfiguração nas Opções

✅ **Reconfiguração Completa** - Sem reiniciar
   - Alterar sensores, tipo, parâmetros
   - Reload automático

---

## 📁 ESTRUTURA DOS FICHEIROS (Final)

```
door_window_advisor/
├── __init__.py                 ✅ FINAL
├── config_flow.py              ✅ FINAL
├── const.py                    ✅ FINAL
├── sensor.py                   ✅ FINAL
├── manifest.json               ✅ FINAL
├── strings.json                ✅ FINAL
├── translations/
│   ├── en.json                 ✅ FINAL
│   └── pt.json                 ✅ FINAL
└── README.md                   (Documentação)
```

---

## 🚀 COMO INSTALAR

### Opção 1: Extrair ZIP (Recomendado)

1. Descarregar `door_window_advisor_v1.2.0.zip`
2. Extrair para `config/custom_components/`
3. Reiniciar Home Assistant
4. Ir a Definições → Dispositivos e Serviços
5. Criar nova integração "Door/Window Advisor"
6. Preencher nome (obrigatório) e sensores

### Opção 2: Cópia Manual

1. Copiar ficheiros para `custom_components/door_window_advisor/`
2. Ficheiros necessários:
   - `__init__.py`
   - `config_flow.py`
   - `const.py`
   - `sensor.py`
   - `manifest.json`
   - `strings.json`
   - `translations/en.json`
   - `translations/pt.json`
3. Reiniciar Home Assistant

---

## 📊 EXEMPLOS DE UTILIZAÇÃO

### Criar Integração: "Porta Cozinha"

```
Nome: Porta Cozinha
Tipo: Porta ▼
Sensor T Interior: sensor.temperatura_cozinha
Sensor T Exterior: sensor.temperatura_exterior
...

Resultado:
entity_id: sensor.advice_porta_cozinha
Nome amigável: Porta Cozinha
```

### Criar Integração: "Janela Sala Estar"

```
Nome: Janela Sala Estar
Tipo: Janela ▼
...

Resultado:
entity_id: sensor.advice_janela_sala_estar
Nome amigável: Janela Sala Estar
```

---

## 🔧 CAMPOS DO CONFIG FLOW

### Obrigatórios:
- **Nome** - Sem default (utilizador preenche)
- **Tipo** - Porta ou Janela
- **Sensor T Interior** - Entidade sensor
- **Sensor T Exterior** - Entidade sensor
- **Sensor Humidade Interior** - Entidade sensor
- **Sensor Humidade Exterior** - Entidade sensor
- **Sensor Contacto** - Entidade binary_sensor
- **Temperatura Alvo** - Default: 22°C
- **Humidade Alvo** - Default: 55%

### Opcionais:
- **Sensor Vento** - Para deteção de vento forte
- **Estado ABRIR** - Customizar label (default: ABRIR)
- **Estado FECHAR** - Customizar label (default: FECHAR)
- **Estado MANTER** - Customizar label (default: MANTER)

---

## 🎯 ESTADOS POSSÍVEIS

### Sensor State:
- `ABRIR` / `FECHAR` / `MANTER` (customizáveis)

### Sensor Icon:
**Se Porta:**
- ABRIR → 🚪 (mdi:door-open)
- FECHAR → 🚪 (mdi:door)
- MANTER → ≈ (mdi:approximately-equal)

**Se Janela:**
- ABRIR → 🪟 (mdi:window-open-variant)
- FECHAR → 🪟 (mdi:window-closed-variant)
- MANTER → ≈ (mdi:approximately-equal)

### Atributos:
- `reason` - Motivo da recomendação
- `indoor_temp` - Temperatura interior
- `outdoor_temp` - Temperatura exterior
- `indoor_hum` - Humidade interior
- `outdoor_hum` - Humidade exterior
- `contact_state` - Estado do contacto
- `wind_speed` - Velocidade do vento
- `enthalpy_indoor` - Enthalpy interior (kJ/kg)
- `enthalpy_outdoor` - Enthalpy exterior (kJ/kg)
- `enthalpy_target` - Enthalpy alvo (kJ/kg)
- `confidence` - Nível de confiança (ALTA/BAIXA)

---

## 🔄 RECONFIGURAÇÃO NAS OPÇÕES

Clicar no botão ⋮ (três pontos) na integração e selecionar **Opções**:

Pode alterar:
- Tipo de entidade (Porta ↔ Janela)
- Qualquer sensor
- Temperaturas/humidades alvo
- Estados personalizados

Mudanças aplicam-se automaticamente (reload em background).

---

## 📝 LÓGICA DE DECISÃO

A integração usa **enthalpy** para comparar conforto interior vs exterior:

1. **Interior confortável?** → MANTER (não fazer nada)
2. **Interior quente/húmido?** → Comparar com exterior
   - Se exterior melhor → ABRIR
   - Se exterior pior → FECHAR (ou MANTER)
3. **Interior frio/seco?** → Comparar com exterior
   - Se exterior melhor → ABRIR
   - Se exterior pior → FECHAR (ou MANTER)
4. **Vento forte (>25 km/h)?** → FECHAR (segurança)

---

## 🐛 TROUBLESHOOTING

### Sensor não aparece após criar integração
- Verificar Logs (Ferramentas → Logs)
- Confirmar que `config_flow.py` está presente
- Reiniciar Home Assistant

### Entity ID não é `sensor.advice_*`
- Verificar que `sensor.py` tem função `_slugify_name()`
- Confirmar que `_attr_has_entity_name = False`
- Verificar line `self.entity_id = f"sensor.advice_{slug_name}"`

### Nome não é obrigatório no formulário
- Verificar que `config_flow.py` tem `vol.Required(CONF_NAME)` SEM default
- Procurar por `vol.Required(CONF_NAME): str`

### Opções não funcionam
- Verificar se `config_flow.py` tem `DoorWindowAdvisorOptionsFlow`
- Confirmar que `__init__.py` tem `add_update_listener`
- Reiniciar Home Assistant

---

## 📋 CHECKLIST DE VALIDAÇÃO

Após instalar:

- [ ] Ficheiros estão em `custom_components/door_window_advisor/`
- [ ] Home Assistant reiniciou
- [ ] Integração aparece em Dispositivos e Serviços
- [ ] Ao criar, pede NOME (campo obrigatório vazio)
- [ ] Entity ID gerado é `sensor.advice_*`
- [ ] Nome amigável é o fornecido (ex: "Porta Cozinha")
- [ ] Ícone muda com tipo (porta 🚪 ou janela 🪟)
- [ ] Botão Opções funciona
- [ ] Consegue alterar sensores/tipo nas Opções
- [ ] Mudanças aplicam-se sem restart

---

## 🔗 FICHEIROS INCLUÍDOS NO ZIP

```
door_window_advisor_v1.2.0.zip
├── door_window_advisor/
│   ├── __init__.py                (46 linhas)
│   ├── config_flow.py             (193 linhas) ← NOVO
│   ├── const.py                   (78 linhas) ← ATUALIZADO
│   ├── sensor.py                  (328 linhas) ← ATUALIZADO
│   ├── manifest.json              (11 linhas)
│   ├── strings.json               (30+ linhas) ← ATUALIZADO
│   └── translations/
│       ├── en.json                (30+ linhas) ← ATUALIZADO
│       └── pt.json                (30+ linhas) ← ATUALIZADO
│
└── README.md (este ficheiro)
```

---

## 📞 SUPORTE

Para questões/bugs:
1. Verificar Logs (Ferramentas de Desenvolvimento → Logs)
2. Procurar mensagens de erro relacionadas com `door_window_advisor`
3. Confirmar estrutura de ficheiros
4. Reiniciar Home Assistant se tudo mais falhar

---

**Versão**: 1.2.0
**Data**: Janeiro 2026
**Status**: ✅ Pronto para Produção

---

## 🙏 CRÉDITOS

Desenvolvido por: **@FragMenthor**
Baseado em: Logica de conforto com enthalpy e sensores

Sugestões/Melhorias: Bem-vindo feedback!
