from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from movies.models import Movie
from .models import Order, Item
from django.contrib.auth.decorators import login_required
from .utils import calculate_cart_total
from django.db.models import Sum

# Create your views here.
def add(request, id):
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    cart[id] = request.POST['quantity']
    request.session['cart'] = cart
    return redirect('cart.index')

def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')

def index(request):
    cart_total = 0
    movies_in_cart = []
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids != []):
        movies_in_cart = Movie.objects.filter(id__in = movie_ids)
        cart_total = calculate_cart_total(cart, movies_in_cart)
    template_data = {}
    template_data['title'] = 'Cart'
    template_data['movies_in_cart'] = movies_in_cart
    template_data['cart_total'] = cart_total
    return render(request, 'cart/index.html', {'template_data' : template_data})

def top_purchases(request):
    template_data = {}
    template_data['title'] = 'Top Purchases'
    top_movies = (
        Item.objects
        .values('movie__id', 'movie__name')  # group by movie
        .annotate(total_quantity=Sum('quantity'))  # sum all quantities purchased
        .order_by('-total_quantity')[:10]  # top 10
    )
    template_data['top_movies'] = top_movies
    return render(request, 'cart/top_purchases.html', {'template_data' : template_data})

@login_required
def purchase(request):
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids == []):
        return redirect('cart.index')
    movies_in_cart = Movie.objects.filter(id__in = movie_ids)
    cart_total = calculate_cart_total(cart, movies_in_cart)
    order = Order()
    order.user = request.user
    order.total = cart_total
    order.save()
    for movie in movies_in_cart:
        item = Item()
        item.movie = movie
        item.price = movie.price
        item.order = order
        item.quantity = cart[str(movie.id)]
        item.save()
    request.session['cart'] = {}
    template_data = {}
    template_data['title'] = 'Purchase confirmation'
    template_data['order_id'] = order.id
    return render(request, 'cart/purchase.html', ({'template_data' : template_data}))

@login_required
def subscription_level(request):
    # Calculate total amount spent by the logged-in user
    total_spent = (
        Order.objects.filter(user=request.user)
        .aggregate(total=Sum('total'))['total'] or 0
    )

    # Determine subscription level
    if total_spent < 15:
        level = "Basic"
    elif 15 <= total_spent <= 30:
        level = "Medium"
    else:
        level = "Premium"

    template_data = {}
    template_data['title'] = 'My Subscription'
    template_data['total_spent'] = total_spent
    template_data['level'] = level
    return render(request, "cart/subscription.html", ({'template_data' : template_data}))