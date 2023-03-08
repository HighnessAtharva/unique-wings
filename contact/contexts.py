from .forms import NewsletterForm


def subscription_form(request):
    """Make Newsletter Subscription Form available throughout all the pages"""
    newsletter_form = NewsletterForm()
    return {
        'newsletter_form': newsletter_form,
    }
