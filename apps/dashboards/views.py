from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboards/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

@login_required
def analytics(request):
    return render(request, 'dashboards/analytics.html')

@login_required
def crm(request):
    return render(request, 'dashboards/crm.html')

@login_required
def ecommerce(request):
    return render(request, 'dashboards/ecommerce.html')
