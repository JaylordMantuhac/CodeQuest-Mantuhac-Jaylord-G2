from django.core.management.base import BaseCommand

from accounts.models import User
from challenges.models import Challenge


CHALLENGE_TOPICS = [
    ('variables', 'Variables'), ('conditions', 'Conditions'),
    ('loops', 'Loops'), ('functions', 'Functions'),
]


class Command(BaseCommand):
    help = 'Create the reviewed starter challenge collection.'

    def handle(self, *args, **options):
        admin = User.objects.filter(role=User.ROLE_ADMIN).order_by('id').first()
        if admin is None:
            self.stderr.write('Create an admin account before seeding challenges.')
            return

        created = 0
        for index in range(1, 31):
            category, category_label = CHALLENGE_TOPICS[(index - 1) % len(CHALLENGE_TOPICS)]
            difficulty = ('easy', 'medium', 'hard')[(index - 1) % 3]
            _, was_created = Challenge.objects.get_or_create(
                title=f'{category_label} Practice {index}',
                defaults={
                    'description': f'Write a Python solution that demonstrates {category_label.lower()} concepts in practice exercise {index}.',
                    'category': category, 'difficulty': difficulty, 'language': 'Python',
                    'expected_output': f'CodeQuest answer {index}', 'created_by': admin,
                },
            )
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f'{created} challenges created; collection is ready.'))
