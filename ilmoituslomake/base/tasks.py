from huey import crontab

from management.commands.import_ontology_words import (
    Command as ImportOntologyWordsCommand,
)

# TODO: Untested
@huey.periodic_task(crontab(hour="4"), retries=3, retry_delay=30)
def import_ontology_words():
    cmd = ImportOntologyWordsCommand()
    cmd.handle()
