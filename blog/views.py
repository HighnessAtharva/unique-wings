from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import BlogForm, CommentForm
from .models import BlogPost, BlogComment

# Create your views here.


def blog(request):
    """ A view to display all blog posts """

    blogposts = BlogPost.objects.all().order_by("-date_posted")

    context = {
        'blogposts': blogposts,
    }
    return render(request, 'blog/blog.html', context)


def blog_detail(request, blogpost_id):
    """ A view to display blog detail page """

    blogpost = get_object_or_404(BlogPost, pk=blogpost_id)
    comments = BlogComment.objects.filter(blogpost=blogpost)

    context = {
        'blogpost': blogpost,
        'comments': comments,
    }

    return render(request, 'blog/blog_detail.html', context)


@login_required
def add_blogpost(request):
    """ A view to Add Blogpost form for admin only """

    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blogpost = form.save(commit=False)
            blogpost.author = request.user
            blogpost = form.save()
            messages.success(request, 'Successfully added blog post!')
            return redirect(reverse('blog_detail', args=[blogpost.id]))
        else:
            messages.error(
                        request,
                        'Failed to add blog post.\
                        Please ensure the form is valid.')
    else:
        form = BlogForm()
    template = 'blog/add_blogpost.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_blogpost(request, blogpost_id):
    """ A view to Edit Blogpost form for admin only """

    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    blogpost = get_object_or_404(BlogPost, pk=blogpost_id)
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blogpost)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated blog post!')
            return redirect(reverse('blog_detail', args=[blogpost.id]))
        else:
            messages.error(
                    request,
                    'Failed to update the blog post.\
                    Please ensure the form is valid.')
    else:
        form = BlogForm(instance=blogpost)
        messages.info(request, f'You are editing {blogpost.title}')

    template = 'blog/edit_blogpost.html'
    context = {
        'form': form,
        'blogpost': blogpost,
    }

    return render(request, template, context)


@login_required
def delete_blogpost(request, blogpost_id):
    """ A view to Delete Blogpost form for admin only """

    blogpost = get_object_or_404(BlogPost, pk=blogpost_id)

    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))
    else:
        messages.error(request, 'You cannot do that !')
        return redirect(reverse('blog'))


def blog_comment(request, blogpost_id):
    """ A view to Add BlogComment form for registered user only only """

    blogpost = get_object_or_404(BlogPost, pk=blogpost_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.comment_user = request.user
            comment.blogpost = blogpost
            comment.save()
            messages.success(request, 'Thank you for your comment !')
            return redirect(reverse('blog_detail', args=[blogpost.id]))
        else:
            messages.error(request,
                           'Oops something went wrong. \
                            Please try again.')
    else:
        form = CommentForm(instance=blogpost)
    template = 'blog/add_comment.html'
    context = {
        'form': form,
        'blogpost': blogpost,
    }

    return render(request, template, context)
