from django.core.cache import cache
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView, TemplateView,
)
from django.urls import reverse_lazy, reverse
from .models import Table, Table_reservation, Feedback
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import TemplateView
from .models import Feedback


class HomeView(TemplateView):
    template_name = "restaurant/home.html"

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        message = request.POST.get('message')
        if email and message:
            Feedback.objects.create(email=email, message=message)
            messages.success(request, "Ваше сообщение успешно отправлено! Спасибо за обратную связь.")
            return redirect('restaurant:home')
        else:
            messages.error(request, "Пожалуйста, заполните все поля.")
            return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class BookingView(TemplateView):
    template_name = "restaurant/booking.html"


class AboutView(TemplateView):
    template_name = "restaurant/about.html"





# class HomeView(ListView):
#     model = Products
#     context_object_name = "products"
#     template_name = "catalog/home.html"
#
#     def get_queryset(self):
#         if self.request.user.is_authenticated and self.request.user.has_perm('catalog.can_unpublish_product'):
#             cache_key = 'home_view_all_products'
#             queryset = Products.objects.all()
#         else:
#             cache_key = 'home_view_published_only'
#             queryset = Products.objects.filter(is_published=True)
#
#         return cache.get_or_set(cache_key, queryset, 60)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['categories'] = cache.get_or_set(
#             'category_list',
#             lambda: Category.objects.exclude(id__isnull=True),
#             60
#         )
#         return context
#
#
# class ProductDetailView(DetailView):
#
#     model = Products
#     context_object_name = "product"
#     pk_url_kwarg = "pk"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["categories"] = Category.objects.all()
#         return context
#
#
# class ProductsCreateView(LoginRequiredMixin, CreateView):
#     model = Products
#     form_class = ProductsForm
#
#     def form_valid(self, form):
#         form.instance.owner = self.request.user
#         return super().form_valid(form)
#
#     def get_success_url(self):
#         return reverse("catalog:product", kwargs={"pk": self.object.pk})
#
#
# class ProductsUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
#
#     model = Products
#     form_class = ProductsForm
#     raise_exception = True
#
#     def test_func(self):
#         product = self.get_object()
#         user = self.request.user
#         return product.owner == user or user.has_perm("catalog.delete_products")
#
#     def get_success_url(self):
#         return reverse("catalog:product", kwargs={"pk": self.object.pk})
#
#     def post(self, request, *args, **kwargs):
#         self.object = self.get_object()
#
#         if "toggle_publish" in request.POST:
#             if not request.user.has_perm("catalog.can_unpublish_product"):
#                 return HttpResponseForbidden("У вас нет прав на публикацию/снятие с публикации.")
#             self.object.is_published = not self.object.is_published
#             self.object.save()
#             return redirect(self.get_success_url())
#
#         return super().post(request, *args, **kwargs)
#
#
# class ProductsDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
#
#     model = Products
#     success_url = reverse_lazy("catalog:home")
#     raise_exception = True
#
#     def test_func(self):
#         product = self.get_object()
#         user = self.request.user
#         return product.owner == user or user.has_perm("catalog.delete_products")
#
#
# class ContactsView(View):
#
#     template_name = "catalog/contacts.html"
#
#     def get(self, request):
#         return render(request, self.template_name)
#
#     def post(self, request):
#         name = request.POST.get("name")
#         email = request.POST.get("email")
#         message = request.POST.get("message")
#         return HttpResponse(f"Спасибо, {name}! Ваше сообщение получено.")
#
#
# class ProductsByCategoryView(ListView):
#
#     model = Products
#     context_object_name = "products"
#     template_name = "catalog/products_by_category.html"
#     paginate_by = 10
#
#     def get_queryset(self):
#         category_id = self.kwargs["category_id"]
#         products = get_products_by_category(category_id)
#
#         if not self.request.user.has_perm("catalog.can_unpublish_product"):
#             products = products.filter(is_published=True)
#
#         return products
#
#     def get_context_data(self, **kwargs):
#
#         context = super().get_context_data(**kwargs)
#         category_id = self.kwargs["category_id"]
#         category = get_object_or_404(Category, pk=category_id)
#         context["category"] = category
#         context["categories"] = Category.objects.all()
#         return context