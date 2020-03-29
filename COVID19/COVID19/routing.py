from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import apisv1.routing

application = ProtocolTypeRouter({
'websocket': AuthMiddlewareStack(
        URLRouter(
            apisv1.routing.websocket_urlpatterns
        )
    ),
})
