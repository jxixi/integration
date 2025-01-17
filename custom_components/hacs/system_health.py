"""Provide info to system health."""
from homeassistant.components import system_health
from homeassistant.core import HomeAssistant, callback

from .base import HacsBase
from .const import DOMAIN, BASE_API_URL

GITHUB_STATUS = "https://www.githubstatus.com/"
CLOUDFLARE_STATUS = "https://www.cloudflarestatus.com/"


@callback
def async_register(hass: HomeAssistant, register: system_health.SystemHealthRegistration) -> None:
    """Register system health callbacks."""
    register.domain = "Home Assistant Community Store"
    register.async_register_info(system_health_info, "/hacs")


async def system_health_info(hass):
    """Get info for the info page."""
    hacs: HacsBase = hass.data[DOMAIN]
    response = await hacs.githubapi.rate_limit()
    api_url = hacs.configuration.github_api_base or BASE_API_URL

    data = {
        "GitHub API": system_health.async_check_can_reach_url(hass, api_url, api_url),
        "GitHub Content": system_health.async_check_can_reach_url(
            hass, "https://ghrp.hacs.vip/raw/hacs/integration/main/hacs.json"
        ),
        "GitHub Web": system_health.async_check_can_reach_url(
            hass, "https://github.com/", GITHUB_STATUS
        ),
        "GitHub API Calls Remaining": response.data.resources.core.remaining,
        "Installed Version": hacs.version,
        "Stage": hacs.stage,
        "Available Repositories": len(hacs.repositories.list_all),
        "Downloaded Repositories": len(hacs.repositories.list_downloaded),
    }

    if hacs.system.disabled:
        data["Disabled"] = hacs.system.disabled_reason

    if hacs.configuration.experimental:
        data["HACS Data"] = system_health.async_check_can_reach_url(
            hass, "https://data-v2.hacs.xyz/data.json", CLOUDFLARE_STATUS
        )

    return data
