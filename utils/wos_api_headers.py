"""Shared HTTP headers for WOS Century Game player APIs."""

WOS_GIFTCODE_WEB_ORIGIN = "https://wos-giftcode.centurygame.com"
WOS_PLAYER_API_URL = "https://wos-giftcode-api.centurygame.com/api/player"

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def wos_giftcode_api_post_headers() -> dict:
    """Browser-like headers for wos-giftcode-api.centurygame.com (player / captcha / gift_code)."""
    return {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/x-www-form-urlencoded",
        "origin": WOS_GIFTCODE_WEB_ORIGIN,
        "referer": f"{WOS_GIFTCODE_WEB_ORIGIN}/",
        "user-agent": _USER_AGENT,
    }


def wos_other_century_player_post_headers() -> dict:
    """Minimal browser headers for other Century Game player endpoints (e.g. gof-report)."""
    return {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": _USER_AGENT,
    }
