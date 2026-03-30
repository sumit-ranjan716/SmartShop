"""
Views for user registration, login, logout, and profile management.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .forms import UserRegisterForm, UserLoginForm, UserUpdateForm, ProfileUpdateForm


def register_view(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('products:product_list')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account has been created.')
            return redirect('products:product_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


class CustomLoginView(LoginView):
    """Custom login view with Bootstrap-styled form."""
    form_class = UserLoginForm
    template_name = 'users/login.html'

    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().username}!')
        return super().form_valid(form)


def logout_view(request):
    """Logout the user and redirect to home."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('products:product_list')


@login_required
def profile_view(request):
    """Display and update user profile."""
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'users/profile.html', context)


@login_required
def become_seller_view(request):
    """Upgrade user to seller account."""
    if request.method == 'POST':
        profile = request.user.profile
        if not profile.is_seller:
            profile.is_seller = True
            profile.save()
            messages.success(request, 'Congratulations! You are now a Seller.')
        return redirect('products:seller_dashboard')
    return redirect('users:profile')
