from django.forms import Form, ChoiceField


class UserReviewForm(Form):
    rating = ChoiceField(
        label='Rating',
        choices=(
            (5, 'Excellent'),
            (4, 'Very Good'),
            (3, 'Good'),
            (2, 'Fair'),
            (1, 'Poor')
        )
    )
