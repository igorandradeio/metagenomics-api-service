from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .seeds import seed_countries


@receiver(post_migrate)
def on_post_migrate(sender, **kwargs):
    # This signal will be triggered after all migrations are applied
    seed_countries()
