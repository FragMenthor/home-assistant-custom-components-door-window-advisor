from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import re
import os
import json
import logging

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.core import Event, State

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_ENTITY_TYPE,
    CONF_INDOOR_TEMP,
    CONF_OUTDOOR_TEMP,
    CONF_INDOOR_HUM,
    CONF_OUTDOOR_HUM,
    CONF_CONTACT,
    CONF_WIND_SPEED,
    CONF_TARGET_TEMP,
    CONF_TARGET_HUM,
    CONF_STATE_OPEN,
    CONF_STATE_CLOSE,
    CONF_STATE_KEEP,
    TYPE_DOOR,
    TYPE_WINDOW,
    ICON_DOOR_OPEN,
    ICON_DOOR_CLOSE,
    ICON_DOOR_KEEP,
    ICON_WINDOW_OPEN,
    ICON_WINDOW_CLOSE,
    ICON_WINDOW_KEEP,
    ATTR_REASON,
    ATTR_INDOOR_TEMP,
    ATTR_OUTDOOR_TEMP,
    ATTR_INDOOR_HUM,
    ATTR_OUTDOOR_HUM,
    ATTR_CONTACT_STATE,
    ATTR_WIND_SPEED,
    ATTR_ENTHALPY_INT,
    ATTR_ENTHALPY_EXT,
    ATTR_ENTHALPY_TARGET,
    ATTR_CONFIDENCE,
    DEFAULT_STATE_OPEN,
    DEFAULT_STATE_CLOSE,
    DEFAULT_STATE_KEEP,
)

_LOGGER = logging.getLogger(__name__)

# Mapeamento de motivos para textos padrÃ£o (fallback - EN)
REASON_FALLBACK_EN = {
    "reason_insufficient_indoor_data": "Insufficient indoor data",
    "reason_comfortable_conditions": "Comfortable conditions",
    "reason_insufficient_outdoor_data": "Insufficient outdoor data",
    "reason_strong_wind": "Strong wind detected",
    "reason_already_open_hot": "Already open, allowing hot and humid air to exit",
    "reason_open_hot": "Open to let hot and humid air exit",
    "reason_close_hotter": "Close to avoid even hotter air entering",
    "reason_keep_hot": "Keep closed to avoid hotter air entering",
    "reason_already_open_warm": "Already open, allowing warmer air to enter",
    "reason_open_warm": "Open to let warmer air enter",
    "reason_close_cold": "Close to conserve indoor heat",
    "reason_keep_cold": "Keep closed to conserve indoor heat",
}

# Mapeamento de motivos para textos padrÃ£o (fallback - PT)
REASON_FALLBACK_PT = {
    "reason_insufficient_indoor_data": "Dados interiores insuficientes",
    "reason_comfortable_conditions": "CondiÃ§Ãµes confortÃ¡veis",
    "reason_insufficient_outdoor_data": "Dados exteriores insuficientes",
    "reason_strong_wind": "Vento forte detectado",
    "reason_already_open_hot": "JÃ¡ estÃ¡ aberta permitindo saÃ­da do ar quente e hÃºmido",
    "reason_open_hot": "Abrir para deixar sair o ar quente e hÃºmido",
    "reason_close_hotter": "Fechar para evitar entrada de ar ainda mais quente",
    "reason_keep_hot": "Manter fechada para evitar entrada de ar mais quente",
    "reason_already_open_warm": "JÃ¡ estÃ¡ aberta permitindo entrada do ar mais quente",
    "reason_open_warm": "Abrir para deixar entrar o ar mais quente",
    "reason_close_cold": "Fechar para conservar o calor interior",
    "reason_keep_cold": "Manter fechada para conservar o calor interior",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Config entry setup."""
    entity = DoorWindowAdvisorSensor(hass, entry)
    async_add_entities([entity], True)


def _slugify_name(name: str) -> str:
    """Converter nome para slug (ex: 'Porta da Cozinha' -> 'porta_da_cozinha')."""
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9\s]", "", slug)
    slug = re.sub(r"\s+", "_", slug)
    slug = re.sub(r"_+", "_", slug)
    return slug.strip("_")


@dataclass
class EnvSample:
    indoor_temp: float | None
    outdoor_temp: float | None
    indoor_hum: float | None
    outdoor_hum: float | None
    contact: str | None
    wind_speed: float | None


class DoorWindowAdvisorSensor(SensorEntity):
    _attr_has_entity_name = False
    _attr_native_unit_of_measurement = None
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.ENUM

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self._entry = entry

        name = entry.data.get(CONF_NAME, "door_window_advisor")
        slug_name = _slugify_name(name)

        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}"
        self.entity_id = f"sensor.{slug_name}_advice"
        
        # Nome amigÃ¡vel serÃ¡ atualizado no async_added_to_hass com a traduÃ§Ã£o correta
        self._base_name = name
        self._attr_name = name
        
        self._state = DEFAULT_STATE_KEEP
        self._attrs: dict[str, Any] = {}
        self._reason_key = "reason_insufficient_indoor_data"
        
        # Cache de traduÃ§Ãµes
        self._translations: dict[str, str] = {}
        self._language = "en"

        self._unsub_listeners: list[callable] = []
        self._unsub_reload = None

    @property
    def _state_options(self) -> list[str]:
        state_open = self._get_config_value(CONF_STATE_OPEN, DEFAULT_STATE_OPEN)
        state_close = self._get_config_value(CONF_STATE_CLOSE, DEFAULT_STATE_CLOSE)
        state_keep = self._get_config_value(CONF_STATE_KEEP, DEFAULT_STATE_KEEP)
        return [state_open, state_close, state_keep]

    @property
    def options(self) -> list[str]:
        return self._state_options

    @property
    def icon(self) -> str:
        entity_type = self._get_config_value(CONF_ENTITY_TYPE, TYPE_WINDOW)
        state_open = self._get_config_value(CONF_STATE_OPEN, DEFAULT_STATE_OPEN)
        state_close = self._get_config_value(CONF_STATE_CLOSE, DEFAULT_STATE_CLOSE)
        state_keep = self._get_config_value(CONF_STATE_KEEP, DEFAULT_STATE_KEEP)

        if entity_type == TYPE_DOOR:
            if self._state == state_open:
                return ICON_DOOR_OPEN
            if self._state == state_close:
                return ICON_DOOR_CLOSE
            return ICON_DOOR_KEEP
        else:
            if self._state == state_open:
                return ICON_WINDOW_OPEN
            if self._state == state_close:
                return ICON_WINDOW_CLOSE
            return ICON_WINDOW_KEEP

    async def async_added_to_hass(self) -> None:
        await self._update_friendly_name()
        await self._load_translations()
        self._register_listeners()
        self._unsub_reload = self._entry.add_update_listener(self._async_config_updated)
        self._recompute()

    async def _update_friendly_name(self) -> None:
        """Atualizar nome amigÃ¡vel com traduÃ§Ã£o de 'Conselho'/'Advice'."""
        try:
            lang = (self.hass.config.language or "en").lower()
            self._language = lang
            
            if lang.startswith("pt"):
                suffix = "Conselho"
            else:
                suffix = "Advice"
        except Exception:
            suffix = "Advice"
        
        self._attr_name = f"{self._base_name} {suffix}"

    async def _load_translations(self) -> None:
        """Carregar todas as traduÃ§Ãµes de motivos do translations/pt.json ou strings.json."""
        try:
            lang = (self.hass.config.language or "en").lower()
            self._language = lang
            
            # Determinar caminho do ficheiro de traduÃ§Ã£o
            integration_dir = os.path.dirname(__file__)
            
            if lang.startswith("pt"):
                # PT: translations/pt.json
                file_path = os.path.join(integration_dir, "translations", "pt.json")
                _LOGGER.debug(f"[door_window_advisor] Loading PT translations from: {file_path}")
            else:
                # EN: strings.json
                file_path = os.path.join(integration_dir, "strings.json")
                _LOGGER.debug(f"[door_window_advisor] Loading EN translations from: {file_path}")
            
            # Tentar carregar o ficheiro JSON
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    if "reasons" in data:
                        self._translations = data["reasons"]
                        _LOGGER.debug(f"[door_window_advisor] Loaded {len(self._translations)} translations from {file_path}")
                        return
                except (json.JSONDecodeError, IOError) as e:
                    _LOGGER.error(f"[door_window_advisor] Error loading translations from {file_path}: {e}")
            else:
                _LOGGER.warning(f"[door_window_advisor] Translation file not found: {file_path}")
        
        except Exception as e:
            _LOGGER.error(f"[door_window_advisor] Error in _load_translations: {e}")
        
        # Fallback: usar o dicionÃ¡rio padrÃ£o conforme idioma
        if self._language.startswith("pt"):
            self._translations = REASON_FALLBACK_PT
            _LOGGER.debug("[door_window_advisor] Using fallback PT translations")
        else:
            self._translations = REASON_FALLBACK_EN
            _LOGGER.debug("[door_window_advisor] Using fallback EN translations")

    async def _async_config_updated(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        await self._load_translations()
        self._register_listeners()
        self._recompute()

    def _register_listeners(self) -> None:
        for unsub in self._unsub_listeners:
            unsub()
        self._unsub_listeners.clear()

        config = self._entry.data
        options = self._entry.options

        ent_ids = [
            options.get(CONF_INDOOR_TEMP, config.get(CONF_INDOOR_TEMP)),
            options.get(CONF_OUTDOOR_TEMP, config.get(CONF_OUTDOOR_TEMP)),
            options.get(CONF_INDOOR_HUM, config.get(CONF_INDOOR_HUM)),
            options.get(CONF_OUTDOOR_HUM, config.get(CONF_OUTDOOR_HUM)),
            options.get(CONF_CONTACT, config.get(CONF_CONTACT)),
        ]
        wind_speed = options.get(CONF_WIND_SPEED, config.get(CONF_WIND_SPEED))
        if wind_speed:
            ent_ids.append(wind_speed)

        @callback
        def _state_changed(event: Event) -> None:
            self._recompute()

        for eid in ent_ids:
            if not eid:
                continue
            unsub = async_track_state_change_event(self.hass, [eid], _state_changed)
            self._unsub_listeners.append(unsub)

    async def async_will_remove_from_hass(self) -> None:
        for unsub in self._unsub_listeners:
            unsub()
        self._unsub_listeners.clear()
        if self._unsub_reload:
            self._unsub_reload()

    @property
    def native_value(self) -> str:
        return self._state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return self._attrs

    def _get_state_float(self, entity_id: str | None) -> float | None:
        if not entity_id:
            return None
        st: State | None = self.hass.states.get(entity_id)
        if st is None or st.state in ("unknown", "unavailable", None):
            return None
        try:
            return float(st.state)
        except (ValueError, TypeError):
            return None

    def _get_state_str(self, entity_id: str | None) -> str | None:
        if not entity_id:
            return None
        st: State | None = self.hass.states.get(entity_id)
        if st is None or st.state in ("unknown", "unavailable", None):
            return None
        return str(st.state)

    def _get_config_value(self, key: str, default: Any = None) -> Any:
        options = self._entry.options
        data = self._entry.data
        return options.get(key, data.get(key, default))

    def _sample(self) -> EnvSample:
        config = self._entry.data
        options = self._entry.options

        indoor_temp = self._get_state_float(options.get(CONF_INDOOR_TEMP, config.get(CONF_INDOOR_TEMP)))
        outdoor_temp = self._get_state_float(options.get(CONF_OUTDOOR_TEMP, config.get(CONF_OUTDOOR_TEMP)))
        indoor_hum = self._get_state_float(options.get(CONF_INDOOR_HUM, config.get(CONF_INDOOR_HUM)))
        outdoor_hum = self._get_state_float(options.get(CONF_OUTDOOR_HUM, config.get(CONF_OUTDOOR_HUM)))
        contact = self._get_state_str(options.get(CONF_CONTACT, config.get(CONF_CONTACT)))
        wind_speed = self._get_state_float(options.get(CONF_WIND_SPEED, config.get(CONF_WIND_SPEED)))

        return EnvSample(indoor_temp, outdoor_temp, indoor_hum, outdoor_hum, contact, wind_speed)

    def _calculate_enthalpy(self, temp: float | None, hum: float | None) -> float | None:
        if temp is None or hum is None:
            return None
        enthalpy = temp + 0.24 * temp * (hum / 100) + 2.5 * (hum / 100)
        return enthalpy

    def _is_contact_open(self, contact_state: str | None) -> bool:
        if contact_state is None:
            return False
        return contact_state.lower() in ("on", "open", "true", "aberto")

    def _translate_reason(self, reason_key: str) -> str:
        """Traduzir chave de motivo usando as traduÃ§Ãµes carregadas."""
        # Procurar no dicionÃ¡rio de traduÃ§Ãµes carregado
        if reason_key in self._translations:
            translated = self._translations[reason_key]
            _LOGGER.debug(f"[door_window_advisor] Translated '{reason_key}' to '{translated}'")
            return translated
        
        # Fallback: verificar qual o idioma e retornar o fallback apropriado
        if self._language.startswith("pt"):
            fallback = REASON_FALLBACK_PT.get(reason_key, reason_key)
        else:
            fallback = REASON_FALLBACK_EN.get(reason_key, reason_key)
        
        _LOGGER.warning(f"[door_window_advisor] No translation found for '{reason_key}', using fallback: '{fallback}'")
        return fallback

    def _decision_logic(self, env: EnvSample) -> tuple[str, str, dict[str, Any]]:
        state_open = self._get_config_value(CONF_STATE_OPEN, DEFAULT_STATE_OPEN)
        state_close = self._get_config_value(CONF_STATE_CLOSE, DEFAULT_STATE_CLOSE)
        state_keep = self._get_config_value(CONF_STATE_KEEP, DEFAULT_STATE_KEEP)

        tgt_t = float(self._get_config_value(CONF_TARGET_TEMP, 22.0))
        tgt_h = float(self._get_config_value(CONF_TARGET_HUM, 55.0))

        h_int = self._calculate_enthalpy(env.indoor_temp, env.indoor_hum)
        h_ext = self._calculate_enthalpy(env.outdoor_temp, env.outdoor_hum)
        h_target = self._calculate_enthalpy(tgt_t, tgt_h)
        is_open = self._is_contact_open(env.contact)

        if h_int is None or env.indoor_temp is None or env.indoor_hum is None:
            reason_key = "reason_insufficient_indoor_data"
            return state_keep, reason_key, {
                "h_int": h_int,
                "h_ext": h_ext,
                "h_target": h_target,
                "confidence": "BAIXA",
            }

        if abs(h_int - h_target) <= 2.0:
            # Condições confortáveis, mas se está aberta, fechar para manter
            if is_open:
                reason_key = "reason_close_cold"
                return state_close, reason_key, {
                    "h_int": round(h_int, 2),
                    "h_ext": round(h_ext, 2) if h_ext else None,
                    "h_target": round(h_target, 2),
                    "confidence": "ALTA",
                }
            reason_key = "reason_comfortable_conditions"
            return state_keep, reason_key, {
                "h_int": round(h_int, 2),
                "h_ext": round(h_ext, 2) if h_ext else None,
                "h_target": round(h_target, 2),
                "confidence": "ALTA",
            }

        if h_ext is None or env.outdoor_temp is None or env.outdoor_hum is None:
            reason_key = "reason_insufficient_outdoor_data"
            return state_keep, reason_key, {
                "h_int": round(h_int, 2),
                "h_ext": None,
                "h_target": round(h_target, 2),
                "confidence": "BAIXA",
            }

        delta_int = h_int - h_target
        delta_ext = h_ext - h_target

        if env.wind_speed and env.wind_speed > 25.0:
            reason_key = "reason_strong_wind"
            if is_open:
                return state_close, reason_key, {
                    "h_int": round(h_int, 2),
                    "h_ext": round(h_ext, 2),
                    "h_target": round(h_target, 2),
                    "wind_speed": round(env.wind_speed, 1),
                    "confidence": "ALTA",
                }
            return state_keep, reason_key, {
                "h_int": round(h_int, 2),
                "h_ext": round(h_ext, 2),
                "h_target": round(h_target, 2),
                "wind_speed": round(env.wind_speed, 1),
                "confidence": "ALTA",
            }

        if delta_int > 0:
            if delta_ext < delta_int:
                if is_open:
                    reason_key = "reason_already_open_hot"
                    return state_keep, reason_key, {
                        "h_int": round(h_int, 2),
                        "h_ext": round(h_ext, 2),
                        "h_target": round(h_target, 2),
                        "confidence": "ALTA",
                    }
                reason_key = "reason_open_hot"
                return state_open, reason_key, {
                    "h_int": round(h_int, 2),
                    "h_ext": round(h_ext, 2),
                    "h_target": round(h_target, 2),
                    "confidence": "ALTA",
                }
            if is_open:
                reason_key = "reason_close_hotter"
                return state_close, reason_key, {
                    "h_int": round(h_int, 2),
                    "h_ext": round(h_ext, 2),
                    "h_target": round(h_target, 2),
                    "confidence": "ALTA",
                }
            reason_key = "reason_keep_hot"
            return state_keep, reason_key, {
                "h_int": round(h_int, 2),
                "h_ext": round(h_ext, 2),
                "h_target": round(h_target, 2),
                "confidence": "ALTA",
            }

        if delta_ext > delta_int:
            if is_open:
                reason_key = "reason_already_open_warm"
                return state_keep, reason_key, {
                    "h_int": round(h_int, 2),
                    "h_ext": round(h_ext, 2),
                    "h_target": round(h_target, 2),
                    "confidence": "ALTA",
                }
            reason_key = "reason_open_warm"
            return state_open, reason_key, {
                "h_int": round(h_int, 2),
                "h_ext": round(h_ext, 2),
                "h_target": round(h_target, 2),
                "confidence": "ALTA",
            }

        if is_open:
            reason_key = "reason_close_cold"
            return state_close, reason_key, {
                "h_int": round(h_int, 2),
                "h_ext": round(h_ext, 2),
                "h_target": round(h_target, 2),
                "confidence": "ALTA",
            }
        reason_key = "reason_keep_cold"
        return state_keep, reason_key, {
            "h_int": round(h_int, 2),
            "h_ext": round(h_ext, 2),
            "h_target": round(h_target, 2),
            "confidence": "ALTA",
        }

    @callback
    def _recompute(self) -> None:
        env = self._sample()
        state, reason_key, scores = self._decision_logic(env)

        self._state = state
        
        # Traduzir a chave do motivo para o texto localizado
        reason_text = self._translate_reason(reason_key)

        self._attrs = {
            ATTR_REASON: reason_text,  # âœ… Mostra o texto traduzido
            ATTR_INDOOR_TEMP: env.indoor_temp,
            ATTR_OUTDOOR_TEMP: env.outdoor_temp,
            ATTR_INDOOR_HUM: env.indoor_hum,
            ATTR_OUTDOOR_HUM: env.outdoor_hum,
            ATTR_CONTACT_STATE: env.contact,
            ATTR_WIND_SPEED: env.wind_speed,
            ATTR_ENTHALPY_INT: scores.get("h_int"),
            ATTR_ENTHALPY_EXT: scores.get("h_ext"),
            ATTR_ENTHALPY_TARGET: scores.get("h_target"),
            ATTR_CONFIDENCE: scores.get("confidence", "BAIXA"),
        }

        self.async_write_ha_state()