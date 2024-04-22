from django.conf import settings
from django.contrib.auth import logout

from django.http import Http404, HttpResponse
from pdx_auth.models import PDXUser
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
from .forms import CustomLoginForm
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import PasswordResetCompleteView
from oauth2_provider.views import AuthorizationView as BaseAuthorizationView
from django.http import HttpResponseRedirect


class CustomLoginView(View):
    form_class = CustomLoginForm
    template_name = "registration/login.html"

    def get(self, request):
        next_url = request.GET.get("next")
        state = extract_state(url=next_url)
        org_name = extract_org(state=state)
        if not org_name:
            return HttpResponse("Invalid request!")
        initial_data = {"next": next_url, "state": state}
        request.session["login_url"] = request.get_full_path()
        form = self.form_class(initial=initial_data)
        return render(request, self.template_name, {"form": form, "state": state})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            state = form.cleaned_data["state"]
            org_name = extract_org(state=state)
            next_url = form.cleaned_data["next"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            username = get_username(email=email, org_name=org_name)
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(next_url)
            else:
                form.add_error(None, "Invalid login credentials")
        return render(request, self.template_name, {"form": form})


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["login_url"] = self.request.session.get("login_url")
        return context


class CustomPasswordResetView(PasswordResetView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["login_url"] = (
            self.request.session.get("login_url")
            if "login_url" in self.request.session.keys()
            else settings.LOGIN_URL
        )
        return context

    def form_valid(self, form):
        state = self.request.GET.get("state")
        org = extract_org(state=state)
        if not org:
            form.add_error(None, "Organization not found!")
            return self.form_invalid(form)
        email = form.cleaned_data["email"]

        try:
            user = get_object_or_404(
                PDXUser, username=get_username(email=email, org_name=org)
            )
        except Http404:
            form.add_error(None, "User not found!")
            return self.form_invalid(form)

        uid = urlsafe_base64_encode(smart_bytes(user.id))
        token = default_token_generator.make_token(user)

        reset_url = (
            f"{self.request.scheme}://{self.request.get_host()}/reset/{uid}/{token}/"
        )

        send_password_reset_link(user_obj=user, reset_url=reset_url)

        return redirect("password_reset_done")


class CustomAuthorizationView(BaseAuthorizationView):
    def form_valid(self, form):
        response = super().form_valid(form)
        state = form.cleaned_data.get("state", None)
        if state:
            redirect_uri = response.url.split("?")[0]  # Get the base URL
            redirect_uri += f"?state={state}&code={self.request.auth_code}"
            return HttpResponseRedirect(redirect_uri)
        return response


class CustomLogoutView(View):
    """ A custom get view which logs out the user and redirects to the frontend """

    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(request.GET.get("redirect_uri", "/"))