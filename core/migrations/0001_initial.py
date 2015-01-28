# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import django.utils.timezone
from django.conf import settings
import django.core.validators
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AtmosphereUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, max_length=30, verbose_name='username', validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.', 'invalid')])),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=75, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
            ],
            options={
                'db_table': 'atmosphere_user',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AccountProvider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'db_table': 'provider_admin',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Allocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('threshold', models.IntegerField(default=10080, null=True, blank=True)),
                ('delta', models.IntegerField(default=525600, null=True, blank=True)),
            ],
            options={
                'db_table': 'allocation',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AllocationRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(default=uuid.uuid4, max_length=36)),
                ('request', models.TextField()),
                ('description', models.CharField(default=b'', max_length=1024, blank=True)),
                ('admin_message', models.CharField(default=b'', max_length=1024, blank=True)),
                ('start_date', models.DateTimeField(default=datetime.datetime(2015, 1, 28, 20, 28, 52, 540784, tzinfo=utc))),
                ('end_date', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'allocation_request',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(default=uuid.uuid4, unique=True, max_length=36)),
                ('name', models.CharField(max_length=256)),
                ('description', models.TextField(null=True, blank=True)),
                ('icon', models.ImageField(null=True, upload_to=b'machine_images', blank=True)),
                ('private', models.BooleanField(default=False)),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_date', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'application',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ApplicationBookmark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('application', models.ForeignKey(related_name='bookmarks', to='core.Application')),
            ],
            options={
                'db_table': 'application_bookmark',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ApplicationMembership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('can_edit', models.BooleanField(default=False)),
                ('application', models.ForeignKey(to='core.Application')),
            ],
            options={
                'db_table': 'application_membership',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ApplicationScore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score', models.IntegerField(default=0)),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_date', models.DateTimeField(null=True, blank=True)),
                ('application', models.ForeignKey(related_name='scores', to='core.Application')),
            ],
            options={
                'db_table': 'application_score',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ApplicationThreshold',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('memory_min', models.IntegerField(default=0)),
                ('storage_min', models.IntegerField(default=0)),
                ('application', models.OneToOneField(related_name='threshold', to='core.Application')),
            ],
            options={
                'db_table': 'application_threshold',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BootScript',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128)),
                ('script_text', models.TextField()),
                ('run_every_deploy', models.BooleanField(default=False)),
                ('applications', models.ManyToManyField(related_name='scripts', to='core.Application')),
            ],
            options={
                'db_table': 'boot_script',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Credential',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=256)),
                ('value', models.CharField(max_length=256)),
            ],
            options={
                'db_table': 'credential',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Flow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alias', models.CharField(max_length=36)),
                ('name', models.CharField(max_length=1024, blank=True)),
                ('status', models.IntegerField(null=True, blank=True)),
                ('start_date', models.DateTimeField(default=datetime.datetime(2015, 1, 28, 20, 28, 52, 537493, tzinfo=utc))),
                ('end_date', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'flow',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FlowType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, blank=True)),
                ('start_date', models.DateTimeField(default=datetime.datetime(2015, 1, 28, 20, 28, 52, 536660, tzinfo=utc))),
                ('end_date', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'flowtype',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('group_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='auth.Group')),
                ('applications', models.ManyToManyField(related_name='members', through='core.ApplicationMembership', to='core.Application', blank=True)),
            ],
            options={
                'db_table': 'group',
            },
            bases=('auth.group',),
        ),
        migrations.CreateModel(
            name='Identity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(default=uuid.uuid4, unique=True, max_length=36)),
            ],
            options={
                'db_table': 'identity',
                'verbose_name_plural': 'identities',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IdentityMembership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('allocation', models.ForeignKey(blank=True, to='core.Allocation', null=True)),
                ('identity', models.ForeignKey(to='core.Identity')),
                ('member', models.ForeignKey(to='core.Group')),
            ],
            options={
                'db_table': 'identity_membership',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('token', models.CharField(max_length=36, null=True, blank=True)),
                ('provider_alias', models.CharField(unique=True, max_length=256)),
                ('ip_address', models.GenericIPAddressField(null=True, unpack_ipv4=True)),
                ('shell', models.BooleanField(default=False)),
                ('vnc', models.BooleanField(default=False)),
                ('password', models.CharField(max_length=64, null=True, blank=True)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField(null=True)),
            ],
            options={
                'db_table': 'instance',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InstanceMembership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('instance', models.ForeignKey(to='core.Instance')),
                ('owner', models.ForeignKey(to='core.Group')),
            ],
            options={
                'db_table': 'instance_membership',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InstanceSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.CharField(max_length=256)),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_date', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'instance_source',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InstanceStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
            ],
            options={
                'db_table': 'instance_status',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InstanceStatusHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateTimeField(default=datetime.datetime(2015, 1, 28, 20, 28, 52, 507318, tzinfo=utc))),
                ('end_date', models.DateTimeField(null=True, blank=True)),
                ('instance', models.ForeignKey(to='core.Instance')),
            ],
            options={
                'db_table': 'instance_status_history',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Leadership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.ForeignKey(to='core.Group')),
            ],
            options={
                'db_table': 'group_leaders',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=256)),
                ('license_text', models.TextField()),
                ('allow_imaging', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'license',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LicenseType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'license_type',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MachineExport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=256)),
                ('export_name', models.CharField(max_length=256)),
                ('export_format', models.CharField(max_length=256)),
                ('export_file', models.CharField(max_length=256, null=True, blank=True)),
                ('start_date', models.DateTimeField(default=datetime.datetime(2015, 1, 28, 20, 28, 52, 528638, tzinfo=utc))),
                ('end_date', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'machine_export',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MachineRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.TextField(default=b'', blank=True)),
                ('iplant_sys_files', models.TextField(default=b'', blank=True)),
                ('installed_software', models.TextField(default=b'', blank=True)),
                ('exclude_files', models.TextField(default=b'', blank=True)),
                ('access_list', models.TextField(default=b'', blank=True)),
                ('new_machine_name', models.CharField(max_length=256)),
                ('new_machine_visibility', models.CharField(max_length=256)),
                ('new_machine_description', models.TextField(default=b'', blank=True)),
                ('new_machine_tags', models.TextField(default=b'', blank=True)),
                ('new_machine_version', models.CharField(default=b'1.0.0', max_length=128)),
                ('new_machine_forked', models.BooleanField(default=False)),
                ('new_machine_memory_min', models.IntegerField(default=0)),
                ('new_machine_storage_min', models.IntegerField(default=0)),
                ('start_date', models.DateTimeField(default=datetime.datetime(2015, 1, 28, 20, 28, 52, 526405, tzinfo=utc))),
                ('end_date', models.DateTimeField(null=True, blank=True)),
                ('instance', models.ForeignKey(to='core.Instance')),
            ],
            options={
                'db_table': 'machine_request',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MaintenanceRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField(null=True, blank=True)),
                ('title', models.CharField(max_length=256)),
                ('message', models.TextField()),
                ('disable_login', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'maintenance_record',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NodeController',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alias', models.CharField(max_length=256)),
                ('hostname', models.CharField(max_length=256)),
                ('port', models.IntegerField(default=22)),
                ('private_ssh_key', models.TextField()),
                ('start_date', models.DateTimeField(default=datetime.datetime(2015, 1, 28, 20, 28, 52, 525259, tzinfo=utc))),
                ('end_date', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'node_controller',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PlatformType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_date', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'platform_type',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(default=uuid.uuid4, unique=True, max_length=36)),
                ('name', models.CharField(max_length=256)),
                ('description', models.TextField(blank=True)),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_date', models.DateTimeField(null=True, blank=True)),
                ('applications', models.ManyToManyField(related_name='projects', null=True, to='core.Application', blank=True)),
                ('instances', models.ManyToManyField(related_name='projects', null=True, to='core.Instance', blank=True)),
                ('owner', models.ForeignKey(related_name='projects', to='core.Group')),
            ],
            options={
                'db_table': 'project',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(default=uuid.uuid4, unique=True, max_length=36)),
                ('location', models.CharField(max_length=256)),
                ('description', models.TextField(blank=True)),
                ('active', models.BooleanField(default=True)),
                ('public', models.BooleanField(default=False)),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('end_date', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'provider',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProviderCredential',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=256)),
                ('value', models.CharField(max_length=256)),
                ('provider', models.ForeignKey(to='core.Provider')),
            ],
            options={
                'db_table': 'provider_credential',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProviderMachine',
            fields=[
                ('instancesource_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.InstanceSource')),
                ('version', models.CharField(default=b'1.0.0', max_length=128)),
                ('application', models.ForeignKey(to='core.Application')),
                ('licenses', models.ManyToManyField(to='core.License', null=True, blank=True)),
            ],
            options={
                'db_table': 'provider_machine',
            },
            bases=('core.instancesource',),
        ),
        migrations.CreateModel(
            name='ProviderMachineMembership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('can_share', models.BooleanField(default=False)),
                ('group', models.ForeignKey(to='core.Group')),
                ('provider_machine', models.ForeignKey(to='core.ProviderMachine')),
            ],
            options={
                'db_table': 'provider_machine_membership',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProviderMembership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('member', models.ForeignKey(to='core.Group')),
                ('provider', models.ForeignKey(to='core.Provider')),
            ],
            options={
                'db_table': 'provider_membership',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProviderType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_date', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'provider_type',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Quota',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cpu', models.IntegerField(default=16, null=True, blank=True)),
                ('memory', models.IntegerField(default=128, null=True, blank=True)),
                ('storage', models.IntegerField(default=10, null=True, blank=True)),
                ('storage_count', models.IntegerField(default=1, null=True, blank=True)),
                ('suspended_count', models.IntegerField(default=2, null=True, blank=True)),
            ],
            options={
                'db_table': 'quota',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuotaRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(default=uuid.uuid4, max_length=36)),
                ('request', models.TextField()),
                ('description', models.CharField(default=b'', max_length=1024, blank=True)),
                ('admin_message', models.CharField(default=b'', max_length=1024, blank=True)),
                ('start_date', models.DateTimeField(default=datetime.datetime(2015, 1, 28, 20, 28, 52, 540784, tzinfo=utc))),
                ('end_date', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'quota_request',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ScriptType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'script_type',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alias', models.CharField(max_length=256)),
                ('name', models.CharField(max_length=256)),
                ('cpu', models.IntegerField()),
                ('disk', models.IntegerField()),
                ('root', models.IntegerField()),
                ('mem', models.IntegerField()),
                ('start_date', models.DateTimeField(default=datetime.datetime(2015, 1, 28, 20, 28, 52, 504115, tzinfo=utc))),
                ('end_date', models.DateTimeField(null=True, blank=True)),
                ('provider', models.ForeignKey(to='core.Provider')),
            ],
            options={
                'db_table': 'size',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StatusType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('description', models.CharField(default=b'', max_length=256, blank=True)),
                ('start_date', models.DateTimeField(default=datetime.datetime(2015, 1, 28, 20, 28, 52, 540092, tzinfo=utc))),
                ('end_date', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'status_type',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alias', models.CharField(max_length=36)),
                ('name', models.CharField(max_length=1024, blank=True)),
                ('script', models.TextField()),
                ('exit_code', models.IntegerField(null=True, blank=True)),
                ('start_date', models.DateTimeField(default=datetime.datetime(2015, 1, 28, 20, 28, 52, 538498, tzinfo=utc))),
                ('end_date', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'step',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='T',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('V', models.CharField(max_length=36)),
                ('start_date', models.DateTimeField(default=datetime.datetime(2015, 1, 28, 20, 28, 52, 534991, tzinfo=utc))),
                ('end_date', models.DateTimeField(null=True)),
            ],
            options={
                'db_table': 'transaction',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.SlugField(max_length=128)),
                ('description', models.CharField(max_length=1024)),
            ],
            options={
                'db_table': 'tag',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Trait',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'trait',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('send_emails', models.BooleanField(default=True)),
                ('quick_launch', models.BooleanField(default=True)),
                ('vnc_resolution', models.CharField(default=b'800x600', max_length=255)),
                ('default_size', models.CharField(default=b'm1.small', max_length=255)),
                ('background', models.CharField(default=b'default', max_length=255)),
                ('icon_set', models.CharField(default=b'default', max_length=255)),
            ],
            options={
                'db_table': 'user_profile',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Volume',
            fields=[
                ('instancesource_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.InstanceSource')),
                ('size', models.IntegerField()),
                ('name', models.CharField(max_length=256)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'volume',
            },
            bases=('core.instancesource',),
        ),
        migrations.CreateModel(
            name='VolumeStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
            ],
            options={
                'db_table': 'volume_status',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VolumeStatusHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('device', models.CharField(max_length=128, null=True, blank=True)),
                ('instance_alias', models.CharField(max_length=36, null=True, blank=True)),
                ('start_date', models.DateTimeField(default=datetime.datetime(2015, 1, 28, 20, 28, 52, 502465, tzinfo=utc))),
                ('end_date', models.DateTimeField(null=True, blank=True)),
                ('status', models.ForeignKey(to='core.VolumeStatus')),
                ('volume', models.ForeignKey(to='core.Volume')),
            ],
            options={
                'db_table': 'volume_status_history',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='tag',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='step',
            name='created_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='step',
            name='created_by_identity',
            field=models.ForeignKey(to='core.Identity', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='step',
            name='flow',
            field=models.ForeignKey(blank=True, to='core.Flow', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='step',
            name='instance',
            field=models.ForeignKey(blank=True, to='core.Instance', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='quotarequest',
            name='created_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='quotarequest',
            name='membership',
            field=models.ForeignKey(to='core.IdentityMembership'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='quotarequest',
            name='status',
            field=models.ForeignKey(to='core.StatusType'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='providermembership',
            unique_together=set([('provider', 'member')]),
        ),
        migrations.AlterUniqueTogether(
            name='providermachinemembership',
            unique_together=set([('provider_machine', 'group')]),
        ),
        migrations.AddField(
            model_name='provider',
            name='traits',
            field=models.ManyToManyField(to='core.Trait', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='provider',
            name='type',
            field=models.ForeignKey(to='core.ProviderType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='provider',
            name='virtualization',
            field=models.ForeignKey(to='core.PlatformType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='volumes',
            field=models.ManyToManyField(related_name='projects', null=True, to='core.Volume', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='nodecontroller',
            name='provider',
            field=models.ForeignKey(to='core.Provider'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='maintenancerecord',
            name='provider',
            field=models.ForeignKey(blank=True, to='core.Provider', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='machinerequest',
            name='new_machine',
            field=models.ForeignKey(related_name='created_machine', blank=True, to='core.ProviderMachine', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='machinerequest',
            name='new_machine_licenses',
            field=models.ManyToManyField(to='core.License', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='machinerequest',
            name='new_machine_owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='machinerequest',
            name='new_machine_provider',
            field=models.ForeignKey(to='core.Provider'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='machinerequest',
            name='parent_machine',
            field=models.ForeignKey(related_name='ancestor_machine', to='core.ProviderMachine'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='machineexport',
            name='export_owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='machineexport',
            name='instance',
            field=models.ForeignKey(to='core.Instance'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='license',
            name='created_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='license',
            name='license_type',
            field=models.ForeignKey(to='core.LicenseType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leadership',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='instancestatushistory',
            name='size',
            field=models.ForeignKey(blank=True, to='core.Size', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='instancestatushistory',
            name='status',
            field=models.ForeignKey(to='core.InstanceStatus'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='instancesource',
            name='created_by',
            field=models.ForeignKey(related_name='source_set', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='instancesource',
            name='created_by_identity',
            field=models.ForeignKey(blank=True, to='core.Identity', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='instancesource',
            name='provider',
            field=models.ForeignKey(to='core.Provider'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='instancesource',
            unique_together=set([('provider', 'identifier')]),
        ),
        migrations.AlterUniqueTogether(
            name='instancemembership',
            unique_together=set([('instance', 'owner')]),
        ),
        migrations.AddField(
            model_name='instance',
            name='created_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='instance',
            name='created_by_identity',
            field=models.ForeignKey(to='core.Identity', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='instance',
            name='source',
            field=models.ForeignKey(related_name='instances', to='core.InstanceSource'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='instance',
            name='tags',
            field=models.ManyToManyField(to='core.Tag', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='identitymembership',
            name='quota',
            field=models.ForeignKey(to='core.Quota'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='identitymembership',
            unique_together=set([('identity', 'member')]),
        ),
        migrations.AddField(
            model_name='identity',
            name='created_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='identity',
            name='provider',
            field=models.ForeignKey(to='core.Provider'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='group',
            name='identities',
            field=models.ManyToManyField(to='core.Identity', through='core.IdentityMembership', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='group',
            name='instances',
            field=models.ManyToManyField(to='core.Instance', through='core.InstanceMembership', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='group',
            name='leaders',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='core.Leadership'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='group',
            name='provider_machines',
            field=models.ManyToManyField(related_name='members', through='core.ProviderMachineMembership', to='core.ProviderMachine', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='group',
            name='providers',
            field=models.ManyToManyField(to='core.Provider', through='core.ProviderMembership', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='flow',
            name='created_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='flow',
            name='created_by_identity',
            field=models.ForeignKey(to='core.Identity', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='flow',
            name='instance',
            field=models.ForeignKey(blank=True, to='core.Instance', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='flow',
            name='type',
            field=models.ForeignKey(to='core.FlowType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='credential',
            name='identity',
            field=models.ForeignKey(to='core.Identity'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bootscript',
            name='created_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bootscript',
            name='instances',
            field=models.ManyToManyField(related_name='scripts', to='core.Instance'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bootscript',
            name='script_type',
            field=models.ForeignKey(to='core.ScriptType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='applicationscore',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='applicationmembership',
            name='group',
            field=models.ForeignKey(to='core.Group'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='applicationmembership',
            unique_together=set([('application', 'group')]),
        ),
        migrations.AddField(
            model_name='applicationbookmark',
            name='user',
            field=models.ForeignKey(related_name='bookmarks', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='application',
            name='created_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='application',
            name='created_by_identity',
            field=models.ForeignKey(to='core.Identity', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='application',
            name='tags',
            field=models.ManyToManyField(to='core.Tag', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='allocationrequest',
            name='created_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='allocationrequest',
            name='membership',
            field=models.ForeignKey(to='core.IdentityMembership'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='allocationrequest',
            name='status',
            field=models.ForeignKey(to='core.StatusType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='accountprovider',
            name='identity',
            field=models.ForeignKey(to='core.Identity'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='accountprovider',
            name='provider',
            field=models.ForeignKey(to='core.Provider'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='atmosphereuser',
            name='groups',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='atmosphereuser',
            name='selected_identity',
            field=models.ForeignKey(blank=True, to='core.Identity', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='atmosphereuser',
            name='user_permissions',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions'),
            preserve_default=True,
        ),
    ]
