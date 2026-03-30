"""
Views for product listing, detail, search, filtering, reviews, and wishlist.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.utils.text import slugify
from .models import Product, Category, Review, Wishlist
from .forms import ReviewForm, ProductForm

def is_seller(user):
    return hasattr(user, 'profile') and user.profile.is_seller


def home_view(request):
    """Home page with featured products, categories, and popular items."""
    featured_products = Product.objects.filter(is_active=True, featured=True)[:8]
    categories = Category.objects.all()
    # Popular products = most ordered
    popular_products = Product.objects.filter(is_active=True).annotate(
        order_count=Count('order_items')
    ).order_by('-order_count')[:8]
    # Latest products
    latest_products = Product.objects.filter(is_active=True)[:8]

    context = {
        'featured_products': featured_products,
        'categories': categories,
        'popular_products': popular_products,
        'latest_products': latest_products,
    }
    return render(request, 'home.html', context)


def product_list_view(request):
    """List products with search, category filter, and price sorting."""
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()

    # --- Search ---
    query = request.GET.get('q', '')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # --- Category filter ---
    category_slug = request.GET.get('category', '')
    active_category = None
    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=active_category)

    # --- Price range filter ---
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # --- Sorting ---
    sort_by = request.GET.get('sort', '')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'rating':
        products = products.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')

    # --- Pagination ---
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'active_category': active_category,
        'sort_by': sort_by,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'products/product_list.html', context)


def product_detail_view(request, slug):
    """Product detail page with reviews and related products."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    reviews = product.reviews.all()
    is_wishlisted = False
    user_review = None

    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(user=request.user, product=product).exists()
        user_review = Review.objects.filter(user=request.user, product=product).first()

    # Related products from same category (exclude current)
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(pk=product.pk)[:4]

    review_form = ReviewForm()

    context = {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'related_products': related_products,
        'is_wishlisted': is_wishlisted,
        'user_review': user_review,
    }
    return render(request, 'products/product_detail.html', context)


@login_required
def add_review_view(request, slug):
    """Add or update a review for a product."""
    product = get_object_or_404(Product, slug=slug)

    if request.method == 'POST':
        # Check if user already reviewed this product
        existing_review = Review.objects.filter(user=request.user, product=product).first()
        if existing_review:
            form = ReviewForm(request.POST, instance=existing_review)
        else:
            form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Your review has been submitted!')
        else:
            messages.error(request, 'Error submitting your review.')

    return redirect('products:product_detail', slug=slug)


@login_required
def toggle_wishlist_view(request, slug):
    """Toggle product in/out of wishlist."""
    product = get_object_or_404(Product, slug=slug)
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product)

    if wishlist_item.exists():
        wishlist_item.delete()
        messages.info(request, f'"{product.name}" removed from your wishlist.')
    else:
        Wishlist.objects.create(user=request.user, product=product)
        messages.success(request, f'"{product.name}" added to your wishlist!')

    return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))


@login_required
def wishlist_view(request):
    """Display user's wishlist."""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'products/wishlist.html', {'wishlist_items': wishlist_items})


# ==========================================
# SELLER VIEWS
# ==========================================

@login_required
@user_passes_test(is_seller, login_url='/users/profile/')
def seller_dashboard_view(request):
    """Dashboard showing seller's own products."""
    products = Product.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, 'products/seller_dashboard.html', {'products': products})


@login_required
@user_passes_test(is_seller, login_url='/users/profile/')
def seller_add_product_view(request):
    """View to add a new product."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            # Generate unique slug
            base_slug = slugify(product.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            product.slug = slug
            product.save()
            messages.success(request, f'Product "{product.name}" added successfully!')
            return redirect('products:seller_dashboard')
    else:
        form = ProductForm()

    return render(request, 'products/seller_product_form.html', {
        'form': form,
        'title': 'Add New Product'
    })


@login_required
@user_passes_test(is_seller, login_url='/users/profile/')
def seller_edit_product_view(request, pk):
    """View to edit an existing product."""
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('products:seller_dashboard')
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/seller_product_form.html', {
        'form': form,
        'title': 'Edit Product'
    })


@login_required
@user_passes_test(is_seller, login_url='/users/profile/')
def seller_delete_product_view(request, pk):
    """View to delete an existing product."""
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted successfully.')
    return redirect('products:seller_dashboard')
