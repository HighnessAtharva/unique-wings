from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.db.models.functions import Lower

from profiles.models import UserProfile
from .models import Product, Category, Review
from .forms import ProductForm, ReviewForm

# Create your views here.


def all_products(request):
    """ A view to display all the products, sorting and searching queries """

    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            subkey = None
            if sortkey == 'rating':
                products = products.annotate(rating_true=Count("avg_rating"))
                sortkey = "rating_true"
                subkey = "avg_rating"
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
                    if subkey:
                        subkey = f'-{subkey}'

            if subkey:
                products = products.order_by(sortkey, subkey)
            else:
                products = products.order_by(sortkey)

        if request.GET and 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(
                    request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))

            queries = Q(
                name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to display the selected products details """

    product = get_object_or_404(Product, pk=product_id)
    reviews = Review.objects.filter(product=product)
    review_form = ReviewForm()
    review_user = request.user if request.user.is_authenticated else None
    context = {
        'product': product,
        'reviews': reviews,
        "review_form": review_form,
        'review_user': review_user
    }

    return render(request, 'products/product_detail.html', context)


@login_required
def add_product(request):
    """ Add a product to the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(
                request,
                'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()

    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """ Edit a product in the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(
                request,
                'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


@login_required
def delete_product(request, product_id):
    """ Delete a product from the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products'))


@login_required
def add_review(request, product_id):
    """ Add a review to a product """
    if not request.user.is_authenticated:
        messages.error(
            request,
            'Filed to add review!')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    user = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data['comment']
            rate = form.cleaned_data['rate']
            Review.objects.create(
                user=user,
                product=get_object_or_404(Product, pk=product_id),
                rate=rate,
                comment=comment)
            messages.success(request, 'Review added successfully. \
                        Thank you for your time')
            return redirect(reverse('product_detail', args=[product_id]))
        else:
            messages.error(request, 'Oops something went wrong. \
                    Please check the form is valid and try again.')
    else:
        form = ReviewForm()

    template = 'products/add_review.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


@login_required
def edit_review(request, review_id):
    """ Edit a review to a product """

    review = get_object_or_404(Review, pk=review_id)
    review_user = request.user
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review edited successfully.')
            return redirect(
                reverse('product_detail', args=(review.product.id,)))
        else:
            messages.error(request, 'Oops something went wrong. \
                    Please check the form is valid and try again.')
    else:
        form = ReviewForm(instance=review)
        messages.info(request, f'You are editing {review.product.name}')

    template = "products/edit_review.html"
    context = {
        "form": form,
        "review": review,
        "product": review.product,
        "review_user": review_user,
    }
    return render(request, template, context)


@login_required
def delete_review(request, review_id):
    """ Delete a review for a product """

    review = get_object_or_404(Review, pk=review_id)
    review.delete()
    messages.success(request, 'Review deleted successully!')
    return redirect(reverse('product_detail', args=(review.product.id,)))
