DOMAIN = "door_window_advisor"

# Configuração
CONF_NAME = "name"
CONF_ENTITY_TYPE = "entity_type"
CONF_INDOOR_TEMP = "indoor_temp"
CONF_OUTDOOR_TEMP = "outdoor_temp"
CONF_INDOOR_HUM = "indoor_hum"
CONF_OUTDOOR_HUM = "outdoor_hum"
CONF_CONTACT = "contact"
CONF_WIND_SPEED = "wind_speed"

CONF_TARGET_TEMP = "target_temp"
CONF_TARGET_HUM = "target_hum"
CONF_TOL_TEMP = "tol_temp"
CONF_TOL_HUM = "tol_hum"

CONF_STATE_OPEN = "state_open"
CONF_STATE_CLOSE = "state_close"
CONF_STATE_KEEP = "state_keep"

# Tipos de entidade
TYPE_DOOR = "door"
TYPE_WINDOW = "window"

# Ícones para Porta
ICON_DOOR_OPEN = "mdi:door-open"
ICON_DOOR_CLOSE = "mdi:door"
ICON_DOOR_KEEP = "mdi:check-circle"

# Ícones para Janela
ICON_WINDOW_OPEN = "mdi:window-open-variant"
ICON_WINDOW_CLOSE = "mdi:window-closed-variant"
ICON_WINDOW_KEEP = "mdi:check-circle"

# Defaults
DEFAULT_NAME = "Door/Window Advisor"
DEFAULT_TARGET_TEMP = 22.0
DEFAULT_TARGET_HUM = 55.0
DEFAULT_TOL_TEMP = 3.5
DEFAULT_TOL_HUM = 15.0

DEFAULT_STATE_OPEN = "ABRIR"
DEFAULT_STATE_CLOSE = "FECHAR"
DEFAULT_STATE_KEEP = "MANTER"

# Atributos
ATTR_REASON = "reason"
ATTR_RECOMMENDATION = "recommendation"
ATTR_INDOOR_TEMP = "indoor_temp"
ATTR_OUTDOOR_TEMP = "outdoor_temp"
ATTR_INDOOR_HUM = "indoor_hum"
ATTR_OUTDOOR_HUM = "outdoor_hum"
ATTR_CONTACT_STATE = "contact_state"
ATTR_WIND_SPEED = "wind_speed"
ATTR_ENTHALPY_INT = "enthalpy_indoor"
ATTR_ENTHALPY_EXT = "enthalpy_outdoor"
ATTR_ENTHALPY_TARGET = "enthalpy_target"
ATTR_OVERALL_SCORE = "overall_score"
ATTR_CONFIDENCE = "confidence"

STATE_OPEN = "ABRIR"
STATE_CLOSE = "FECHAR"
STATE_KEEP = "MANTER"
