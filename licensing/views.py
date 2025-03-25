from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext as _
from .models import License

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class LicenseListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = License
    template_name = 'licensing/license_list.html'
    context_object_name = 'licenses'
    ordering = ['-created_at']

class LicenseCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = License
    template_name = 'licensing/license_form.html'
    fields = ['license_key', 'company_name', 'contact_email', 'start_date', 'end_date', 'is_active']
    success_url = reverse_lazy('licensing:license_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, _('تم إنشاء الترخيص بنجاح'))
        return super().form_valid(form)

class LicenseUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = License
    template_name = 'licensing/license_form.html'
    fields = ['license_key', 'company_name', 'contact_email', 'start_date', 'end_date', 'is_active']
    success_url = reverse_lazy('licensing:license_list')

    def form_valid(self, form):
        messages.success(self.request, _('تم تحديث الترخيص بنجاح'))
        return super().form_valid(form)

class LicenseDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = License
    template_name = 'licensing/license_confirm_delete.html'
    success_url = reverse_lazy('licensing:license_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, _('تم حذف الترخيص بنجاح'))
        return super().delete(request, *args, **kwargs)

class LicenseDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = License
    template_name = 'licensing/license_detail.html'
    context_object_name = 'license'