from django.core.management.base import BaseCommand
from chats.models import CustomUser, Conversation, Message
from faker import Faker
from random import choice

class Command(BaseCommand):
    help = 'Seeds the database with random users, conversations, and messages'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Create random users ensuring no duplicate usernames
        for _ in range(5):  # Create 5 users
            username = fake.user_name()

            # Ensure username is unique
            while CustomUser.objects.filter(username=username).exists():
                username = fake.user_name()  # Generate a new one if the username exists

            user = CustomUser.objects.create_user(
                username=username, 
                email=fake.email(), 
                password="password123"
            )

        # Create random conversations
        users = list(CustomUser.objects.all())  # Get all custom users
        for _ in range(3):  # Create 3 conversations
            participants = [choice(users), choice(users)]
            conversation = Conversation.objects.create()
            conversation.participants.set(participants)
            conversation.save()

        # Create random messages
        conversations = list(Conversation.objects.all())
        for conversation in conversations:
            for _ in range(2):  # 2 messages per conversation
                sender = choice(conversation.participants.all())
                Message.objects.create(
                    conversation=conversation, 
                    sender=sender, 
                    message_body=fake.text()
                )

        self.stdout.write(self.style.SUCCESS("Database seeded with random data"))
