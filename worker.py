from persica.applicationbuilder import ApplicationBuilder
from persica.context.application import ApplicationContext

from src.core.web_app import WebApp

application = (
    ApplicationBuilder()
    .set_application_context_class(ApplicationContext)
    .set_scanner_packages(["src.core", "src.api", "src.route"])
    .build()
)
application.context.run()
application.loop.create_task(application.initialize())
web_app: WebApp = application.factory.get_object(WebApp)
app = web_app.app
