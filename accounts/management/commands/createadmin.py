"""
Custom management command to create admin/superuser with full_name field
"""
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from accounts.models import User
import getpass


class Command(BaseCommand):
    help = 'Create a superuser/admin account for Markom system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username for the admin account',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email address',
        )
        parser.add_argument(
            '--fullname',
            type=str,
            help='Full name of the admin',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password (not recommended, use interactive mode)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('  Create Admin Account for Markom System'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write('')

        # Get username
        username = options.get('username')
        if not username:
            username = input('Username: ')
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'❌ User "{username}" already exists!'))
            user = User.objects.get(username=username)
            self.stdout.write(f'   Full name: {user.full_name}')
            self.stdout.write(f'   Email: {user.email}')
            self.stdout.write(f'   Role: {user.get_role_display()}')
            return

        # Get full name
        full_name = options.get('fullname')
        if not full_name:
            full_name = input('Full Name: ')
        
        # Get email
        email = options.get('email')
        if not email:
            email = input('Email (optional, press Enter to skip): ')
        
        # Get password
        password = options.get('password')
        if not password:
            while True:
                password = getpass.getpass('Password: ')
                password_confirm = getpass.getpass('Password (again): ')
                
                if password != password_confirm:
                    self.stdout.write(self.style.ERROR('❌ Passwords do not match. Try again.'))
                    continue
                
                if len(password) < 6:
                    self.stdout.write(self.style.ERROR('❌ Password must be at least 6 characters.'))
                    continue
                
                break

        # Create superuser
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email or '',
                password=password,
                full_name=full_name,
                role=User.Role.ADMIN
            )
            
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('='*60))
            self.stdout.write(self.style.SUCCESS('✅ Admin account created successfully!'))
            self.stdout.write(self.style.SUCCESS('='*60))
            self.stdout.write('')
            self.stdout.write(f'   Username: {user.username}')
            self.stdout.write(f'   Full name: {user.full_name}')
            self.stdout.write(f'   Email: {user.email or "(not set)"}')
            self.stdout.write(f'   Role: {user.get_role_display()}')
            self.stdout.write(f'   Superuser: Yes')
            self.stdout.write(f'   Staff: Yes')
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('⚠️  Remember your password! You can now login to:'))
            self.stdout.write('   - Admin panel: /admin')
            self.stdout.write('   - Dashboard: /dashboard')
            self.stdout.write('')
            
        except ValidationError as e:
            self.stdout.write(self.style.ERROR(f'❌ Validation error: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error creating admin: {e}'))
