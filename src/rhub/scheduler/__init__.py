import logging

import flask
import injector
from flask_apscheduler import APScheduler


logger = logging.getLogger(__name__)


class SchedulerModule(injector.Module):
    def __init__(self, app):
        self.app = app

    def configure(self, binder):
        binder.bind(
            APScheduler,
            to=self._create_scheduler(),
            scope=injector.singleton,
        )

    def _create_scheduler(self):
        sched = APScheduler()
        sched.init_app(self.app)

        if flask.helpers.get_debug_flag():
            logger.warning('Not starting scheduler, Flask debug is enabled.')
        else:
            sched.start()

        @sched.task('interval', id='rhub_scheduler', seconds=1, max_instances=1)
        def rhub_scheduler():
            from rhub.scheduler import worker
            with self.app.app_context():
                worker.run()

        return sched
