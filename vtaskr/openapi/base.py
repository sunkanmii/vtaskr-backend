from .api_registry import OpenApiRegistry

openapi = OpenApiRegistry()

if openapi.infos is None:
    infos = {
        "title": "vTaskr",
        "description": "vTaskr is an open-source Task/Todo list manager",
        "contact": {
            "name": "Valbou vTaskr API Support",
            "url": "http://www.valbou.fr/contact",
            "email": "contact@valbou.fr",
        },
        "license": {
            "name": "LGPL v3",
            "url": "https://www.gnu.org/licenses/lgpl-3.0.en.html",
        },
        "version": "1.0.0",
    }
    openapi.register_infos(infos)

    openapi.register_server("https://api.vtaskr.com", "Production API")
    openapi.register_server("https://test-api.vtaskr.com", "Test API")
