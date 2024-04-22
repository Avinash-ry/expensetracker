import locale
from datetime import datetime

from django.conf import settings
from django.contrib.auth import logout

from django.http import Http404, HttpResponse
from pdx_auth.models import PDXUser, Transaction
from pdx_auth.utils import (
    extract_org,
    extract_state,
    send_password_reset_link,
)
from pdx_auth_gateway.utils import get_username
from django.contrib.auth.views import PasswordResetView
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_bytes
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect, get_object_or_404
from .forms import CustomLoginForm, FileUploadForm
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import PasswordResetCompleteView
from oauth2_provider.views import AuthorizationView as BaseAuthorizationView
from django.http import HttpResponseRedirect


import csv
from django.shortcuts import render, redirect
from django.views.generic import FormView
from django.http import HttpResponse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_bytes
from .forms import CSVUploadForm
from .models import PDXUser

class BulkPasswordResetView(FormView):
    template_name = 'bulk_password_reset.html'
    form_class = CSVUploadForm
    success_url = '/password-reset/done/'

    def form_valid(self, form):
        file = form.cleaned_data['file']
        csv_file = csv.reader(file.read().decode('utf-8').splitlines())

        errors = []
        for i, row in enumerate(csv_file):
            if i == 0:  # Assuming the first row contains headers
                continue
            email, org_name = row
            user = PDXUser.objects.filter(username=get_username(email=email, org_name=org_name)).first()
            if user:
                uid = urlsafe_base64_encode(smart_bytes(user.id))
                token = default_token_generator.make_token(user)
                reset_url = f"{self.request.scheme}://{self.request.get_host()}/reset/{uid}/{token}/"
                send_password_reset_link(user_obj=user, reset_url=reset_url)
            else:
                errors.append(f"User with email {email} and organization {org_name} not found.")

        if errors:
            return HttpResponse('<br>'.join(errors), status=400)

        return redirect(self.get_success_url())

class CSVDisplayView(FormView):
    template_name = 'csv_display.html'
    form_class = CSVUploadForm
    success_url = '/display-csv/'  # This URL is just a placeholder

    def form_valid(self, form):
        file = form.cleaned_data['file']
        csv_file = csv.reader(file.read().decode('utf-8').splitlines())

        rows = []
        for i, row in enumerate(csv_file):
            if i > 20:  # Skip after the first 20 rows
                break
            rows.append(row)

        context = self.get_context_data()
        context['rows'] = rows
        return render(self.request, self.template_name, context)


import csv
from django.shortcuts import render, redirect
from django.views import View
from django import forms
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# MongoDB connection setup
client = MongoClient(
    "mongodb+srv://avinashry:mbOtCV2bSnaNXhts@expense.irtu2xl.mongodb.net/?retryWrites=true&w=majority&appName=expense",
    server_api=ServerApi('1')
)
db = client['expense']  # Use your database name
collection = db['mycollection']  # Use your collection name

# View to handle file upload and save to MongoDB
class UploadProcessView(View):
    template_name = 'upload_process.html'
    form_class = FileUploadForm

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form_class()})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.reader(decoded_file)

            # Convert reader to list and take first row for header
            rows = list(reader)
            header = rows[0]
            header_value_pairs = []

            for row in rows[1:]:  # Skip header row
                # Create a dictionary for each row with header-value pairs
                row_dict = dict(zip(header, row))
                header_value_pairs.append(row_dict)

            # Save all data to MongoDB if user confirms
            if 'confirm' in request.POST:
                documents = self.prepare_documents(header_value_pairs)
                collection.insert_many(documents)
                return render(request, 'success.html')  # Redirect or show a success message

            # Show header-value pairs and ask for confirmation
            context = {
                'form': form,
                'header_value_pairs': header_value_pairs[:10],  # Display first 10 rows for confirmation
                'confirm': True  # Signal to the template to show the confirm button
            }
            return render(request, self.template_name, context)
        return render(request, self.template_name, {'form': form})

    def prepare_documents(self, header_value_pairs):
        documents = []
        for row_dict in header_value_pairs:
            print(row_dict)
            # Process and validate each row_dict as needed before saving
            # For example, parsing dates and converting numerical values
            # Insert additional validation and processing logic here
            documents.append(row_dict)
        return documents


import csv
from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_date

class Command(BaseCommand):
    help = 'Imports transactions from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The CSV file to import.')

    def handle(self, *args, **options):
        try:
            with open(options['csv_file'], newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    transaction_date = parse_date(row['Txn Date']) if 'Txn Date' in row else None
                    description = row['Description'] if 'Description' in row else ''
                    ref_number = row['Ref No./Cheque No.'] if 'Ref No./Cheque No.' in row else ''
                    debit_amount = row['Debit'] if 'Debit' in row else 0
                    credit_amount = row['Credit'] if 'Credit' in row else 0
                    # Assuming 'Account' is a column in your CSV, otherwise set to None
                    account = row['Account'] if 'Account' in row else None

                    # Create and save transaction to database
                    Transaction.objects.create(
                        transaction_date=transaction_date,
                        description=description,
                        ref_number=ref_number,
                        debit_amount=debit_amount,
                        credit_amount=credit_amount,
                        account=account
                    )
            self.stdout.write(self.style.SUCCESS('Successfully imported transactions'))
        except FileNotFoundError:
            raise CommandError('File "%s" does not exist' % options['csv_file'])
